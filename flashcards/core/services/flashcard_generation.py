"""Flashcard generation service for AI-powered flashcard creation.

This service handles the business logic for generating flashcards from user input text
using Google's Gemini API via the GeminiLLMService.
"""

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from pydantic import BaseModel
from pydantic import Field

from flashcards.core.models import AIGenerationSession
from flashcards.core.services.llm_service import GeminiLLMService

if TYPE_CHECKING:
    from flashcards.users.models import User
else:
    User = get_user_model()

logger = logging.getLogger(__name__)

# Validation constants for flashcard fields
MAX_FRONT_LENGTH = 200
MAX_BACK_LENGTH = 500

# System instruction for LLM flashcard generation
FLASHCARD_GENERATION_SYSTEM_INSTRUCTION = """You are an expert educational content creator specializing in creating effective flashcards for learning.

Your task is to analyze the provided text and generate 5-10 high-quality flashcards that help students learn the key concepts.

Guidelines:
- Create clear, concise questions that test understanding of important concepts
- Provide complete, accurate answers with sufficient context
- Focus on fundamental concepts, definitions, facts, and relationships
- Avoid overly complex or ambiguous questions
- Each flashcard should be self-contained and understandable
- Use simple, direct language appropriate for the subject matter
- Ensure questions have definitive, factual answers"""


class GenerateFlashcardsError(Exception):
    pass


class FlashcardSchema(BaseModel):
    """Schema for a single flashcard returned by the LLM."""

    front: str = Field(
        description="The question or prompt on the front of the flashcard",
        max_length=MAX_FRONT_LENGTH,
    )
    back: str = Field(
        description="The answer or explanation on the back of the flashcard",
        max_length=MAX_BACK_LENGTH,
    )


class FlashcardGenerationResponse(BaseModel):
    """Schema for the complete flashcard generation response from LLM."""

    flashcards: list[FlashcardSchema] = Field(
        description="List of generated flashcards (5-10 cards)",
        min_length=5,
        max_length=10,
    )


@dataclass
class GenerateFlashcardsCommand:
    """Command object for flashcard generation request.

    Attributes:
        user: The authenticated user making the request
        input_text: The text from which to generate flashcards
        model_name: The AI model to use for generation (default: "gemini-2.0-flash-001")
    """

    user: User
    input_text: str
    model_name: str = "gemini-2.0-flash-001"


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

    def __init__(self, llm_service: GeminiLLMService | None = None) -> None:
        """Initialize the flashcard generation service.

        Args:
            llm_service: Optional GeminiLLMService instance. If None, creates a new
                instance with default settings.
        """
        self.logger = logger
        self._llm_service = llm_service

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

            # Generate flashcards using Gemini LLM
            flashcards = self._generate_flashcards_with_llm(
                command.input_text,
                command.model_name,
            )

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

    def _generate_flashcards_with_llm(
        self,
        input_text: str,
        model_name: str,
    ) -> list[dict[str, str]]:
        """Generate flashcards using Gemini LLM API.

        Args:
            input_text: The text from which to generate flashcards
            model_name: The Gemini model to use for generation

        Returns:
            List of flashcard dictionaries with 'front' and 'back' keys

        Raises:
            GenerateFlashcardsError: If LLM generation fails
        """
        # Initialize LLM service if not provided in constructor
        if self._llm_service is None:
            self._llm_service = GeminiLLMService(
                model=model_name,
                system_instruction=FLASHCARD_GENERATION_SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=2048,
            )

        # Create prompt for flashcard generation
        prompt = f"""Generate educational flashcards from the following text:

{input_text}

Create 5-10 flashcards that cover the most important concepts, facts, and ideas from this text."""

        try:
            # Call LLM with structured output
            response = self._llm_service.generate_structured(
                prompt=prompt,
                response_schema=FlashcardGenerationResponse,
            )

            # Convert Pydantic models to dictionaries
            flashcards = [
                {"front": card.front, "back": card.back} for card in response.flashcards
            ]

            self.logger.info(
                "LLM generated %d flashcards from input_text_length=%d",
                len(flashcards),
                len(input_text),
            )
        except Exception as e:
            self.logger.exception("LLM flashcard generation failed")
            msg = f"Failed to generate flashcards with LLM: {e}"
            raise GenerateFlashcardsError(msg) from e
        else:
            return flashcards

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
