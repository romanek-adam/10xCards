"""Serializers for flashcard generation API endpoint.

This module defines request and response serializers for the POST /api/generations
endpoint, including input validation and error response formatting.
"""

from rest_framework import serializers


class GenerationRequestSerializer(serializers.Serializer):
    """Serializer for flashcard generation request.

    Validates the input_text field according to business requirements:
    - Required field
    - Trims leading/trailing whitespace
    - Must be non-empty after trimming
    - Maximum 10,000 characters
    """

    input_text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=10000,
        min_length=1,
        help_text="The text from which to generate flashcards (max 10,000 characters)",
        error_messages={
            "required": "This field is required.",
            "blank": "This field may not be blank.",
            "max_length": "Ensure this field has no more than 10000 characters.",
            "min_length": "This field may not be blank.",
        },
    )


class GeneratedFlashcardSerializer(serializers.Serializer):
    """Serializer for a single generated flashcard proposal.

    Represents an AI-generated flashcard that hasn't been persisted yet.
    These are proposals that users can accept/reject.
    """

    front = serializers.CharField(
        max_length=200,
        help_text="Question or prompt text (max 200 characters)",
    )
    back = serializers.CharField(
        max_length=500,
        help_text="Answer or explanation text (max 500 characters)",
    )


class GenerationResponseSerializer(serializers.Serializer):
    """Serializer for successful flashcard generation response.

    Returns the generated flashcard proposals along with session metadata
    for analytics tracking.
    """

    session_id = serializers.IntegerField(
        help_text="ID of the AIGenerationSession record for analytics",
    )
    generated_count = serializers.IntegerField(
        help_text="Number of flashcards successfully generated",
    )
    generated_flashcards = GeneratedFlashcardSerializer(
        many=True,
        help_text="List of generated flashcard proposals",
    )
