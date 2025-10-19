"""API view for flashcard generation endpoint.

This module implements the POST /api/generations endpoint that generates
flashcard proposals from user input text using AI.
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from flashcards.api.serializers.generation import GenerationRequestSerializer
from flashcards.api.serializers.generation import GenerationResponseSerializer
from flashcards.core.services.flashcard_generation import FlashcardGenerationService
from flashcards.core.services.flashcard_generation import GenerateFlashcardsCommand

logger = logging.getLogger(__name__)


class GenerateFlashcardsView(APIView):
    """API view for generating flashcard proposals from input text.

    **Endpoint:** POST /api/generations

    **Authentication:** Session-based authentication with CSRF protection

    **Permissions:** IsAuthenticated (user must be logged in)

    **Request Body:**
    ```json
    {
        "input_text": "The French Revolution was a period of radical political..."
    }
    ```

    **Success Response (200 OK):**
    ```json
    {
        "session_id": 789,
        "generated_count": 5,
        "generated_flashcards": [
            {
                "front": "When did the French Revolution begin?",
                "back": "The French Revolution began in 1789..."
            },
            ...
        ]
    }
    ```

    **Error Responses:**
    - 400 Bad Request: Validation errors (missing/invalid input_text)
    - 401 Unauthorized: Not authenticated
    - 403 Forbidden: CSRF token missing
    - 500 Internal Server Error: AI generation failure
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        """Initialize view with flashcard generation service."""
        super().__init__(**kwargs)
        self.service = FlashcardGenerationService()

    def post(self, request):
        """Handle POST request to generate flashcards.

        Flow:
        1. Validate request body using GenerationRequestSerializer
        2. Create GenerateFlashcardsCommand with user and input_text
        3. Call FlashcardGenerationService.generate_flashcards()
        4. Return 200 OK with generated flashcards on success
        5. Return 500 with error message on AI generation failure

        Args:
            request: DRF Request object with authenticated user and JSON body

        Returns:
            Response object with appropriate status code and data
        """
        # Validate request body
        serializer = GenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        input_text = serializer.validated_data["input_text"]

        # Create command object for service layer
        command = GenerateFlashcardsCommand(
            user=request.user,
            input_text=input_text,
            model_name="mock_model",  # Hardcoded for MVP
        )

        # Call service layer to generate flashcards
        result = self.service.generate_flashcards(command)

        # Check if generation succeeded
        if not result.success:
            # Return 500 with user-friendly error message
            return Response(
                {
                    "error": result.error_code,
                    "message": result.error_message,
                    "session_id": result.session_id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Prepare response data
        response_data = {
            "session_id": result.session_id,
            "generated_count": result.generated_count,
            "generated_flashcards": result.flashcards,
        }

        # Serialize and return successful response
        response_serializer = GenerationResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)
