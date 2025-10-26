"""Django view for flashcard generation review page."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.views.generic import DetailView

from flashcards.core.models import AIGenerationSession
from flashcards.core.models import Flashcard


class GenerateFlashcardsReviewView(LoginRequiredMixin, DetailView):
    """View for reviewing AI-generated flashcards.

    Displays all flashcards generated in a session for user review.
    Users can accept (with optional edits) or reject each flashcard.

    Security:
    - Verifies session ownership (session.user == request.user)
    - Returns 403 if user tries to access another user's session
    """

    model = AIGenerationSession
    template_name = "flashcards/generate_review.html"
    context_object_name = "session"
    pk_url_kwarg = "session_id"

    def get_object(self, queryset=None):
        """Get the AIGenerationSession and verify ownership.

        Returns:
            AIGenerationSession: The session object

        Raises:
            Http404: If session doesn't exist
            HttpResponseForbidden: If session doesn't belong to request user
        """
        session = super().get_object(queryset)

        # Verify session ownership
        if session.user != self.request.user:
            return HttpResponseForbidden(
                "You don't have permission to access this generation session.",
            )

        return session

    def get_context_data(self, **kwargs):
        """Add generated flashcards to template context.

        Returns:
            dict: Template context with session and pending flashcards
        """
        context = super().get_context_data(**kwargs)

        # Get all pending flashcards for this session
        pending_flashcards = Flashcard.objects.filter(
            ai_session=self.object,
            ai_review_state=Flashcard.PENDING,
        ).order_by("id")

        context["flashcards"] = pending_flashcards
        context["flashcard_count"] = pending_flashcards.count()

        return context
