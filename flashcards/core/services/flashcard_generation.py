"""Flashcard generation service for AI-powered flashcard creation.

This service handles the business logic for generating flashcards from user input text.
For the MVP, it uses a mock AI service that returns hardcoded flashcards.
In production, this will integrate with OpenRouter API.
"""

import logging
import random
import time
from dataclasses import dataclass

from django.contrib.auth import get_user_model

from flashcards.core.models import AIGenerationSession

User = get_user_model()
logger = logging.getLogger(__name__)

# Validation constants for flashcard fields
MAX_FRONT_LENGTH = 200
MAX_BACK_LENGTH = 500


class GenerateFlashcardsError(Exception):
    pass


@dataclass
class GenerateFlashcardsCommand:
    """Command object for flashcard generation request.

    Attributes:
        user: The authenticated user making the request
        input_text: The text from which to generate flashcards
        model_name: The AI model to use for generation (default: "mock_model")
    """

    user: User
    input_text: str
    model_name: str = "mock_model"


@dataclass
class GenerationResult:
    """Result object containing generation outcome and data.

    Attributes:
        session_id: ID of the AIGenerationSession record
        generated_count: Number of flashcards successfully generated
        flashcards: List of generated flashcard dictionaries with 'front'
            and 'back' keys
        success: Whether generation succeeded
        error_code: Error code if generation failed (optional)
        error_message: User-friendly error message if generation failed
            (optional)
        api_response_time_ms: API response time in milliseconds (optional)
    """

    session_id: int
    generated_count: int
    flashcards: list[dict[str, str]]
    success: bool
    error_code: str | None = None
    error_message: str | None = None
    api_response_time_ms: int | None = None


