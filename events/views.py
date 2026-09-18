import re
from collections import defaultdict
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Event,
    EventQuestion,
    EventQuestionOption,
    Registration,
    RegistrationAnswer,
    RegistrationAnswerOption,
    RegistrationAttempt,
)

# Max public registration-form submissions allowed from one IP within the
# window below, across all events. Generous enough that a real household
# fumbling the form a few times never gets blocked, tight enough to choke a
# scripted spam loop.
REGISTRATION_RATE_LIMIT = 5
REGISTRATION_RATE_WINDOW = timedelta(minutes=10)

# Read-only preview table on the registration page, kept in sync by hand with
# each location's "Which sessions will you attend?" EventQuestion options
# rather than derived from them — this app only ever serves the two locations
# of one campaign, so the duplication is cheap; revisit if that changes.
SCHEDULE_ROWS_BY_SLUG = {
    "preparing-the-home-for-home-tn": [
        {"date": "Wed, Oct 14", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Thu, Oct 15", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Fri, Oct 16", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Sat, Oct 17", "detail": "Preparing The Home For Home – All-Day Program · 9:00 AM - 6:00 PM"},
    ],
    "preparing-the-home-for-home-ca": [
        {"date": "Wed, Oct 21", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Thu, Oct 22", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Fri, Oct 23", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
        {"date": "Sat, Oct 24", "detail": "Preparing The Home For Home – All-Day Program · 9:00 AM - 6:00 PM"},
    ],
}


def _client_ip(request):
    # Railway (and most PaaS hosts) terminate TLS at a proxy and forward the
    # real client IP via X-Forwarded-For — same trust boundary already
    # relied on for SECURE_PROXY_SSL_HEADER in settings.py. Take the
    # left-most address (the original client), falling back to REMOTE_ADDR
    # for local/direct runs where no proxy is involved.
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _is_rate_limited(ip_address):
    cutoff = timezone.now() - REGISTRATION_RATE_WINDOW
    # Prune this IP's own old attempts while we're here, so a returning
    # visitor's row count doesn't grow forever — cheap, bounded per-IP.
    RegistrationAttempt.objects.filter(ip_address=ip_address, created_at__lt=cutoff).delete()
    recent_count = RegistrationAttempt.objects.filter(ip_address=ip_address, created_at__gte=cutoff).count()
    return recent_count >= REGISTRATION_RATE_LIMIT

CHOICE_TYPES = {EventQuestion.QuestionType.SINGLE_CHOICE, EventQuestion.QuestionType.MULTI_CHOICE}
REPEAT_FIELD_RE = re.compile(r"^q_(\d+)_(\d+)$")


def _format_submitted(dt):
    # Avoid strftime's %-I/%-d (platform-specific) — build "no leading zero" fields manually.
    hour12 = dt.hour % 12 or 12
    return f"{dt.strftime('%b')} {dt.day}, {dt.year} · {hour12}:{dt.strftime('%M')} {dt.strftime('%p')}"


def _format_submitted_short(dt):
    return f"{dt.strftime('%b')} {dt.day}"


def _format_date_short(d):
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def _short_session_label(full_label):
    # "Wednesday, October 14" -> "Wed, Oct 14" — abbreviated form for the
    # combined dashboard's compact table tags and session-bar rows. Derived
    # rather than stored since the seed data's option labels are already in
    # a consistent "Weekday, Month Day" shape.
    try:
        weekday, rest = full_label.split(", ", 1)
        month, day = rest.split(" ", 1)
        return f"{weekday[:3]}, {month[:3]} {day}"
    except ValueError:
        return full_label


def _top_questions(event):
    return (
        event.questions
        .filter(parent_question__isnull=True)
        .prefetch_related("options", "sub_questions__options")
    )


def _group_sections(questions):
    sections = []
    for q in questions:
        if q.section_title:
            if not sections or sections[-1]["title"] != q.section_title:
                sections.append({"title": q.section_title, "questions": []})
        elif not sections:
            sections.append({"title": "", "questions": []})
        sections[-1]["questions"].append(q)
    return sections


@staff_member_required
def events_list_view(request):
    events = list(
        Event.objects
        .annotate(registration_count=Count("registrations"))
        .order_by("-start_date")
    )
    published_count = sum(1 for e in events if e.is_published)
    return render(request, "events/events_list.html", {
        "events": events,
        "published_count": published_count,
        "draft_count": len(events) - published_count,
        "total_registrations": sum(e.registration_count for e in events),
    })


# ── Public registration form ────────────────────────────────────────────────

def _is_visible(question, post):
    if not question.depends_on_id:
        return True
    controlling_value = post.get(f"q_{question.depends_on_id}", "")
    return controlling_value == question.depends_on_value


def _save_scalar_answer(registration, question, value, repeat_index=0):
    value = (value or "").strip()
    if value:
        RegistrationAnswer.objects.create(
            registration=registration, question=question, value_text=value, repeat_index=repeat_index,
        )


def _save_choice_answers(registration, question, values, repeat_index=0):
    options_by_value = {o.value: o for o in question.options.all()}
    for v in values:
        option = options_by_value.get(v)
        if option:
            RegistrationAnswerOption.objects.create(
                registration=registration, question=question, option=option, repeat_index=repeat_index,
            )


def _process_repeatable_group(registration, question, post, missing, visible):
    sub_questions = list(question.sub_questions.all())
    sub_ids = {sq.id for sq in sub_questions}
    indices = set()
    for key in post.keys():
        m = REPEAT_FIELD_RE.match(key)
        if m and int(m.group(1)) in sub_ids:
            indices.add(int(m.group(2)))

    if visible and question.required and not indices:
        missing.append(question.label)

    for idx in sorted(indices):
        for sq in sub_questions:
            field_name = f"q_{sq.id}_{idx}"
            if sq.question_type in CHOICE_TYPES:
                values = post.getlist(field_name)
                if visible and sq.required and not values:
                    missing.append(f"{question.label} — {sq.label} (row {idx})")
                if visible:
                    _save_choice_answers(registration, sq, values, repeat_index=idx)
            else:
                value = post.get(field_name, "")
                if visible and sq.required and not value.strip():
                    missing.append(f"{question.label} — {sq.label} (row {idx})")
                if visible:
                    _save_scalar_answer(registration, sq, value, repeat_index=idx)


def _process_question(registration, question, post, missing):
    visible = _is_visible(question, post)

    if question.question_type == EventQuestion.QuestionType.REPEATABLE_GROUP:
        _process_repeatable_group(registration, question, post, missing, visible)
        return

    field_name = f"q_{question.id}"

    if question.question_type == EventQuestion.QuestionType.MULTI_CHOICE:
        values = post.getlist(field_name)
        if visible and question.required and not values:
            missing.append(question.label)
        if visible:
            _save_choice_answers(registration, question, values)
        return

    value = post.get(field_name, "")
    if visible and question.required and not value.strip():
        missing.append(question.label)
    if not visible:
        return

    if question.question_type == EventQuestion.QuestionType.SINGLE_CHOICE:
        _save_choice_answers(registration, question, [value] if value else [])
    else:
        _save_scalar_answer(registration, question, value)


def initial_page_view(request):
    # Landing page in front of both locations' registration forms — a picker,
    # not an Event itself, so it lists whatever's published rather than
    # hardcoding the two current slugs.
    events = Event.objects.filter(is_published=True).order_by("start_date")
    return render(request, "events/initial_page.html", {"events": events})


def registration_view(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)

    if request.method == "POST":
        ip_address = _client_ip(request)
        if _is_rate_limited(ip_address):
            return render(request, "events/register.html", {
                "event": event,
                "sections": _group_sections(_top_questions(event)),
                "schedule_rows": SCHEDULE_ROWS_BY_SLUG.get(event.slug, []),
                "rate_limited": True,
            }, status=429)

        # Logged for every POST regardless of outcome — a scripted loop of
        # invalid submissions should still get throttled, not just
        # successful ones.
        RegistrationAttempt.objects.create(ip_address=ip_address)

        top_questions = _top_questions(event)
        missing = []
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}".strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        attendee_count_raw = request.POST.get("attendee_count", "").strip()

        if not first_name:
            missing.append("First name")
        if not last_name:
            missing.append("Last name")
        if not email:
            missing.append("Email address")
        else:
            try:
                validate_email(email)
            except ValidationError:
                missing.append("Email address (enter a valid email, e.g. name@example.com)")
            else:
                if Registration.objects.filter(event=event, email__iexact=email).exists():
                    missing.append(
                        "Email address — this email is already registered for this event. "
                        f"To change your registration, email {event.contact_email or 'us'}."
                    )
        if not phone:
            missing.append("Phone number")

        attendee_count = None
        try:
            attendee_count = int(attendee_count_raw)
            if attendee_count < 1:
                raise ValueError
        except ValueError:
            missing.append("Number of attendees")

        registration = None
        if not missing:
            try:
                registration = Registration.objects.create(
                    event=event, full_name=full_name, email=email, phone=phone,
                    attendee_count=attendee_count,
                )
            except IntegrityError:
                # Backstop for two identical-email submissions landing at the
                # same instant — the .exists() pre-check above catches this
                # in the normal case, this only fires on a genuine race.
                missing.append(
                    "Email address — this email is already registered for this event. "
                    f"To change your registration, email {event.contact_email or 'us'}."
                )
            else:
                for question in top_questions:
                    _process_question(registration, question, request.POST, missing)
                if missing:
                    registration.delete()
                    registration = None

        if not missing:
            return redirect(f"{request.path}?submitted=1")

        return render(request, "events/register.html", {
            "event": event,
            "sections": _group_sections(top_questions),
            "schedule_rows": SCHEDULE_ROWS_BY_SLUG.get(event.slug, []),
            "missing": missing,
        }, status=400)

    if request.GET.get("submitted") == "1":
        return render(request, "events/register.html", {"event": event, "success": True})

    return render(request, "events/register.html", {
        "event": event,
        "sections": _group_sections(_top_questions(event)),
        "schedule_rows": SCHEDULE_ROWS_BY_SLUG.get(event.slug, []),
    })


def _current_answers(registration, top_questions):
    scalar_lookup, choice_lookup = _build_answer_lookups(registration.event)
    return {
        str(q.id): _question_value(registration.id, q, scalar_lookup, choice_lookup)
        for q in top_questions
    }


@staff_member_required
def edit_registration_view(request, registration_id):
    registration = get_object_or_404(Registration, pk=registration_id)
    event = registration.event
    top_questions = list(_top_questions(event))
    short = "tn" if event.slug.endswith("-tn") else "ca"
    back_url = f"/preparing-the-home-for-home/dashboard/?event={short}"

    if request.method == "POST":
        missing = []
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        attendee_count_raw = request.POST.get("attendee_count", "").strip()

        if not full_name:
            missing.append("Full name")
        if not email:
            missing.append("Email address")
        else:
            try:
                validate_email(email)
            except ValidationError:
                missing.append("Email address (enter a valid email, e.g. name@example.com)")
            else:
                # Excludes this registration's own row — unlike the public
                # form's duplicate check, editing a registration back to its
                # own unchanged email must not trip the uniqueness guard.
                if Registration.objects.filter(event=event, email__iexact=email).exclude(pk=registration.pk).exists():
                    missing.append("Email address — another registration for this event already uses this email.")
        if not phone:
            missing.append("Phone number")

        attendee_count = None
        try:
            attendee_count = int(attendee_count_raw)
            if attendee_count < 1:
                raise ValueError
        except ValueError:
            missing.append("Number of attendees")

        if not missing:
            with transaction.atomic():
                registration.full_name = full_name
                registration.email = email
                registration.phone = phone
                registration.attendee_count = attendee_count
                registration.save()

                # Clear and re-save every answer rather than diffing —
                # simplest correct way to handle every question type
                # (including repeatable-group rows) through the same
                # _process_question path the public form already uses.
                RegistrationAnswer.objects.filter(registration=registration).delete()
                RegistrationAnswerOption.objects.filter(registration=registration).delete()

                for question in top_questions:
                    _process_question(registration, question, request.POST, missing)

                if missing:
                    # Rolls back the whole save, including the top-level
                    # field changes above — an edit either fully succeeds or
                    # leaves the prior saved state untouched, never a mix.
                    transaction.set_rollback(True)

        if not missing:
            return redirect(back_url)

        return render(request, "events/edit_registration.html", {
            "event": event,
            "registration": registration,
            "back_url": back_url,
            "sections": _group_sections(top_questions),
            "answers": _current_answers(registration, top_questions),
            "missing": missing,
        }, status=400)

    return render(request, "events/edit_registration.html", {
        "event": event,
        "registration": registration,
        "back_url": back_url,
        "sections": _group_sections(top_questions),
        "answers": _current_answers(registration, top_questions),
    })


# ── Staff dashboard ──────────────────────────────────────────────────────────

def _question_meta(question):
    return {
        "id": question.id,
        "label": question.label,
        "short_label": question.display_label,
        "type": question.question_type,
        "section": question.section_title,
        "show_in_insights": question.show_in_insights,
        "quick_filter": question.quick_filter,
        "quick_filter_sums_attendees": question.quick_filter_sums_attendees,
        "show_in_table": question.show_in_table,
        "counts_as_attendees": question.counts_as_attendees,
        "options": [
            {"label": o.label, "value": o.value} for o in question.options.all()
        ],
        "sub_questions": [
            {
                "id": sq.id,
                "label": sq.label,
                "type": sq.question_type,
                "options": [{"label": o.label, "value": o.value} for o in sq.options.all()],
            }
            for sq in question.sub_questions.all()
        ],
    }


def _build_answer_lookups(event):
    answers = (
        RegistrationAnswer.objects
        .filter(registration__event=event)
        .values("registration_id", "question_id", "repeat_index", "value_text")
    )
    scalar_lookup = defaultdict(dict)
    for a in answers:
        scalar_lookup[(a["registration_id"], a["question_id"])][a["repeat_index"]] = a["value_text"]

    answer_options = (
        RegistrationAnswerOption.objects
        .filter(registration__event=event)
        .select_related("option")
        .values("registration_id", "question_id", "repeat_index", "option__label")
    )
    choice_lookup = defaultdict(lambda: defaultdict(list))
    for ao in answer_options:
        choice_lookup[(ao["registration_id"], ao["question_id"])][ao["repeat_index"]].append(ao["option__label"])

    return scalar_lookup, choice_lookup


def _question_value(reg_id, question, scalar_lookup, choice_lookup):
    if question.question_type == EventQuestion.QuestionType.REPEATABLE_GROUP:
        sub_qs = list(question.sub_questions.all())
        indices = set()
        for sq in sub_qs:
            indices.update(scalar_lookup.get((reg_id, sq.id), {}).keys())
            indices.update(choice_lookup.get((reg_id, sq.id), {}).keys())
        rows = []
        for idx in sorted(indices):
            row = {}
            for sq in sub_qs:
                if sq.question_type in CHOICE_TYPES:
                    vals = choice_lookup.get((reg_id, sq.id), {}).get(idx, [])
                    row[str(sq.id)] = ", ".join(vals)
                else:
                    row[str(sq.id)] = scalar_lookup.get((reg_id, sq.id), {}).get(idx, "")
            rows.append(row)
        return rows

    if question.question_type == EventQuestion.QuestionType.MULTI_CHOICE:
        return choice_lookup.get((reg_id, question.id), {}).get(0, [])

    if question.question_type == EventQuestion.QuestionType.SINGLE_CHOICE:
        vals = choice_lookup.get((reg_id, question.id), {}).get(0, [])
        return vals[0] if vals else ""

    return scalar_lookup.get((reg_id, question.id), {}).get(0, "")


def _build_dashboard_data(event):
    top_questions = list(_top_questions(event))
    registrations = event.registrations.all()
    scalar_lookup, choice_lookup = _build_answer_lookups(event)

    # Only repeatable groups explicitly flagged counts_as_attendees are rows
    # of actual people (e.g. "list each child") rather than something else
    # (e.g. "list each allergy") — used for the "Total children" stat only,
    # not folded into attendee_count/total attendees.
    child_group_questions = [
        q for q in top_questions
        if q.question_type == EventQuestion.QuestionType.REPEATABLE_GROUP and q.counts_as_attendees
    ]

    registrations_json = []
    for reg in registrations:
        answers = {
            str(q.id): _question_value(reg.id, q, scalar_lookup, choice_lookup)
            for q in top_questions
        }
        # attendee_count is what the registrant reported for "how many people
        # will be attending with you" — trusted as the total party size
        # (kids included), used directly for the "Total attendees" stat and
        # any quick-filter stat flagged to sum headcount (e.g. meals).
        registrations_json.append({
            "id": reg.id,
            "full_name": reg.full_name,
            "email": reg.email,
            "phone": reg.phone,
            "attendee_count": reg.attendee_count,
            "child_count": sum(len(answers[str(q.id)]) for q in child_group_questions),
            "submitted": _format_submitted(reg.submitted_at),
            "answers": answers,
        })

    questions_meta = [_question_meta(q) for q in top_questions]
    return top_questions, registrations_json, questions_meta


# Bespoke to this one campaign (two locations of "Preparing The Home For
# Home") rather than a generic multi-event view — the per-question shape
# below (Sessions/Bringing children/Joining meal/City) is specific to this
# campaign's four questions, matched by short_label since each location has
# its own EventQuestion rows (and therefore different ids) for the same
# logical question.
COMBINED_DASHBOARD_SLUGS = ["preparing-the-home-for-home-tn", "preparing-the-home-for-home-ca"]


@staff_member_required
def combined_dashboard_view(request):
    events = list(Event.objects.filter(slug__in=COMBINED_DASHBOARD_SLUGS).order_by("start_date"))

    event_meta = []
    registrations = []
    for event in events:
        short = "TN" if event.slug.endswith("-tn") else "CA"
        top_questions, regs, meta = _build_dashboard_data(event)
        meta_by_label = {m["short_label"]: m for m in meta}
        session_q = meta_by_label.get("Sessions")
        children_q = meta_by_label.get("Bringing children")
        meal_q = meta_by_label.get("Joining meal")
        city_q = meta_by_label.get("City")

        session_order = [_short_session_label(o["label"]) for o in (session_q["options"] if session_q else [])]
        event_meta.append({
            "slug": event.slug,
            "short": short,
            "name": event.location.split(" · ")[0] if event.location else event.title,
            "deadline": _format_date_short(event.registration_deadline) if event.registration_deadline else "",
            "session_order": session_order,
        })

        submitted_by_id = dict(event.registrations.values_list("id", "submitted_at"))
        for reg in regs:
            answers = reg["answers"]
            session_values = answers.get(str(session_q["id"]), []) if session_q else []
            registrations.append({
                "id": reg["id"],
                "event": event.slug,
                "event_short": short,
                "full_name": reg["full_name"],
                "email": reg["email"],
                "phone": reg["phone"],
                "city": answers.get(str(city_q["id"]), "") if city_q else "",
                "sessions": [_short_session_label(v) for v in session_values],
                "total": reg["attendee_count"],
                "children": answers.get(str(children_q["id"]), "") == "Yes" if children_q else False,
                "meal": answers.get(str(meal_q["id"]), "") == "Yes" if meal_q else False,
                "submitted": _format_submitted_short(submitted_by_id[reg["id"]]),
                "submitted_ts": submitted_by_id[reg["id"]].isoformat(),
            })

    return render(request, "events/combined_dashboard.html", {
        "event_meta_json": event_meta,
        "registrations_json": registrations,
    })


