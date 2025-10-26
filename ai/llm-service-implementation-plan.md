# LLM Service Implementation Plan

## 1. Service Description
A Django service class that provides a clean interface for interacting with Google's Gemini API. It handles chat-based interactions, supports structured JSON responses via Pydantic schemas, and manages model configuration including system instructions, temperature, and token limits.

## 2. Constructor
- `__init__(api_key: str, model: str = 'gemini-2.5-flash', system_instruction: str | None = None, temperature: float = 0.7, max_output_tokens: int = 2048)`
- Initialize `genai.Client` with API key from Django settings
- Store model name, system instruction, and default generation parameters
- Raise `ValueError` if API key is missing or invalid

## 3. Public Methods and Fields
- `generate_structured(prompt: str, response_schema: type[BaseModel]) -> BaseModel`: Generate response conforming to Pydantic schema, returns parsed object
- `generate_text(prompt: str) -> str`: Simple text generation, returns string response
- `model: str`: Current model name (read-only property)
- `default_config: GenerateContentConfig`: Default generation configuration

## 4. Private Methods and Fields
- `_client: genai.Client`: Gemini API client instance
- `_build_config(**overrides) -> GenerateContentConfig`: Merge default config with method-specific overrides (temperature, max_tokens, etc.)
- `_handle_api_error(exception: Exception) -> None`: Convert Gemini exceptions to Django-appropriate exceptions

## 5. Error Handling
- Catch `google.api_core.exceptions.GoogleAPIError` for API failures (rate limits, auth, network)
- Catch `ValidationError` from Pydantic for schema mismatches
- Raise `ImproperlyConfigured` for missing/invalid API keys
- Raise `ValueError` for invalid parameters (negative temperature, etc.)
- Log all errors with structured logging including request context

## 6. Security Considerations
- Store API key in `.env` file, load via `django-environ`, never commit to version control
- Validate and sanitize user prompts before sending (max length, content filtering)
- Implement rate limiting per user to prevent abuse
- Set appropriate timeout values to prevent hanging requests

## 7. Step-by-Step Implementation Plan

**Step 1: Setup Dependencies**
- Configure in `config/settings/base.py`: `GEMINI_API_KEY = env('GEMINI_API_KEY')`

**Step 2: Create Service Class**
- Create `flashcards/core/services/llm_service.py`
- Import required modules: `from google import genai`, `from google.genai import types`, `from pydantic import BaseModel`
- Define `GeminiLLMService` class with constructor storing client and config

**Step 3: Implement Configuration Builder**
- Implement `_build_config()` to create `types.GenerateContentConfig` objects
- Include `system_instruction`, `temperature`, `max_output_tokens`, `top_p`, `top_k`
- Accept `**overrides` to allow per-request customization

**Step 5: Implement Structured Generation**
- Implement `generate_structured()` using same API call
- Set `response_mime_type='application/json'` and `response_schema=response_schema` in config
- Return `response.parsed` for automatic Pydantic parsing
- Validate parsed result before returning

**Step 7: Error Handling & Logging**
- Wrap all API calls in try-except blocks for `google.api_core.exceptions.GoogleAPIError`
- Implement `_handle_api_error()` to map to Django exceptions
- Add logging using `logger.error()` with lazy formatting
- Include request details (model, prompt length, but NEVER the API key) in logs

**Step 9: Integration**
- Create service instance in Django views or management commands
- Use `GeminiLLMService(api_key=settings.GEMINI_API_KEY)` for instantiation
- Call `generate_structured()` with flashcard Pydantic schemas
- Handle exceptions at view layer, return appropriate HTTP responses

**Step 10: Documentation & Security Review**
- Document usage examples in docstrings
- Verify API key is not logged or exposed in error messages
- Add input validation for prompt length (e.g., max 10,000 chars)
