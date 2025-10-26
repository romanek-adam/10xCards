"""URL configuration for the core flashcard app.

This module defines URL patterns for both web views and API endpoints.
"""

from django.urls import path

from flashcards.api.views.flashcards import FlashcardListView as FlashcardAPIListView
from flashcards.api.views.generation import GenerateFlashcardsView
from flashcards.core.views import AcceptFlashcardView
from flashcards.core.views import FlashcardDeleteView
from flashcards.core.views import FlashcardListView
from flashcards.core.views import GenerateFlashcardsInputView
from flashcards.core.views import GenerateFlashcardsReviewView
from flashcards.core.views import RejectFlashcardView

app_name = "core"

urlpatterns = [
    # Web views
    path("flashcards/", FlashcardListView.as_view(), name="flashcard-list"),
    path(
        "flashcards/<int:pk>/delete/",
        FlashcardDeleteView.as_view(),
        name="flashcard-delete",
    ),
    path(
        "flashcards/generate/",
        GenerateFlashcardsInputView.as_view(),
        name="generate-input",
    ),
    path(
        "flashcards/generate/review/<int:session_id>/",
        GenerateFlashcardsReviewView.as_view(),
        name="generate-review",
    ),
    path(
        "flashcards/generate/review/<int:session_id>/accept/",
        AcceptFlashcardView.as_view(),
        name="generate-accept",
    ),
    path(
        "flashcards/generate/review/<int:session_id>/reject/",
        RejectFlashcardView.as_view(),
        name="generate-reject",
    ),
    # API endpoints
    path("api/flashcards/", FlashcardAPIListView.as_view(), name="api-flashcard-list"),
    path("api/generations/", GenerateFlashcardsView.as_view(), name="api-generations"),
]
