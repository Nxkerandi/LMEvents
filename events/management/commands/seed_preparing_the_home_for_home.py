from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import Event, EventQuestion, EventQuestionOption

FIGMA_EXPORT = Path(__file__).resolve().parent.parent.parent.parent / "figma_export" / "registration"


class Command(BaseCommand):
    help = "Seeds the real 'Preparing The Home For Home' event, from the Living Manna Figma registration page pull."

    @transaction.atomic
    def handle(self, *args, **options):
        Event.objects.filter(slug="preparing-the-home-for-home").delete()

        event = Event.objects.create(
            title="Preparing The Home For Home",
            slug="preparing-the-home-for-home",
            kicker="Living Manna Ministries",
            mission_statement=(
                "Join us for four days of meetings designed to prepare our hearts and homes for "
                "what lies ahead. Together we'll consider what it means to build a home that "
                "honors God now, in view of the eternal home He is preparing for us."
            ),
            start_date="2026-10-14",
            end_date="2026-10-17",
            registration_deadline="2026-09-27",
            registration_notice_highlight="Sunday, September 27, 2026",
            registration_notice_body="This event is free to attend.",
            location="Harbert Hills Academy · 45 Rural Lane, Savannah, TN 38372",
            contact_email="livingmanna@yahoo.com",
            quote_text=(
                "The well-being of society, the success of the church, and the prosperity of the "
                "nation truly depend upon home influences."
            ),
            quote_attribution="ELLEN G. WHITE, THE ADVENTIST HOME, p. 15.1",
            speakers="Devaney & Fazlyn Haupt\nElvin & Marcia Bridges",
            admission_text="Free Admission",
            is_published=True,
        )

        hero_path = FIGMA_EXPORT / "hero-bg.png"
        if hero_path.exists():
            with open(hero_path, "rb") as f:
                event.hero_background_image.save("hero-bg.png", File(f), save=True)

        sessions = EventQuestion.objects.create(
            event=event, section_title="WHICH SESSIONS WILL YOU ATTEND?",
            label="Which sessions will you attend?", short_label="Sessions",
            question_type=EventQuestion.QuestionType.MULTI_CHOICE,
            required=True, order=10, show_in_table=True,
        )
        session_options = [
            ("Wednesday, October 14", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Thursday, October 15", "Evening Session : 6:00 PM - 9:00 PM"),
            # Figma source literally says "Friday, October 1" (missing the trailing
            # "6") — the Schedule table on the same page correctly says "Fri, Oct
            # 16" for this session. Seeded with the corrected date rather than the
            # apparent typo, since this is a live form real people submit through.
            ("Friday, October 16", "Evening Session : 6:00 PM - 9:00 PM"),
            ("Saturday, October 17", "All-Day Program : 9:00 AM - 6:00 PM"),
        ]
        for i, (label, secondary) in enumerate(session_options):
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
            help_text="Meals will be provided for all visitors on Sabbath, October 17, only.",
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
