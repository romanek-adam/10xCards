"""API views for the core flashcard app.

This module defines DRF views for REST API endpoints that provide
programmatic access to flashcard data.
"""

from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from flashcards.core.models import Flashcard
from flashcards.core.pagination import FlashcardPagination
from flashcards.core.serializers import FlashcardSerializer


class FlashcardListView(generics.ListAPIView):
    """API endpoint for retrieving paginated list of user's flashcards.

    **Authentication:** Required - users can only access their own flashcards.

    **Permissions:** IsAuthenticated - enforces user login.

    **Filtering:** Automatic filtering by authenticated user via get_queryset().

    **Sorting:** Supports ordering by created_at and updated_at fields.
    Default sort is -created_at (newest first).

    **Pagination:** Uses FlashcardPagination (25-50 items per page, default 25).

    **Query Parameters:**
    - page (int): Page number for pagination, default: 1
    - page_size (int): Items per page, default: 25, range: 25-50
    - sort (str): Field to sort by, default: "-created_at",
                  allowed: "created_at", "-created_at", "updated_at", "-updated_at"

    **Example Request:**
    GET /api/flashcards?page=2&page_size=25&sort=-created_at

    **Example Response (200 OK):**
    {
      "count": 150,
      "next": "http://localhost:8000/api/flashcards?page=3",
      "previous": "http://localhost:8000/api/flashcards?page=1",
      "results": [
        {
          "id": 456,
          "front": "What is the capital of France?",
          "back": "Paris",
          "creation_method": "ai_full",
          "created_at": "2025-01-18T14:22:00Z",
          "updated_at": "2025-01-18T14:22:00Z"
        },
        ...
      ]
    }
    """

    serializer_class = FlashcardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FlashcardPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]  # Default ordering: newest first

    def get_queryset(self):
        """Return flashcards for the authenticated user only.

        Implements row-level security by filtering queryset to only include
        flashcards owned by the requesting user. This prevents users from
        accessing other users' flashcards.

        Uses the custom FlashcardManager.for_user() method which applies
        efficient database-level filtering.
        """
        return Flashcard.objects.for_user(self.request.user)
