from django.contrib import admin
from django.shortcuts import redirect

from .models import (
    Event,
    EventQuestion,
    EventQuestionOption,
    Registration,
    RegistrationAnswer,
    RegistrationAnswerOption,
    RegistrationAttempt,
    SiteSettings,
)


class EventQuestionOptionInline(admin.TabularInline):
    model = EventQuestionOption
    extra = 1


@admin.register(EventQuestion)
class EventQuestionAdmin(admin.ModelAdmin):
    list_display = [
        "label", "event", "question_type", "section_title", "order", "required", "parent_question",
        "quick_filter", "quick_filter_sums_attendees", "counts_as_attendees",
    ]
    list_filter = ["event", "question_type"]
    inlines = [EventQuestionOptionInline]


class EventQuestionInline(admin.TabularInline):
    model = EventQuestion
    fk_name = "event"
    extra = 0
    fields = ["order", "section_title", "question_type", "label", "required", "parent_question"]
    show_change_link = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "start_date", "end_date", "registration_deadline", "is_published"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventQuestionInline]


class RegistrationAnswerInline(admin.TabularInline):
    model = RegistrationAnswer
    extra = 0


class RegistrationAnswerOptionInline(admin.TabularInline):
    model = RegistrationAnswerOption
    extra = 0


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "event", "attendee_count", "submitted_at"]
    list_filter = ["event"]
    search_fields = ["full_name", "email", "phone"]
    inlines = [RegistrationAnswerInline, RegistrationAnswerOptionInline]


@admin.register(RegistrationAttempt)
class RegistrationAttemptAdmin(admin.ModelAdmin):
    # Read-only tracking for the registration-form rate limit — useful for
    # looking up or clearing an IP if a legitimate visitor gets blocked
    # (e.g. a shared office/church network hitting the cap).
    list_display = ["ip_address", "created_at"]
    list_filter = ["ip_address"]
    search_fields = ["ip_address"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # Singleton — one row, shared by every event's registration page.
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(f"/admin/events/sitesettings/{obj.pk}/change/")
