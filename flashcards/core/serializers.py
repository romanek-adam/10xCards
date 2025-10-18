"""Serializers for the core flashcard app.

This module defines DRF serializers for API endpoints that expose
flashcard data to authenticated users.
"""

from rest_framework import serializers

from flashcards.core.models import Flashcard


class FlashcardSerializer(serializers.ModelSerializer):
    """Serializer for Flashcard model exposing read-only fields for listing.

    Used by the GET /api/flashcards endpoint to return paginated flashcard data.
    All fields are read-only as this serializer is only used for listing flashcards.
    """

    class Meta:
        model = Flashcard
        fields = ["id", "front", "back", "creation_method", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