class FlashcardGenerationService:
    """Service for generating flashcards from user input text using AI.

    This service creates AIGenerationSession records for analytics tracking
    and returns generated flashcard proposals without persisting them to the
    Flashcard model (users accept/reject proposals in a separate flow).
    """

    def __init__(self) -> None:
        """Initialize the flashcard generation service."""
        self.logger = logger

    def generate_flashcards(
        self,
        command: GenerateFlashcardsCommand,
    ) -> GenerationResult:
        """Generate flashcards from input text using AI.

        This is the main entry point for flashcard generation. It:
        1. Creates an AIGenerationSession record for analytics
        2. Calls the AI service (mocked for MVP)
        3. Validates generated flashcards
        4. Updates the session with results
        5. Returns a GenerationResult object

        Args:
            command: GenerateFlashcardsCommand containing user, input_text,
                and model_name

        Returns:
            GenerationResult with success status, flashcards, and session_id
        """
        # Create AIGenerationSession record for analytics tracking
        session = AIGenerationSession.objects.create(
            user=command.user,
            input_text=command.input_text,
            model=command.model_name,
            generated_count=0,  # Will be updated after generation
        )

        try:
            # Track API response time
            start_time = time.time()

            # Generate flashcards using mock service
            # (replace with real API in production)
            flashcards = self._generate_flashcards_mock(command.input_text)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Validate generated flashcards
            valid_flashcards = self._validate_flashcards(flashcards, session.id)

            # Update session with successful generation results
            session.generated_count = len(valid_flashcards)
            session.api_response_time_ms = response_time_ms
            session.save(update_fields=["generated_count", "api_response_time_ms"])

            self.logger.info(
                "Successfully generated %d flashcards for user %s",
                len(valid_flashcards),
                command.user.id,
                extra={
                    "user_id": command.user.id,
                    "session_id": session.id,
                    "generated_count": len(valid_flashcards),
                    "response_time_ms": response_time_ms,
                },
            )

            return GenerationResult(
                session_id=session.id,
                generated_count=len(valid_flashcards),
                flashcards=valid_flashcards,
                success=True,
                api_response_time_ms=response_time_ms,
            )

        except Exception as e:
            # Log detailed error information for debugging
            error_code = "ai_generation_failed"
            error_message = "Couldn't generate flashcards right now. Please try again."

            self.logger.exception(
                "AI generation failed for user %s: %s",
                command.user.id,
                error_code,
                extra={
                    "user_id": command.user.id,
                    "input_text_preview": command.input_text[:100],
                    "session_id": session.id,
                    "error_code": error_code,
                    "exception": str(e),
                },
            )

            # Update session with error details for analytics
            session.error_code = error_code
            session.error_message = str(e)
            session.save(update_fields=["error_code", "error_message"])

            return GenerationResult(
                session_id=session.id,
                generated_count=0,
                flashcards=[],
                success=False,
                error_code=error_code,
                error_message=error_message,
            )

    def _generate_flashcards_mock(self, input_text: str) -> list[dict[str, str]]:
        """Mock AI service that returns hardcoded flashcards.

        This simulates the OpenRouter API for MVP testing. In production,
        this will be replaced with actual API calls.

        Args:
            input_text: The input text (not used in mock, but included
                for API compatibility)

        Returns:
            List of flashcard dictionaries with 'front' and 'back' keys
        """
        # S311: random is acceptable here for mock/testing purposes
        mock_error = random.choice([True, False])  # noqa: S311
        if mock_error:
            msg = "OpenRouter API error occurred (mocked)"
            raise GenerateFlashcardsError(msg)

        # Simulate API latency (500-2000ms)
        time.sleep(random.uniform(0.5, 2.0))  # noqa: S311

        # Return 5-7 hardcoded educational flashcards
        mock_flashcards = [
            {
                "front": "What is the capital of France?",
                "back": "Paris is the capital and largest city of France.",
            },
            {
                "front": "When did World War II end?",
                "back": (
                    "World War II ended in 1945 with the surrender of "
                    "Germany in May and Japan in September."
                ),
            },
            {
                "front": "What is photosynthesis?",
                "back": (
                    "Photosynthesis is the process by which plants use "
                    "sunlight, water, and carbon dioxide to produce oxygen "
                    "and energy in the form of sugar."
                ),
            },
            {
                "front": "Who wrote 'Romeo and Juliet'?",
                "back": (
                    "William Shakespeare wrote the tragic play 'Romeo and "
                    "Juliet' in the early 1590s."
                ),
            },
            {
                "front": "What is the speed of light?",
                "back": (
                    "The speed of light in a vacuum is approximately "
                    "299,792,458 meters per second (or about 186,282 "
                    "miles per second)."
                ),
            },
            {
                "front": "What is the Pythagorean theorem?",
                "back": (
                    "The Pythagorean theorem states that in a right triangle, "
                    "the square of the hypotenuse equals the sum of squares "
                    "of the other two sides: a² + b² = c²."
                ),
            },
            {
                "front": "What is DNA?",
                "back": (
                    "DNA (deoxyribonucleic acid) is a molecule that contains "
                    "the genetic instructions for the development, "
                    "functioning, growth, and reproduction of all living "
                    "organisms."
                ),
            },
        ]

        # Return random 5-7 flashcards
        num_cards = random.randint(5, 7)  # noqa: S311
        return random.sample(mock_flashcards, num_cards)

    def _validate_flashcards(
        self,
        flashcards: list[dict[str, str]],
        session_id: int,
    ) -> list[dict[str, str]]:
        """Validate generated flashcards against model constraints.

        Filters out flashcards that don't meet the required constraints:
        - front: non-empty, max MAX_FRONT_LENGTH characters
        - back: non-empty, max MAX_BACK_LENGTH characters

        Args:
            flashcards: List of flashcard dictionaries to validate
            session_id: Session ID for logging purposes

        Returns:
            List of valid flashcard dictionaries
        """
        valid_flashcards = []

        for idx, card in enumerate(flashcards):
            # Check for required keys
            if "front" not in card or "back" not in card:
                self.logger.warning(
                    "Flashcard %d missing required keys (session: %s)",
                    idx,
                    session_id,
                )
                continue

            front = card["front"].strip()
            back = card["back"].strip()

            # Validate front field
            if not front or len(front) > MAX_FRONT_LENGTH:
                self.logger.warning(
                    "Flashcard %d has invalid front field (session: %s): length=%d",
                    idx,
                    session_id,
                    len(front),
                )
                continue

            # Validate back field
            if not back or len(back) > MAX_BACK_LENGTH:
                self.logger.warning(
                    "Flashcard %d has invalid back field (session: %s): length=%d",
                    idx,
                    session_id,
                    len(back),
                )
                continue

            valid_flashcards.append({"front": front, "back": back})

        return valid_flashcards
