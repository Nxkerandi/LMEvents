from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    kicker = models.CharField(
        max_length=200, blank=True,
        help_text="Small label shown above the title, e.g. the organization name.",
    )
    mission_statement = models.TextField(
        blank=True, help_text="Shown under the title on the public registration page.",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField(null=True, blank=True)
    registration_notice_body = models.TextField(
        blank=True,
        help_text="Body text for the registration-deadline notice box. Falls back to a generic sentence if blank.",
    )
    registration_notice_highlight = models.CharField(
        max_length=200, blank=True,
        help_text="Optional phrase appended to the notice body in gold, e.g. \"September 30.\" — for emphasizing a deadline.",
    )
    location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    hero_background_image = models.ImageField(
        upload_to="events/hero_backgrounds/", blank=True, null=True,
        help_text="Full-bleed photo behind the hero title. Falls back to a plain navy background if blank.",
    )
    hero_title_image = models.ImageField(
        upload_to="events/hero_titles/", blank=True, null=True,
        help_text="Stylized title artwork shown in the hero, in place of the plain event title text. Optional.",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def date_range_display(self):
        # Avoid strftime's %-d/%#d (platform-specific) — build the "no leading zero" day manually.
        start, end = self.start_date, self.end_date
        if start == end:
            return f"{start.strftime('%B')} {start.day}, {start.year}"
        if start.month == end.month and start.year == end.year:
            return f"{start.strftime('%B')} {start.day}–{end.day}, {end.year}"
        return f"{start.strftime('%B')} {start.day}, {start.year} – {end.strftime('%B')} {end.day}, {end.year}"

    @property
    def hero_date_display(self):
        # Compact all-caps form for the hero badge, e.g. "OCT 7 - 10, 2026"
        start, end = self.start_date, self.end_date
        month = start.strftime('%b').upper()
        if start == end:
            return f"{month} {start.day}, {start.year}"
        if start.month == end.month and start.year == end.year:
            return f"{month} {start.day} - {end.day}, {end.year}"
        end_month = end.strftime('%b').upper()
        return f"{month} {start.day}, {start.year} - {end_month} {end.day}, {end.year}"


class EventQuestion(models.Model):
    class QuestionType(models.TextChoices):
        TEXT = "text", "Short text"
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        NUMBER = "number", "Number"
        TEXTAREA = "textarea", "Long text"
        BOOLEAN = "boolean", "Yes / No"
        SINGLE_CHOICE = "single_choice", "Single choice"
        MULTI_CHOICE = "multi_choice", "Multiple choice"
        REPEATABLE_GROUP = "repeatable_group", "Repeatable group"

    event = models.ForeignKey(Event, related_name="questions", on_delete=models.CASCADE)
    parent_question = models.ForeignKey(
        "self", related_name="sub_questions", null=True, blank=True, on_delete=models.CASCADE,
        help_text="Set only for a sub-question that repeats inside a Repeatable group question.",
    )
    section_title = models.CharField(
        max_length=200, blank=True,
        help_text="Groups this question under a section heading. Leave blank to continue the previous section.",
    )
    order = models.PositiveIntegerField(default=0)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    label = models.CharField(max_length=300)
    short_label = models.CharField(
        max_length=60, blank=True,
        help_text="Compact label for dashboard stat cards, filter pills, and table columns (falls back to a truncated label).",
    )
    help_text = models.CharField(max_length=300, blank=True)
    required = models.BooleanField(default=False)
    depends_on = models.ForeignKey(
        "self", related_name="dependents", null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Only show this question if depends_on's answer equals depends_on_value.",
    )
    depends_on_value = models.CharField(max_length=200, blank=True)
    show_in_insights = models.BooleanField(
        default=False, help_text="Show an answer-distribution bar chart for this question on the dashboard.",
    )
    quick_filter = models.BooleanField(
        default=False, help_text="Add a quick-filter pill for this question on the dashboard (best for Yes/No questions).",
    )
    quick_filter_sums_attendees = models.BooleanField(
        default=False,
        help_text="Only used when quick_filter is on. Show total headcount (this registration's attendee "
                   "count plus anyone listed in a repeatable group, e.g. children) across matching "
                   "registrations, instead of just counting matching registrations. Turn on for "
                   "headcount-planning questions like meals; leave off for things like \"first time visitor?\" "
                   "where a household count is what you actually want.",
    )
    show_in_table = models.BooleanField(
        default=False, help_text="Give this question its own column in the dashboard table (kept short — best for Yes/No or repeatable-group counts).",
    )
    counts_as_attendees = models.BooleanField(
        default=False,
        help_text="Repeatable-group questions only. Turn on when each row in this group is a person who should "
                   "count toward headcount stats (e.g. \"list each child\"). Leave off for repeatable groups "
                   "that aren't people (e.g. \"list each allergy\") — otherwise their row count would get added "
                   "to attendee totals.",
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.event}: {self.label}"

    @property
    def is_choice_type(self):
        return self.question_type in (self.QuestionType.SINGLE_CHOICE, self.QuestionType.MULTI_CHOICE)

    @property
    def display_label(self):
        if self.short_label:
            return self.short_label
        if len(self.label) <= 40:
            return self.label
        return self.label[:37].rstrip() + "…"


class EventQuestionOption(models.Model):
    question = models.ForeignKey(EventQuestion, related_name="options", on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    secondary_label = models.CharField(
        max_length=100, blank=True,
        help_text="Optional right-aligned tag, e.g. a time shown next to a schedule option.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.question}: {self.label}"


class Registration(models.Model):
    event = models.ForeignKey(Event, related_name="registrations", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    attendee_count = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            # Case-insensitive on purpose (Lower(email), not email) — "Jane@x.com"
            # and "jane@x.com" are the same person for this purpose. This is the
            # backstop against a race between two identical-email submissions
            # landing at the same instant; the view does its own pre-check
            # first for the friendly error message in the normal case.
            models.UniqueConstraint(models.functions.Lower("email"), "event", name="unique_registration_per_event_email"),
        ]

    def __str__(self):
        return f"{self.full_name} — {self.event}"


class RegistrationAnswer(models.Model):
    registration = models.ForeignKey(Registration, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(EventQuestion, related_name="answers", on_delete=models.CASCADE)
    repeat_index = models.PositiveIntegerField(
        default=0, help_text="Which repetition this belongs to, for sub-questions of a repeatable group.",
    )
    value_text = models.TextField(blank=True)

    class Meta:
        ordering = ["repeat_index", "id"]

    def __str__(self):
        return f"{self.registration}: {self.question.label} = {self.value_text}"


class RegistrationAnswerOption(models.Model):
    registration = models.ForeignKey(Registration, related_name="answer_options", on_delete=models.CASCADE)
    question = models.ForeignKey(EventQuestion, related_name="answer_options", on_delete=models.CASCADE)
    option = models.ForeignKey(EventQuestionOption, related_name="selections", on_delete=models.CASCADE)
    repeat_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["repeat_index", "id"]

    def __str__(self):
        return f"{self.registration}: {self.option.label}"


class RegistrationAttempt(models.Model):
    """One row per POST to the public registration form, successful or not.

    Used only to rate-limit that endpoint by IP — not tied to a specific
    event, since a bot can just target whichever event slug it likes. A
    plain DB table (rather than Django's cache framework) so the limit is
    accurate across all gunicorn workers without needing a shared cache
    backend.
    """
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["ip_address", "created_at"])]


class SiteSettings(models.Model):
    """Singleton (always pk=1) for org-wide branding shared across every event,
    as opposed to Event fields, which are per-event content."""
    motto = models.CharField(
        max_length=200, blank=True,
        help_text="Organization tagline shown under the mission statement on every event's registration page, "
                   'e.g. "ARISE. BUILD. COMPEL". Leave blank to hide it.',
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
