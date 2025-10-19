"""Django Models for 10xCards MVP.

This module defines the core data models for the flashcard application:
- Flashcard: User flashcards with AI/manual creation tracking
- AIGenerationSession: AI generation attempt tracking for analytics
"""

from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.db import models


class FlashcardManager(models.Manager):
    """Custom manager for Flashcard model that automatically filters by user.

    Provides application-level row security by ensuring users can only
    access their own flashcards.
    """

    def for_user(self, user):
        """Return flashcards for a specific user."""
        return self.filter(user=user)


class Flashcard(models.Model):
    """Central model storing user flashcards.

    Supports both AI-generated and manually-created flashcards with
    tracking for success metrics calculation.
    """

    # Creation method choices
    AI_FULL = "ai_full"
    AI_EDITED = "ai_edited"
    MANUAL = "manual"

    CREATION_METHOD_CHOICES = [
        (AI_FULL, "AI Generated (Accepted without edits)"),
        (AI_EDITED, "AI Generated (Edited before accepting)"),
        (MANUAL, "Manually Created"),
    ]

    # Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flashcards",
        help_text="Owner of this flashcard",
    )

    front = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1), MaxLengthValidator(200)],
        help_text="Question or prompt text (max 200 characters)",
    )

    back = models.CharField(
        max_length=500,
        validators=[MinLengthValidator(1), MaxLengthValidator(500)],
        help_text="Answer or explanation text (max 500 characters)",
    )

    creation_method = models.CharField(
        max_length=20,
        choices=CREATION_METHOD_CHOICES,
        help_text="How this flashcard was created",
    )

    ai_session = models.ForeignKey(
        "AIGenerationSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_flashcards",
        help_text="AI generation session that created this card (if applicable)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when flashcard was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when flashcard was last modified",
    )

    # Custom manager
    objects = FlashcardManager()

    class Meta:
        db_table = "flashcards"
        verbose_name = "Flashcard"
        verbose_name_plural = "Flashcards"
        ordering = ["-created_at"]  # Newest first
        indexes = [
            # Composite index for efficient browse/pagination queries
            models.Index(
                fields=["user", "-created_at"],
                name="flashcard_user_created_idx",
            ),
        ]

    def __str__(self):
        """Return front text truncated to 50 characters for admin display."""
        front_preview = self.front[:47] + "..." if len(self.front) > 50 else self.front  # noqa: PLR2004
        return f"{self.user.email}: {front_preview}"


class AIGenerationSession(models.Model):
    """Tracks each AI generation attempt for analytics and debugging.

    Stores input text, model and error information to support troubleshooting.
    """

    # Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
        help_text="User who initiated this generation session",
    )

    model = models.CharField(
        help_text="AI model used for generation",
    )

    input_text = models.TextField(
        validators=[MaxLengthValidator(10000)],
        help_text="Input text provided by user (max 10,000 characters)",
    )

    generated_count = models.PositiveIntegerField(
        help_text="Number of flashcards generated",
    )

    error_message = models.TextField(
        blank=True,
        help_text="Detailed error message if generation failed",
    )

    error_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Error code for categorizing failures",
    )

    api_response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="API response time in milliseconds for performance monitoring",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when session was created",
    )

    class Meta:
        db_table = "ai_generation_sessions"
        verbose_name = "AI Generation Session"
        verbose_name_plural = "AI Generation Sessions"
        ordering = ["-created_at"]  # Newest first
        indexes = [
            # Composite index for user-specific analytics queries
            models.Index(
                fields=["user", "-created_at"],
                name="ai_session_user_created_idx",
            ),
            # Single index for time-based analytics
            models.Index(fields=["created_at"], name="ai_session_created_idx"),
        ]

    def __str__(self):
        """Return session summary for admin display."""
        input_preview = (
            self.input_text[:47] + "..."
            if len(self.input_text) > 50  # noqa: PLR2004
            else self.input_text
        )
        return f"{self.user.email} - {input_preview}"
