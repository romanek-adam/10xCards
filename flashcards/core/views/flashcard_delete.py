"""Django view for handling flashcard deletion with HTMX support."""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

from flashcards.core.models import Flashcard

logger = logging.getLogger(__name__)


class FlashcardDeleteView(LoginRequiredMixin, View):
    """Handle flashcard deletion with ownership validation.

    Follows HTMX delete-row pattern by returning empty 200 response,
    allowing HTMX to remove the element from the DOM with swap animation.

    Supports:
    - User ownership validation for security
    - HTMX swap with fade animation via empty response
    """

    def delete(self, request, pk):
        """Delete flashcard and return empty response for HTMX.

        Args:
            request: HttpRequest with authenticated user
            pk: Primary key of flashcard to delete

        Returns:
            HttpResponse: Empty 200 response signaling HTMX to remove element
        """
        flashcard = get_object_or_404(
            Flashcard,
            pk=pk,
            user=request.user,
        )

        try:
            flashcard.delete()
        except Exception:
            logger.exception("Failed to delete flashcard %s", pk)
            return HttpResponse(status=500)

        return HttpResponse(status=200)
