"""Django Models for 10xCards MVP.

This module defines the core data models for the flashcard application:
- Flashcard: User flashcards with AI/manual creation tracking
- AIGenerationSession: AI generation attempt tracking for analytics
- GeneratedFlashcard: All AI-generated cards (accepted/rejected) for metrics
"""

from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone


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
        validators=[MaxLengthValidator(200)],
        help_text="Question or prompt text (max 200 characters)",
    )

    back = models.CharField(
        max_length=500,
        validators=[MaxLengthValidator(500)],
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
        front_preview = self.front[:47] + "..." if len(self.front) > 50 else self.front
        return f"{self.user.email}: {front_preview}"

    def save(self, *args, **kwargs):
        """Override save to ensure both front and back are non-empty."""
        if not self.front or not self.front.strip():
            raise ValueError("Front text is required")
        if not self.back or not self.back.strip():
            raise ValueError("Back text is required")
        super().save(*args, **kwargs)


class AIGenerationSession(models.Model):
    """Tracks each AI generation attempt for analytics and debugging.

    Stores input text, status, error information, and performance metrics
    to support success metrics calculation and troubleshooting.
    """

    # Status choices
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    # Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
        help_text="User who initiated this generation session",
    )

    input_text = models.TextField(
        validators=[MaxLengthValidator(10000)],
        help_text="Input text provided by user (max 10,000 characters)",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of this generation attempt",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed error message if generation failed",
    )

    error_code = models.CharField(
        max_length=50,
        null=True,
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
            # Single index for filtering by status
            models.Index(fields=["status"], name="ai_session_status_idx"),
            # Single index for time-based analytics
            models.Index(fields=["created_at"], name="ai_session_created_idx"),
        ]

    def __str__(self):
        """Return session summary for admin display."""
        input_preview = (
            self.input_text[:47] + "..."
            if len(self.input_text) > 50
            else self.input_text
        )
        return f"{self.user.email} - {self.status} - {input_preview}"

    @property
    def acceptance_rate(self):
        """Calculate acceptance rate for this session.

        Returns:
            float: Percentage of generated flashcards that were accepted (0-100)
            None: If no flashcards were generated
        """
        total = self.generated_flashcards.count()
        if total == 0:
            return None
        accepted = self.generated_flashcards.filter(was_accepted=True).count()
        return (accepted / total) * 100


class GeneratedFlashcard(models.Model):
    """Stores ALL flashcards generated by AI for metrics calculation.

    Preserves original AI-generated content and tracks user modifications
    to distinguish between AI_FULL and AI_EDITED creation methods.
    Records accept/reject decisions for calculating AI acceptance rate.
    """

    # Fields
    session = models.ForeignKey(
        AIGenerationSession,
        on_delete=models.CASCADE,
        related_name="generated_flashcards",
        help_text="AI generation session that produced this flashcard",
    )

    original_front = models.CharField(
        max_length=200,
        help_text="Original front text generated by AI",
    )

    original_back = models.CharField(
        max_length=500,
        help_text="Original back text generated by AI",
    )

    edited_front = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="User-edited front text (if modified before accepting)",
    )

    edited_back = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="User-edited back text (if modified before accepting)",
    )

    was_accepted = models.BooleanField(
        default=False,
        help_text="Whether user accepted this flashcard",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when user accepted/rejected this card",
    )

    class Meta:
        db_table = "generated_flashcards"
        verbose_name = "Generated Flashcard"
        verbose_name_plural = "Generated Flashcards"
        ordering = ["id"]  # Order by creation sequence

    def __str__(self):
        """Return generated card summary for admin display."""
        status = "Accepted" if self.was_accepted else "Rejected"
        front_preview = (
            self.original_front[:47] + "..."
            if len(self.original_front) > 50
            else self.original_front
        )
        return f"{status}: {front_preview}"

    @property
    def was_edited(self):
        """Check if flashcard was edited before accepting.

        Returns:
            bool: True if either front or back was edited
        """
        return bool(self.edited_front or self.edited_back)

    @property
    def final_front(self):
        """Get final front text (edited version if available, otherwise original).

        Returns:
            str: Final front text
        """
        return self.edited_front if self.edited_front else self.original_front

    @property
    def final_back(self):
        """Get final back text (edited version if available, otherwise original).

        Returns:
            str: Final back text
        """
        return self.edited_back if self.edited_back else self.original_back

    def accept(self, front_text=None, back_text=None):
        """Mark this generated flashcard as accepted.

        Args:
            front_text (str, optional): Edited front text if user modified it
            back_text (str, optional): Edited back text if user modified it
        """
        self.was_accepted = True
        self.reviewed_at = timezone.now()

        # Store edited versions if provided and different from original
        if front_text and front_text != self.original_front:
            self.edited_front = front_text
        if back_text and back_text != self.original_back:
            self.edited_back = back_text

        self.save()

    def reject(self):
        """Mark this generated flashcard as rejected."""
        self.was_accepted = False
        self.reviewed_at = timezone.now()
        self.save()
