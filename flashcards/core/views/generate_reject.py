"""Django view for rejecting AI-generated flashcards."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views import View

from flashcards.core.models import AIGenerationSession
from flashcards.core.models import Flashcard


class RejectFlashcardView(LoginRequiredMixin, View):
    """View for rejecting an AI-generated flashcard.

    Handles POST requests to reject a flashcard.
    Updates the flashcard's ai_review_state to REJECTED.

    Security:
    - Verifies session ownership (session.user == request.user)
    - Validates flashcard belongs to the session
    - Returns 403 if unauthorized access attempt
    """

    def post(self, request, session_id):
        """Reject a flashcard and update its state.

        Expected POST data:
        - flashcard_id: ID of the flashcard to reject

        Returns:
            HttpResponse: Empty 200 response on success (triggers HTMX swap)
            JsonResponse: 400/404 with error message on failure
            HttpResponseForbidden: 403 if unauthorized
        """
        # Get and validate session
        try:
            session = AIGenerationSession.objects.get(id=session_id)
        except AIGenerationSession.DoesNotExist as e:
            raise Http404("Generation session not found") from e

        # Verify session ownership
        if session.user != request.user:
            return HttpResponseForbidden(
                "You don't have permission to access this generation session.",
            )

        # Get POST data
        flashcard_id = request.POST.get("flashcard_id")

        # Validate flashcard_id
        if not flashcard_id:
            return JsonResponse({"error": "Missing flashcard_id"}, status=400)

        # Get flashcard and verify it belongs to this session
        try:
            flashcard = Flashcard.objects.get(
                id=flashcard_id,
                ai_session=session,
                user=request.user,
                ai_review_state=Flashcard.PENDING,
            )
        except Flashcard.DoesNotExist:
            return JsonResponse(
                {"error": "Flashcard not found or already reviewed"},
                status=404,
            )

        # Update flashcard to rejected state
        flashcard.ai_review_state = Flashcard.REJECTED
        flashcard.save(update_fields=["ai_review_state", "updated_at"])

        # Return empty response (HTMX will remove card from DOM)
        return HttpResponse(status=200)
