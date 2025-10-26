"""Django view for accepting AI-generated flashcards."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views import View

from flashcards.core.models import AIGenerationSession
from flashcards.core.models import Flashcard

# Field length validation constants
MAX_FRONT_LENGTH = 200
MAX_BACK_LENGTH = 500


class AcceptFlashcardView(LoginRequiredMixin, View):
    """View for accepting an AI-generated flashcard.

    Handles POST requests to accept a flashcard with optional edits.
    Updates the flashcard's creation_method and ai_review_state.

    Security:
    - Verifies session ownership (session.user == request.user)
    - Validates flashcard belongs to the session
    - Returns 403 if unauthorized access attempt
    """

    def post(self, request, session_id):
        """Accept a flashcard and update its state.

        Expected POST data:
        - flashcard_id: ID of the flashcard to accept
        - front: Front text (may be edited)
        - back: Back text (may be edited)

        The backend determines if the flashcard was edited by comparing
        submitted text with the original flashcard text.

        Returns:
            HttpResponse: Empty 200 response on success (triggers HTMX swap)
            JsonResponse: 400 with error message on validation failure
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
        front = request.POST.get("front", "").strip()
        back = request.POST.get("back", "").strip()

        # Validate and get flashcard
        error_response = self._validate_and_get_flashcard(
            session,
            flashcard_id,
            front,
            back,
            request.user,
        )
        if error_response:
            return error_response

        flashcard = Flashcard.objects.get(
            id=flashcard_id,
            ai_session=session,
            user=request.user,
            ai_review_state=Flashcard.PENDING,
        )

        # Determine if flashcard was edited by comparing with original
        original_front = flashcard.front.strip()
        original_back = flashcard.back.strip()
        was_edited = (front != original_front) or (back != original_back)

        # Update flashcard
        flashcard.front = front
        flashcard.back = back
        flashcard.creation_method = (
            Flashcard.AI_EDITED if was_edited else Flashcard.AI_FULL
        )
        flashcard.ai_review_state = Flashcard.ACCEPTED
        flashcard.save(
            update_fields=[
                "front",
                "back",
                "creation_method",
                "ai_review_state",
                "updated_at",
            ],
        )

        # Return empty response (HTMX will remove card from DOM)
        return HttpResponse(status=200)

    def _validate_and_get_flashcard(self, session, flashcard_id, front, back, user):
        """Validate flashcard data and return error response if invalid.

        Returns:
            JsonResponse or None: Error response if validation fails, None otherwise
        """
        # Validate flashcard_id
        if not flashcard_id:
            return JsonResponse({"error": "Missing flashcard_id"}, status=400)

        # Verify flashcard exists and belongs to session
        try:
            Flashcard.objects.get(
                id=flashcard_id,
                ai_session=session,
                user=user,
                ai_review_state=Flashcard.PENDING,
            )
        except Flashcard.DoesNotExist:
            return JsonResponse(
                {"error": "Flashcard not found or already reviewed"},
                status=404,
            )

        # Validate front and back text
        return self._validate_text_fields(front, back)

    def _validate_text_fields(self, front, back):
        """Validate front and back text fields.

        Returns:
            JsonResponse or None: Error response if validation fails, None otherwise
        """
        if not front:
            return JsonResponse({"error": "Front text is required"}, status=400)

        if len(front) > MAX_FRONT_LENGTH:
            return JsonResponse(
                {"error": f"Front text too long (max {MAX_FRONT_LENGTH} characters)"},
                status=400,
            )

        if not back:
            return JsonResponse({"error": "Back text is required"}, status=400)

        if len(back) > MAX_BACK_LENGTH:
            return JsonResponse(
                {"error": f"Back text too long (max {MAX_BACK_LENGTH} characters)"},
                status=400,
            )

        return None
