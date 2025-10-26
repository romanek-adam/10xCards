"""Views for the core flashcard app."""

from .flashcard_delete import FlashcardDeleteView
from .flashcard_list import FlashcardListView
from .generate_accept import AcceptFlashcardView
from .generate_input import GenerateFlashcardsInputView
from .generate_reject import RejectFlashcardView
from .generate_review import GenerateFlashcardsReviewView

__all__ = [
    "AcceptFlashcardView",
    "FlashcardDeleteView",
    "FlashcardListView",
    "GenerateFlashcardsInputView",
    "GenerateFlashcardsReviewView",
    "RejectFlashcardView",
]
