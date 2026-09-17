import csv
import re
from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
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


def _unique_slug(base_slug):
    candidate = f"{base_slug}-copy"
    n = 2
    while Event.objects.filter(slug=candidate).exists():
        candidate = f"{base_slug}-copy-{n}"
        n += 1
    return candidate


@staff_member_required
def duplicate_event_view(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    original = get_object_or_404(Event, slug=slug)

    with transaction.atomic():
        new_event = Event.objects.create(
            title=f"Copy of {original.title}",
            slug=_unique_slug(original.slug),
            kicker=original.kicker,
            mission_statement=original.mission_statement,
            start_date=original.start_date,
            end_date=original.end_date,
            registration_deadline=original.registration_deadline,
            registration_notice_body=original.registration_notice_body,
            registration_notice_highlight=original.registration_notice_highlight,
            location=original.location,
            contact_email=original.contact_email,
            # Draft by default — this is a starting point, not ready to
            # accept real registrations until staff review/adjust it
            # (dates especially — those are almost certainly wrong for a
            # new event and copied here only so the required fields aren't
            # left blank).
            is_published=False,
        )
        # Point at the same underlying file rather than duplicating it on
        # disk — perfectly safe, ImageField assignment on the draft later
        # (if staff upload a new photo) creates a new file without touching
        # the original event's copy.
        if original.hero_background_image:
            new_event.hero_background_image = original.hero_background_image.name
        if original.hero_title_image:
            new_event.hero_title_image = original.hero_title_image.name
        if original.hero_background_image or original.hero_title_image:
            new_event.save()

        # Two passes: create every question first, then wire up
        # parent_question/depends_on afterward — both are self-referencing
        # FKs to *other questions on this same event*, so they need to be
        # remapped to the new cloned rows, not left pointing at the
        # original event's questions.
        question_map = {}
        old_questions = list(original.questions.all())
        for old_q in old_questions:
            new_q = EventQuestion.objects.create(
                event=new_event,
                section_title=old_q.section_title,
                order=old_q.order,
                question_type=old_q.question_type,
                label=old_q.label,
                short_label=old_q.short_label,
                help_text=old_q.help_text,
                required=old_q.required,
                depends_on_value=old_q.depends_on_value,
                show_in_insights=old_q.show_in_insights,
                quick_filter=old_q.quick_filter,
                quick_filter_sums_attendees=old_q.quick_filter_sums_attendees,
                show_in_table=old_q.show_in_table,
                counts_as_attendees=old_q.counts_as_attendees,
            )
            question_map[old_q.id] = new_q
            for old_opt in old_q.options.all():
                EventQuestionOption.objects.create(
                    question=new_q,
                    label=old_opt.label,
                    value=old_opt.value,
                    secondary_label=old_opt.secondary_label,
                    order=old_opt.order,
                )

        for old_q in old_questions:
            if not old_q.parent_question_id and not old_q.depends_on_id:
                continue
            new_q = question_map[old_q.id]
            if old_q.parent_question_id in question_map:
                new_q.parent_question = question_map[old_q.parent_question_id]
            if old_q.depends_on_id in question_map:
                new_q.depends_on = question_map[old_q.depends_on_id]
            new_q.save()

    messages.success(
        request,
        f'Duplicated "{original.title}" as "{new_event.title}" ({new_event.questions.count()} questions copied). '
        f"It's saved as a draft — review the dates and details below before publishing.",
    )
    return redirect(f"/admin/events/event/{new_event.pk}/change/")


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


def registration_view(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)

    if request.method == "POST":
        ip_address = _client_ip(request)
        if _is_rate_limited(ip_address):
            return render(request, "events/register.html", {
                "event": event,
                "sections": _group_sections(_top_questions(event)),
                "rate_limited": True,
            }, status=429)

        # Logged for every POST regardless of outcome — a scripted loop of
        # invalid submissions should still get throttled, not just
        # successful ones.
        RegistrationAttempt.objects.create(ip_address=ip_address)

        top_questions = _top_questions(event)
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
            "missing": missing,
        }, status=400)

    if request.GET.get("submitted") == "1":
        return render(request, "events/register.html", {"event": event, "success": True})

    return render(request, "events/register.html", {
        "event": event,
        "sections": _group_sections(_top_questions(event)),
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


@staff_member_required
def dashboard_view(request, slug):
    event = get_object_or_404(Event, slug=slug)
    _, registrations_json, questions_meta = _build_dashboard_data(event)
    return render(request, "events/dashboard.html", {
        "event": event,
        "registrations_json": registrations_json,
        "questions_meta": questions_meta,
    })


@staff_member_required
def export_csv_view(request, slug):
    event = get_object_or_404(Event, slug=slug)
    top_questions, registrations_json, questions_meta = _build_dashboard_data(event)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{event.slug}-registrations.csv"'
    writer = csv.writer(response)

    headers = ["Full Name", "Email", "Phone", "Attendee Count", "Submitted"]
    for q in top_questions:
        headers.append(q.label)
    writer.writerow(headers)

    for reg in registrations_json:
        row = [reg["full_name"], reg["email"], reg["phone"], reg["attendee_count"], reg["submitted"]]
        for q in top_questions:
            value = reg["answers"].get(str(q.id))
            if q.question_type == EventQuestion.QuestionType.REPEATABLE_GROUP:
                sub_qs = list(q.sub_questions.all())
                row.append(" | ".join(
                    ", ".join(f"{sq.label}: {r.get(str(sq.id), '')}" for sq in sub_qs)
                    for r in (value or [])
                ))
            elif isinstance(value, list):
                row.append(", ".join(value))
            else:
                row.append(value or "")
        writer.writerow(row)

    return response
