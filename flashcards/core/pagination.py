"""Custom pagination classes for the core flashcard app.

This module defines DRF pagination classes that enforce business logic
requirements for API endpoints.
"""

from rest_framework.pagination import PageNumberPagination


class FlashcardPagination(PageNumberPagination):
    """Custom pagination for flashcard list endpoint.

    Enforces page_size range of 25-50 items as per PRD requirements.
    Default page size is 25 items.
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_page_size(self, request):
        """Get and validate page_size parameter.

        Ensures page_size is between 25 and 50 items.
        Returns default of 25 if parameter is missing or invalid.
        """
        page_size = super().get_page_size(request)

        # Enforce minimum page size of 25
        if page_size and page_size < 25:  # noqa: PLR2004
            return 25

        return page_size
