"""URL configuration for the core flashcard app.

This module defines URL patterns for both web views and API endpoints.
"""

from django.urls import path

from flashcards.api.views.flashcards import FlashcardListView as FlashcardAPIListView
from flashcards.api.views.generation import GenerateFlashcardsView
from flashcards.core.views import FlashcardDeleteView
from flashcards.core.views import FlashcardListView

app_name = "core"

urlpatterns = [
    # Web views
    path("flashcards/", FlashcardListView.as_view(), name="flashcard-list"),
    path(
        "flashcards/<int:pk>/delete/",
        FlashcardDeleteView.as_view(),
        name="flashcard-delete",
    ),
    # API endpoints
    path("api/flashcards/", FlashcardAPIListView.as_view(), name="api-flashcard-list"),
    path("api/generations/", GenerateFlashcardsView.as_view(), name="api-generations"),
]
