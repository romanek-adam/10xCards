"""Django view for displaying paginated list of user's flashcards."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from flashcards.core.models import Flashcard


class FlashcardListView(LoginRequiredMixin, ListView):
    """Display paginated list of user's flashcards.

    Supports:
    - User-specific queryset filtering for security
    - Configurable page size via query parameter (25-50 items)
    - HTMX-aware template selection (full page vs. fragment)
    """

    model = Flashcard
    template_name = "flashcards/flashcard_list.html"
    context_object_name = "flashcards"
    paginate_by = 25

    def get_queryset(self):
        """Return only flashcards owned by authenticated user.

        Applies application-level row security using the custom manager's
        for_user() method to ensure users can only access their own flashcards.
        """
        return Flashcard.objects.for_user(self.request.user).ready()

    def get_paginate_by(self, queryset):
        """Allow page_size override via query param, clamped to 25-50.

        Args:
            queryset: The queryset to paginate (unused but required by Django)

        Returns:
            int: Validated page size between 25 and 50, defaulting to 25
        """
        page_size = self.request.GET.get("page_size", 25)
        try:
            page_size = int(page_size)
            return max(25, min(50, page_size))
        except (ValueError, TypeError):
            return 25

    def get_template_names(self):
        """Return fragment template for HTMX requests, full page otherwise.

        When HTMX makes a request (detected via HX-Request header), returns
        only the list items fragment for efficient DOM swapping. For normal
        requests, returns the full page template.

        Returns:
            list: Template name(s) to render
        """
        if self.request.headers.get("HX-Request"):
            return ["flashcards/_flashcard_list_items.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        """Add additional context data for template rendering.

        Extends base context with:
        - total_count: Total number of user's flashcards
        - has_flashcards: Boolean indicating if user has any flashcards
        - page_size: Current page size for pagination

        Returns:
            dict: Template context dictionary
        """
        context = super().get_context_data(**kwargs)
        context["total_count"] = self.get_queryset().count()
        context["has_flashcards"] = context["total_count"] > 0
        context["page_size"] = self.get_paginate_by(None)
        return context
