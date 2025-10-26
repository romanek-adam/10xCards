"""Django management command to generate fake flashcards for testing/development."""

import random
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from faker import Faker

from flashcards.core.models import AIGenerationSession
from flashcards.core.models import Flashcard
from flashcards.core.services.flashcard_generation import FlashcardGenerationService
from flashcards.core.services.flashcard_generation import GenerateFlashcardsCommand

if TYPE_CHECKING:
    from flashcards.users.models import User
else:
    User = get_user_model()


class Command(BaseCommand):
    """Generate fake flashcards for development and testing purposes."""

    help = "Generate a specified number of fake flashcards for a user"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "count",
            type=int,
            help="Number of flashcards to generate",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Email of the user to create flashcards for (default: first user)",
        )
        parser.add_argument(
            "--creation-method",
            type=str,
            choices=["manual", "ai_full", "ai_edited", "mixed"],
            default="mixed",
            help="Creation method for flashcards (default: mixed)",
        )
        parser.add_argument(
            "--input-text",
            type=str,
            help="Input text for AI generation (required when using --creation-method=ai_full)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        count = options["count"]
        user_email = options.get("user")
        creation_method = options["creation_method"]
        input_text = options.get("input_text")

        if count <= 0:
            raise CommandError("Count must be a positive integer")

        # Validate input_text requirement for ai_full
        if creation_method == "ai_full" and not input_text:
            raise CommandError(
                "--input-text is required when using --creation-method=ai_full",
            )

        # Get or verify user
        user: User
        if user_email:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                raise CommandError(
                    f"User with email '{user_email}' does not exist",
                ) from None
        else:
            first_user = User.objects.first()
            if not first_user:
                raise CommandError(
                    "No users found in database. Create a user first or specify --user",
                )
            user = first_user

        self.stdout.write(f"Generating {count} flashcards for user: {user.email}")

        # Handle ai_full method separately using FlashcardGenerationService
        if creation_method == "ai_full":
            self._handle_ai_full_generation(user, input_text, count)

        # Initialize Faker
        fake = Faker()

        # Define categories and question types for more realistic flashcards
        categories = self._get_flashcard_categories()

        # Generate flashcards
        flashcards_created = []
        for _ in range(count):
            category = random.choice(categories)
            front, back = self._generate_flashcard_content(fake, category)

            # Determine creation method
            if creation_method == "mixed":
                method = random.choice(
                    [Flashcard.AI_FULL, Flashcard.AI_EDITED, Flashcard.MANUAL],
                )
            else:
                method = creation_method

            flashcard = Flashcard.objects.create(
                user=user,
                front=front,
                back=back,
                creation_method=method,
            )
            flashcards_created.append(flashcard)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(flashcards_created)} flashcards for {user.email}",
            ),
        )

    def _get_flashcard_categories(self):
        """Return list of flashcard categories with question/answer patterns."""
        return [
            {
                "type": "vocabulary",
                "question_format": "What does '{word}' mean?",
                "answer_generator": lambda fake: fake.sentence(nb_words=8),
            },
            {
                "type": "definition",
                "question_format": "Define: {term}",
                "answer_generator": lambda fake: fake.sentence(nb_words=12),
            },
            {
                "type": "historical",
                "question_format": "When did {event} occur?",
                "answer_generator": lambda fake: f"In {fake.year()}, {fake.sentence(nb_words=10)}",
            },
            {
                "type": "scientific",
                "question_format": "What is {concept}?",
                "answer_generator": lambda fake: fake.sentence(nb_words=15),
            },
            {
                "type": "mathematical",
                "question_format": "How do you calculate {formula}?",
                "answer_generator": lambda fake: fake.sentence(nb_words=20),
            },
            {
                "type": "geography",
                "question_format": "What is the capital of {location}?",
                "answer_generator": lambda fake: fake.city(),
            },
            {
                "type": "language",
                "question_format": "Translate '{phrase}' to English",
                "answer_generator": lambda fake: fake.sentence(nb_words=6),
            },
        ]

    def _generate_flashcard_content(self, fake, category):
        """Generate front and back content for a flashcard based on category."""
        question_format = category["question_format"]
        answer_generator = category["answer_generator"]

        # Generate placeholder values for question format
        if "{word}" in question_format:
            word = fake.word()
            front = question_format.format(word=word)
        elif "{term}" in question_format:
            term = fake.word().capitalize()
            front = question_format.format(term=term)
        elif "{event}" in question_format:
            event = fake.catch_phrase()
            front = question_format.format(event=event)
        elif "{concept}" in question_format:
            concept = fake.bs()
            front = question_format.format(concept=concept)
        elif "{formula}" in question_format:
            formula = fake.word()
            front = question_format.format(formula=formula)
        elif "{location}" in question_format:
            location = fake.country()
            front = question_format.format(location=location)
        elif "{phrase}" in question_format:
            phrase = fake.sentence(nb_words=4)
            front = question_format.format(phrase=phrase)
        else:
            front = question_format

        # Ensure front doesn't exceed 200 characters
        front = front[:200]

        # Generate back content
        back = answer_generator(fake)
        # Ensure back doesn't exceed 500 characters
        back = back[:500]

        return front, back

    def _handle_ai_full_generation(self, user, input_text, count):
        """Handle flashcard generation using AI service.

        Args:
            user: User instance to create flashcards for
            input_text: Text to generate flashcards from
            count: Number of flashcards requested (for info only, AI generates 5-10)

        Returns:
            None (outputs results to stdout)
        """
        self.stdout.write("Using AI to generate flashcards...")

        # Initialize the service
        service = FlashcardGenerationService()

        # Create command
        command = GenerateFlashcardsCommand(
            user=user,
            input_text=input_text,
        )

        try:
            # Generate flashcards
            result = service.generate_flashcards(command)

            if not result.success:
                raise CommandError(  # noqa: TRY301
                    f"AI generation failed: {result.error_message}",
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"AI generated {result.generated_count} flashcards "
                    f"(response time: {result.api_response_time_ms}ms)",
                ),
            )

            # Get the AIGenerationSession to link flashcards
            ai_session = AIGenerationSession.objects.get(id=result.session_id)

            # Create Flashcard records from generated flashcards
            flashcards_created = []
            for card_data in result.flashcards:
                flashcard = Flashcard.objects.create(
                    user=user,
                    front=card_data["front"],
                    back=card_data["back"],
                    creation_method=Flashcard.AI_FULL,
                    ai_session=ai_session,
                )
                flashcards_created.append(flashcard)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(flashcards_created)} flashcards for {user.email}",
                ),
            )

            # Note about count parameter
            if result.generated_count != count:
                self.stdout.write(
                    self.style.WARNING(
                        f"Note: AI generated {result.generated_count} flashcards "
                        f"(you requested {count}). AI always generates 5-10 cards.",
                    ),
                )

        except Exception as e:
            raise CommandError(f"Failed to generate flashcards: {e}") from e
