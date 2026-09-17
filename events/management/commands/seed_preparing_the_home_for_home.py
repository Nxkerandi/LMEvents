from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import Event, EventQuestion, EventQuestionOption

# Shared marketing-flyer graphic, identical across both locations' registration
# pages and the Initial Page selector, confirmed byte-identical by the Figma
# pulls for all three frames.
HERO_IMAGE = Path(__file__).resolve().parent.parent.parent.parent / "figma_export" / "hero-banner-final.jpg"

# One event, two physical locations. Content is identical except where noted
# per-location below (dates, address, deadline, schedule, session options).
LOCATIONS = [
    {
        "slug": "preparing-the-home-for-home-tn",
        "location": "Harbert Hills Academy · 45 Rural Lane, Savannah, TN 38372",
        "start_date": "2026-10-14",
        "end_date": "2026-10-17",
        "registration_deadline": "2026-09-27",
        "registration_notice_highlight": "Sunday, September 27, 2026",
        "sabbath_date": "October 17",
        "schedule": [
            {"date": "Wed, Oct 14", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Thu, Oct 15", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Fri, Oct 16", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Sat, Oct 17", "detail": "Preparing The Home For Home – All-Day Program · 9:00 AM - 6:00 PM"},
        ],
        # Figma source literally says "Friday, October 1" (missing the trailing
        # "6") for this location only — confirmed against the Pasadena frame,
        # where the equivalent option is correct, that this is an isolated typo
        # here rather than a shared default. Seeded with the corrected date.
        "session_options": [
            ("Wednesday, October 14", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Thursday, October 15", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Friday, October 16", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Saturday, October 17", "All-Day Program : 9:00 AM - 6:00 PM"),
        ],
    },
    {
        "slug": "preparing-the-home-for-home-ca",
        # Figma's live text for this footer line omits the venue name (just the
        # address) even though the hero image names "Pasadena SDA Church"
        # prominently — flagged in the Figma pull as a likely content gap.
        # Added here for consistency with the Savannah page's "Venue · address"
        # pattern rather than reproducing what looks like an omission.
        "location": "Pasadena SDA Church · 1280 E. Washington Blvd, Pasadena, CA 91104",
        "start_date": "2026-10-21",
        "end_date": "2026-10-24",
        "registration_deadline": "2026-10-04",
        "registration_notice_highlight": "Sunday, October 4, 2026",
        "sabbath_date": "October 24",
        "schedule": [
            {"date": "Wed, Oct 21", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Thu, Oct 22", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Fri, Oct 23", "detail": "Preparing The Home For Home – Evening Session · 6:00 PM - 9:00 PM"},
            {"date": "Sat, Oct 24", "detail": "Preparing The Home For Home – All-Day Program · 9:00 AM - 6:00 PM"},
        ],
        "session_options": [
            ("Wednesday, October 21", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Thursday, October 22", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Friday, October 23", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Saturday, October 24", "All-Day Program : 9:00 AM - 6:00 PM"),
        ],
    },
]

COMMON = {
    "title": "Preparing The Home For Home",
    "kicker": "Living Manna Ministries",
    "mission_statement": (
        "Join us for four days of meetings designed to prepare our hearts and homes for what "
        "lies ahead. Together we'll consider what it means to build a home that honors God now, "
        "in view of the eternal home He is preparing for us."
    ),
    "registration_notice_body": "This event is free to attend.",
    "contact_email": "livingmanna@yahoo.com",
    "quote_text": (
        "The well-being of society, the success of the church, and the prosperity of the nation "
        "truly depend upon home influences."
    ),
    "quote_attribution": "ELLEN G. WHITE, THE ADVENTIST HOME, p. 15.1",
    "speakers": "Devaney & Fazlyn Haupt\nElvin & Marcia Bridges",
    "admission_text": "Free Admission",
}


class Command(BaseCommand):
    help = "Seeds both locations of 'Preparing The Home For Home' (Savannah, TN and Pasadena, CA)."

    @transaction.atomic
    def handle(self, *args, **options):
        for loc in LOCATIONS:
            Event.objects.filter(slug=loc["slug"]).delete()

            event = Event.objects.create(
                title=COMMON["title"],
                slug=loc["slug"],
                kicker=COMMON["kicker"],
                mission_statement=COMMON["mission_statement"],
                start_date=loc["start_date"],
                end_date=loc["end_date"],
                registration_deadline=loc["registration_deadline"],
                registration_notice_highlight=loc["registration_notice_highlight"],
                registration_notice_body=COMMON["registration_notice_body"],
                location=loc["location"],
                contact_email=COMMON["contact_email"],
                quote_text=COMMON["quote_text"],
                quote_attribution=COMMON["quote_attribution"],
                speakers=COMMON["speakers"],
                admission_text=COMMON["admission_text"],
                is_published=True,
            )

            if HERO_IMAGE.exists():
                with open(HERO_IMAGE, "rb") as f:
                    event.hero_background_image.save(HERO_IMAGE.name, File(f), save=True)

            sessions = EventQuestion.objects.create(
                event=event, section_title="WHICH SESSIONS WILL YOU ATTEND?",
                label="Which sessions will you attend?", short_label="Sessions",
                question_type=EventQuestion.QuestionType.MULTI_CHOICE,
                required=True, order=10, show_in_table=True,
            )
            for i, (label, secondary) in enumerate(loc["session_options"]):
                EventQuestionOption.objects.create(
                    question=sessions, label=label, value=label, secondary_label=secondary, order=i,
                )

            EventQuestion.objects.create(
                event=event, section_title="CHILDREN & YOUTH",
                label="Will children or youth be attending with you?", short_label="Bringing children",
                question_type=EventQuestion.QuestionType.BOOLEAN,
                help_text=(
                    "Cradle Roll and Youth Sabbath School classes, plus afternoon classes, are "
                    "available. Outside of class time, we respectfully ask that parents keep their "
                    "children with them at all times."
                ),
                required=True, order=20, quick_filter=True, show_in_table=True,
            )

            EventQuestion.objects.create(
                event=event, section_title="SABBATH MEAL",
                label="Will you be joining us for the Sabbath meal?", short_label="Joining meal",
                question_type=EventQuestion.QuestionType.BOOLEAN,
                help_text=f"Meals will be provided for all visitors on Sabbath, {loc['sabbath_date']}, only.",
                required=True, order=30, quick_filter=True, quick_filter_sums_attendees=True, show_in_table=True,
            )

            EventQuestion.objects.create(
                event=event, section_title="ADDITIONAL INFORMATION",
                label="What city do you currently live in?", short_label="City",
                question_type=EventQuestion.QuestionType.TEXT,
                required=False, order=40, show_in_insights=True,
            )

            self.stdout.write(self.style.SUCCESS(
                f"Seeded '{event.title}' ({event.slug}) with {event.questions.count()} questions."
            ))
