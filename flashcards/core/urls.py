"""URL configuration for the core flashcard app.

This module defines URL patterns for API endpoints that provide
programmatic access to flashcard data.
"""

from django.urls import path

from flashcards.api.views.flashcards import FlashcardListView
from flashcards.api.views.generation import GenerateFlashcardsView

app_name = "core"

urlpatterns = [
    path("api/flashcards/", FlashcardListView.as_view(), name="api-flashcard-list"),
    path("api/generations/", GenerateFlashcardsView.as_view(), name="api-generations"),
]
