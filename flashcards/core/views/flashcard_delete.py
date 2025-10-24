"""Django view for handling flashcard deletion with HTMX support."""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from flashcards.core.models import Flashcard

logger = logging.getLogger(__name__)


class FlashcardDeleteView(LoginRequiredMixin, View):
    """Handle flashcard deletion with ownership validation and HTMX support.

    Supports:
    - User ownership validation for security
    - HTMX-friendly HTML fragment responses
    - Success/error messaging via Django messages framework
    - Automatic list refresh after deletion with pagination
    """

    def delete(self, request, pk):
        """Delete flashcard and return updated list.

        Args:
            request: HttpRequest with authenticated user
            pk: Primary key of flashcard to delete

        Returns:
            HttpResponse: Rendered HTML fragment with updated flashcard list
                         and success/error message
        """
        flashcard = get_object_or_404(
            Flashcard,
            pk=pk,
            user=request.user,
        )

        try:
            flashcard.delete()
            messages.success(request, "Flashcard deleted successfully.")
        except Exception:
            logger.exception("Failed to delete flashcard %s", pk)
            messages.error(request, "Failed to delete flashcard. Please try again.")

        # Get updated queryset and paginate
        queryset = Flashcard.objects.for_user(request.user)
        page_size = 25

        try:
            page_size = int(request.GET.get("page_size", 25))
            page_size = max(25, min(50, page_size))
        except (ValueError, TypeError):
            page_size = 25

        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get("page", 1)

        # If the requested page is out of range, show page 1
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        return render(
            request,
            "flashcards/_flashcard_list_items.html",
            {
                "flashcards": page_obj.object_list,
                "page_obj": page_obj,
                "paginator": paginator,
                "is_paginated": paginator.num_pages > 1,
                "has_flashcards": queryset.exists(),
                "page_size": page_size,
            },
        )
