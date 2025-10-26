"""Django view for flashcard generation input page."""

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from flashcards.core.services.flashcard_generation import FlashcardGenerationService
from flashcards.core.services.flashcard_generation import GenerateFlashcardsCommand


class GenerateFlashcardsForm(forms.Form):
    """Form for flashcard generation input.

    Validates input text length (max 10,000 characters) and provides
    Bootstrap-styled form field rendering.
    """

    input_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 15,
                "placeholder": "Paste your study material here (up to 10,000 characters)...",
                "maxlength": 10000,
            },
        ),
        max_length=10000,
        required=True,
        help_text="Paste text from your notes, textbook, or any study material. The AI will generate 5-10 flashcards from it.",
        error_messages={
            "required": "Please enter some text to generate flashcards from.",
            "max_length": "Input text too long (max 10,000 characters).",
        },
    )


class GenerateFlashcardsInputView(LoginRequiredMixin, FormView):
    """View for flashcard generation input page.

    Displays a form with large textarea for pasting study material.
    On successful generation, redirects to review page where user can
    accept/reject generated flashcards.

    GET: Display input form
    POST: Generate flashcards and redirect to review page
    """

    template_name = "flashcards/generate_input.html"
    form_class = GenerateFlashcardsForm

    def form_valid(self, form):
        """Handle successful form submission.

        Calls FlashcardGenerationService to generate flashcards and
        redirects to review page on success. On failure, re-renders
        form with error message.

        Args:
            form: Validated GenerateFlashcardsForm instance

        Returns:
            HttpResponse: Redirect to review page or re-rendered form
        """
        input_text = form.cleaned_data["input_text"]

        # Generate flashcards using service
        service = FlashcardGenerationService()
        command = GenerateFlashcardsCommand(
            user=self.request.user,
            input_text=input_text,
        )

        result = service.generate_flashcards(command)

        if result.success:
            # Redirect to review page with session_id
            return redirect(
                reverse(
                    "core:generate-review",
                    kwargs={"session_id": result.session_id},
                ),
            )
        # Generation failed - re-render form with error
        form.add_error(
            None,
            result.error_message
            or "Couldn't generate flashcards right now. Please try again.",
        )
        return self.form_invalid(form)
