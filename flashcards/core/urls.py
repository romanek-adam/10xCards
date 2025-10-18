"""URL configuration for the core flashcard app.

This module defines URL patterns for API endpoints that provide
programmatic access to flashcard data.
"""

from django.urls import path

from flashcards.core.views.api import FlashcardListView

app_name = "core"

urlpatterns = [
    path("api/flashcards/", FlashcardListView.as_view(), name="api-flashcard-list"),
]
