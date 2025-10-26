"""LLM service for interacting with Google's Gemini API."""

import logging
from typing import Any
from typing import TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google import genai
from google.genai import errors
from google.genai import types
from pydantic import BaseModel
from pydantic import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GeminiLLMService:
    """Service class for interacting with Google's Gemini API.

    Provides a clean interface for chat-based interactions with support for
    structured JSON responses via Pydantic schemas. Handles model configuration
    including system instructions, temperature, and token limits.

    Example:
        >>> from pydantic import BaseModel
        >>> class Recipe(BaseModel):
        ...     name: str
        ...     ingredients: list[str]
        >>> service = GeminiLLMService()
        >>> result = service.generate_structured(
        ...     prompt="Give me a recipe for chocolate chip cookies",
        ...     response_schema=Recipe
        ... )
        >>> print(result.name)
    """

    # Maximum prompt length to prevent abuse and excessive API costs
    MAX_PROMPT_LENGTH = 10000
    # Maximum temperature value allowed by Gemini API
    MAX_TEMPERATURE = 2.0

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash-001",
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ):
        """Initialize the Gemini LLM service.

        Args:
            api_key: Google Gemini API key. If None, uses settings.GEMINI_API_KEY
            model: Model name to use (default: gemini-2.0-flash-001)
            system_instruction: Optional system instruction for the model
            temperature: Temperature for generation (0.0-2.0, default: 0.7)
            max_output_tokens: Maximum tokens in response (default: 2048)

        Raises:
            ImproperlyConfigured: If API key is missing or invalid
            ValueError: If parameters are invalid (e.g., negative temperature)
        """
        if api_key is None:
            api_key = settings.GEMINI_API_KEY

        if not api_key:
            msg = (
                "GEMINI_API_KEY is not configured. "
                "Please set it in your .env file or pass it to the constructor."
            )
            raise ImproperlyConfigured(msg)

        if temperature < 0 or temperature > self.MAX_TEMPERATURE:
            msg = f"Temperature must be between 0 and {self.MAX_TEMPERATURE}, got {temperature}"
            raise ValueError(msg)

        if max_output_tokens <= 0:
            msg = f"max_output_tokens must be positive, got {max_output_tokens}"
            raise ValueError(msg)

        self._api_key = api_key
        self._model = model
        self._system_instruction = system_instruction
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

        try:
            self._client = genai.Client(api_key=self._api_key)
        except Exception as e:
            logger.exception("Failed to initialize Gemini client")
            msg = f"Failed to initialize Gemini client: {e}"
            raise ImproperlyConfigured(msg) from e

    @property
    def model(self) -> str:
        """Get the current model name."""
        return self._model

    @property
    def default_config(self) -> types.GenerateContentConfig:
        """Get the default generation configuration."""
        return self._build_config()

    def generate_text(self, prompt: str, **config_overrides) -> str:
        """Generate simple text response from a prompt.

        Args:
            prompt: The text prompt to send to the model
            **config_overrides: Optional config overrides (temperature, max_output_tokens, etc.)

        Returns:
            Generated text response as a string

        Raises:
            ValueError: If prompt is invalid (empty, too long, etc.)
            google.api_core.exceptions.GoogleAPIError: For API failures
        """
        self._validate_prompt(prompt)

        config = self._build_config(**config_overrides)

        try:
            logger.info(
                "Generating text with model=%s, prompt_length=%d",
                self._model,
                len(prompt),
            )
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            if not response.text:
                logger.warning("Gemini API returned empty response text")
                return ""
            logger.info(
                "Successfully generated text, response_length=%d",
                len(response.text),
            )
            return response.text  # noqa: TRY300

        except errors.APIError as e:
            self._handle_api_error(e, prompt_length=len(prompt))
            raise

        except Exception:
            logger.exception(
                "Unexpected error during text generation with model=%s",
                self._model,
            )
            raise

    def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        **config_overrides,
    ) -> T:
        """Generate response conforming to a Pydantic schema.

        Args:
            prompt: The text prompt to send to the model
            response_schema: Pydantic BaseModel class defining the expected structure
            **config_overrides: Optional config overrides (temperature, max_output_tokens, etc.)

        Returns:
            Parsed Pydantic object matching the response_schema

        Raises:
            ValueError: If prompt or schema is invalid
            ValidationError: If response doesn't match schema
            google.api_core.exceptions.GoogleAPIError: For API failures
        """
        self._validate_prompt(prompt)

        if not issubclass(response_schema, BaseModel):
            msg = "response_schema must be a Pydantic BaseModel subclass"
            raise TypeError(msg)

        config = self._build_config(
            response_mime_type="application/json",
            response_schema=response_schema,
            **config_overrides,
        )

        try:
            logger.info(
                "Generating structured output with model=%s, schema=%s, prompt_length=%d",
                self._model,
                response_schema.__name__,
                len(prompt),
            )

            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )

            if not hasattr(response, "parsed") or response.parsed is None:
                logger.error(
                    "Response missing parsed attribute for schema=%s",
                    response_schema.__name__,
                )
                msg = "API response did not contain structured data"
                raise ValidationError(msg)  # noqa: TRY301

            parsed_result = response.parsed

            try:
                validated_result = response_schema.model_validate(parsed_result)
            except ValidationError:
                logger.exception(
                    "Validation failed for schema=%s",
                    response_schema.__name__,
                )
                raise
            else:
                logger.info(
                    "Successfully generated and validated structured output for schema=%s",
                    response_schema.__name__,
                )
                return validated_result

        except errors.APIError as e:
            self._handle_api_error(
                e,
                prompt_length=len(prompt),
                schema_name=response_schema.__name__,
            )
            raise

        except ValidationError:
            raise

        except Exception:
            logger.exception(
                "Unexpected error during structured generation with model=%s, schema=%s",
                self._model,
                response_schema.__name__,
            )
            raise

    def _build_config(self, **overrides: Any) -> types.GenerateContentConfig:
        """Build generation configuration with optional overrides.

        Args:
            **overrides: Configuration parameters to override defaults

        Returns:
            GenerateContentConfig object
        """
        config_params: dict[str, Any] = {
            "temperature": self._temperature,
            "max_output_tokens": self._max_output_tokens,
        }

        if self._system_instruction:
            config_params["system_instruction"] = self._system_instruction

        config_params.update(overrides)

        return types.GenerateContentConfig(**config_params)

    def _validate_prompt(self, prompt: str) -> None:
        """Validate prompt before sending to API.

        Args:
            prompt: The prompt to validate

        Raises:
            ValueError: If prompt is invalid
        """
        if not prompt or not prompt.strip():
            msg = "Prompt cannot be empty"
            raise ValueError(msg)

        if len(prompt) > self.MAX_PROMPT_LENGTH:
            msg = (
                f"Prompt length ({len(prompt)}) exceeds maximum "
                f"allowed length ({self.MAX_PROMPT_LENGTH})"
            )
            raise ValueError(msg)

    def _handle_api_error(
        self,
        exception: errors.APIError,
        **context,
    ) -> None:
        """Handle and log API errors with context.

        Args:
            exception: The GoogleAPIError that occurred
            **context: Additional context to log (prompt_length, schema_name, etc.)
                      NEVER include the actual prompt or API key
        """
        error_context = {
            "model": self._model,
            **context,
        }

        logger.error(
            "Gemini API error: %s, context=%s",
            type(exception).__name__,
            error_context,
            exc_info=True,
        )
