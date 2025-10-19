# API Endpoint Implementation Plan: POST /api/generations

## 1. Endpoint Overview

The `POST /api/generations` endpoint generates flashcard proposals from user-provided input text using AI. This endpoint is central to the MVP's AI-powered flashcard generation feature and directly supports the success metric of achieving 75% AI-generated flashcard acceptance rate.

**Key Characteristics:**
- Generates 5-10 flashcard proposals without saving them to the database
- Creates an `AIGenerationSession` record for every attempt (success or failure) to track analytics
- Uses OpenRouter API with Claude model for generation (mocked for MVP)
- Returns proposals to the user for review and acceptance
- Tracks performance metrics (API response time) and error details for debugging

**Authentication:** Required (session-based with CSRF protection)

## 2. Request Details

**HTTP Method:** POST

**URL Structure:** `/api/generations`

**Authentication:** Django session-based authentication (DRF's `SessionAuthentication`)

**Permissions:** `IsAuthenticated` permission class

**CSRF Protection:** Required (must include `X-CSRFToken` header)

**Request Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token_value>
Cookie: sessionid=<session_id>; csrftoken=<csrf_token>
```

**Request Body:**
```json
{
  "input_text": "The French Revolution was a period of radical political and societal change in France that began with the Estates General of 1789..."
}
```

**Parameters:**

**Required:**
- `input_text` (string): The text from which to generate flashcards
  - Constraints: Non-empty, maximum 10,000 characters
  - Should be trimmed of leading/trailing whitespace before validation

**Optional:**
- None

## 3. Used Types

### Request DTOs

**GenerationRequestSerializer** (DRF Serializer)
```python
{
  "input_text": str  # Required, max_length=10000, min_length=1
}
```

Fields:
- `input_text`: TextField with validators:
  - `required=True`
  - `max_length=10000`
  - `min_length=1` (after trimming)
  - `trim_whitespace=True`
  - `allow_blank=False`

### Response DTOs

**GeneratedFlashcardSerializer** (DRF Serializer)
```python
{
  "front": str,  # Max 200 characters
  "back": str    # Max 500 characters
}
```

**GenerationResponseSerializer** (DRF Serializer)
```python
{
  "session_id": int,
  "generated_count": int,
  "generated_flashcards": List[GeneratedFlashcardSerializer]
}
```

### Command Models (Service Layer)

**GenerateFlashcardsCommand**
```python
{
  "user": User,
  "input_text": str,
  "model_name": str  # Default: "mock_model" for MVP
}
```

**GenerationResult**
```python
{
  "session_id": int,
  "generated_count": int,
  "flashcards": List[dict],  # [{"front": str, "back": str}, ...]
  "success": bool,
  "error_code": Optional[str],
  "error_message": Optional[str],
  "api_response_time_ms": Optional[int]
}
```

## 4. Response Details

### Success Response (200 OK)

**Status Code:** 200 OK (Note: Using 200 instead of 201 because no persistent resources are created; flashcards are proposals only)

**Response Body:**
```json
{
  "session_id": 789,
  "generated_count": 5,
  "generated_flashcards": [
    {
      "front": "When did the French Revolution begin?",
      "back": "The French Revolution began in 1789 with the Estates General."
    },
    {
      "front": "When did the French Revolution end?",
      "back": "The French Revolution ended in November 1799 with the formation of the French Consulate."
    },
    {
      "front": "What characterized the French Revolution?",
      "back": "It was a period of radical political and societal change in France."
    },
    {
      "front": "What was the Estates General?",
      "back": "A legislative and consultative assembly that marked the beginning of the French Revolution in 1789."
    },
    {
      "front": "What was the French Consulate?",
      "back": "The government system formed in November 1799 that marked the end of the French Revolution."
    }
  ]
}
```

### Error Responses

**400 Bad Request - Validation Error**
```json
{
  "error": "validation_error",
  "details": {
    "input_text": ["This field is required."]
  }
}
```

Common validation errors:
- "This field is required."
- "Ensure this field has no more than 10000 characters."
- "This field may not be blank."

**401 Unauthorized - Not Authenticated**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden - CSRF Token Missing**
```json
{
  "detail": "CSRF Failed: CSRF token missing or incorrect."
}
```

**500 Internal Server Error - AI Generation Failure**
```json
{
  "error": "generation_failed",
  "message": "Couldn't generate flashcards right now. Please try again."
}
```

## 5. Data Flow

### Happy Path Flow

1. **Request Reception:**
   - DRF receives POST request at `/api/generations`
   - Django middleware validates session cookie and CSRF token
   - DRF's `SessionAuthentication` authenticates user
   - `IsAuthenticated` permission check passes

2. **Input Validation:**
   - `GenerationRequestSerializer` validates request body
   - Checks `input_text` is present and within 10,000 character limit
   - Trims whitespace and ensures non-empty

3. **Service Layer Invocation:**
   - View instantiates `FlashcardGenerationService`
   - Creates `GenerateFlashcardsCommand` with:
     - `user`: `request.user`
     - `input_text`: validated input
     - `model_name`: "mock_model" (hardcoded for MVP)

4. **AIGenerationSession Creation:**
   - Service creates `AIGenerationSession` record:
     ```python
     session = AIGenerationSession.objects.create(
         user=command.user,
         input_text=command.input_text,
         model=command.model_name,
         generated_count=0,  # Updated after generation
     )
     ```
   - Timestamp `created_at` auto-populated

5. **AI Generation (Mocked for MVP):**
   - Service calls `_generate_flashcards_mock()` method
   - Returns hardcoded list of 5-7 flashcards with educational content
   - Simulates API response time (e.g., random 500-2000ms)

6. **Response Validation:**
   - Service validates each generated flashcard:
     - `front`: non-empty, max 200 characters
     - `back`: non-empty, max 500 characters
   - Filters out invalid flashcards (logs warnings)
   - Counts valid flashcards

7. **Session Update:**
   - Updates `AIGenerationSession` record:
     ```python
     session.generated_count = len(valid_flashcards)
     session.api_response_time_ms = response_time_ms
     session.save()
     ```

8. **Response Construction:**
   - Service returns `GenerationResult` object
   - View serializes result with `GenerationResponseSerializer`
   - Returns 200 OK with JSON response

### Error Path Flow

**Validation Error (400):**
1. `GenerationRequestSerializer` validation fails
2. DRF automatically returns 400 with error details
3. No database operations performed

**Authentication Error (401/403):**
1. Session authentication fails or CSRF token missing
2. DRF middleware returns 401/403 before view execution
3. No database operations performed

**AI Generation Error (500):**
1. Mock service raises exception or returns error
2. Service creates `AIGenerationSession` with error details:
   ```python
   session = AIGenerationSession.objects.create(
       user=command.user,
       input_text=command.input_text,
       model=command.model_name,
       generated_count=0,
       error_message=str(exception),
       error_code="ai_generation_failed",
   )
   ```
3. Service returns `GenerationResult` with `success=False`
4. View returns 500 with user-friendly error message

### Database Interactions (ORM)

**Write Operations:**
1. Create `AIGenerationSession`:
   ```python
   AIGenerationSession.objects.create(
       user=request.user,
       input_text=validated_data['input_text'],
       model="mock_model",
       generated_count=len(flashcards),
       api_response_time_ms=response_time,
   )
   ```

2. Update `AIGenerationSession` on error:
   ```python
   session.error_message = error_msg
   session.error_code = error_code
   session.save(update_fields=['error_message', 'error_code'])
   ```

**Read Operations:**
- None (user authentication handled by Django middleware)

**No Transactions Required:**
- Single atomic write operation (session creation)
- If creation fails, let exception propagate to return 500

### External Service Interactions

**For MVP (Mocked):**
- No actual external API calls
- Mock service returns hardcoded flashcards
- Simulated response time for realistic testing

**For Production (Future):**
- HTTP POST to OpenRouter API: `https://openrouter.ai/api/v1/chat/completions`
- Request timeout: 30 seconds
- Retry logic: 1 retry on timeout/5xx errors
- Rate limiting: Handled at service layer (not in this endpoint)

## 6. Security Considerations

### Authentication & Authorization

**Authentication:**
- Session-based authentication via DRF's `SessionAuthentication`
- Validates `sessionid` cookie against Django session store
- User must be logged in and email verified (django-allauth mandatory verification)

**Authorization:**
- All generated sessions belong to authenticated user (`user=request.user`)
- No cross-user access possible (sessions are user-scoped)

**CSRF Protection:**
- Django CSRF middleware enabled for POST requests
- Requires `X-CSRFToken` header matching `csrftoken` cookie
- Returns 403 Forbidden if token missing or invalid

### Input Validation & Sanitization

**Request Validation:**
1. **input_text length limit (10,000 chars):**
   - Prevents excessive AI API costs
   - Prevents resource exhaustion
   - Enforced by DRF serializer `max_length` validator

2. **Whitespace trimming:**
   - `trim_whitespace=True` in serializer
   - Prevents empty-but-whitespace inputs

3. **No HTML/script injection risk:**
   - API returns JSON only (not rendered HTML)
   - Frontend responsible for XSS prevention when displaying flashcards

**AI Prompt Injection Mitigation:**
1. Use structured prompt templates with clear boundaries
2. Prefix system instructions that cannot be overridden
3. Validate AI responses before returning to user
4. For production: Implement content filtering on both input and output

### Rate Limiting (Future Consideration)

**Not implemented in MVP, but planned:**
- Per-user rate limit: 10 requests per minute
- Per-user daily limit: 100 generations per day
- Prevents abuse and controls AI API costs
- Implementation: Django REST Framework throttling classes

### Data Privacy

**Stored Data:**
- `input_text`: Stored in `AIGenerationSession` for analytics
- Not shared with other users
- No PII beyond authenticated user association

**Sensitive Data Handling:**
- No passwords or credentials in requests
- Session cookies are HTTP-only and Secure (production)
- Database connections use SSL/TLS (production)

### Error Information Disclosure

**Generic Error Messages:**
- Internal errors return: "Couldn't generate flashcards right now. Please try again."
- Avoid exposing stack traces, internal paths, or system details
- Detailed errors logged server-side only

**Session ID Exposure:**
- Session IDs are exposed in responses for analytics
- Using integer PKs (acceptable for MVP)
- For production: Consider UUIDs to prevent enumeration

## 7. Error Handling

### Client Errors (4xx)

| Status Code | Error Scenario | Response Body | View Handling |
|-------------|----------------|---------------|---------------|
| 400 Bad Request | Missing `input_text` | `{"error": "validation_error", "details": {"input_text": ["This field is required."]}}` | DRF serializer validation automatic |
| 400 Bad Request | `input_text` exceeds 10,000 chars | `{"error": "validation_error", "details": {"input_text": ["Ensure this field has no more than 10000 characters."]}}` | DRF serializer validation automatic |
| 400 Bad Request | Empty `input_text` after trim | `{"error": "validation_error", "details": {"input_text": ["This field may not be blank."]}}` | DRF serializer validation automatic |
| 400 Bad Request | Malformed JSON | `{"detail": "JSON parse error - ..."}` | DRF parser automatic |
| 401 Unauthorized | No session cookie | `{"detail": "Authentication credentials were not provided."}` | DRF authentication automatic |
| 401 Unauthorized | Invalid/expired session | `{"detail": "Invalid session."}` | DRF authentication automatic |
| 403 Forbidden | Missing CSRF token | `{"detail": "CSRF Failed: CSRF token missing or incorrect."}` | Django middleware automatic |
| 403 Forbidden | Email not verified | `{"error": "email_not_verified", "message": "Please verify your email address."}` | Custom permission class |

### Server Errors (5xx)

| Status Code | Error Scenario | Response Body | View Handling |
|-------------|----------------|---------------|---------------|
| 500 Internal Server Error | AI generation failure | `{"error": "generation_failed", "message": "Couldn't generate flashcards right now. Please try again."}` | Catch exception in service, create session with error, return structured error |
| 500 Internal Server Error | AI response parsing error | Same as above | Catch `JSONDecodeError` in service |
| 500 Internal Server Error | Database error (session creation) | `{"error": "internal_error", "message": "An unexpected error occurred. Please try again."}` | Let DRF exception handler return generic 500 |
| 500 Internal Server Error | Generated flashcard validation failure | `{"error": "generation_failed", "message": "Couldn't generate flashcards right now. Please try again."}` | Service logs warning, creates session with error |

### Error Handling Strategy

**Service Layer Responsibilities:**
1. Catch all AI-related exceptions (timeouts, API errors, parsing errors)
2. Create `AIGenerationSession` with error details for analytics
3. Return `GenerationResult` with `success=False`
4. Log detailed error information (exception type, stack trace, input text preview)

**View Layer Responsibilities:**
1. Check `GenerationResult.success` flag
2. If `False`, return DRF `Response` with status 500 and user-friendly message
4. Let DRF handle authentication/validation errors automatically

**Logging:**
```python
# Service layer
logger.error(
    f"AI generation failed for user {user.id}: {error_code}",
    extra={
        "user_id": user.id,
        "input_text_preview": input_text[:100],
        "session_id": session.id,
        "error_code": error_code,
        "exception": str(exception),
    }
)
```

**User-Facing Messages:**
- Generic: "Couldn't generate flashcards right now. Please try again."
- No technical details exposed

## 8. Performance Considerations

### Potential Bottlenecks

1. **AI API Call Latency:**
   - Mock: ~500-2000ms (simulated)
   - Production: 2-10 seconds (actual OpenRouter API)
   - Mitigation: Implement request timeout (30s), consider async processing for production

2. **Database Write (AIGenerationSession):**
   - Single INSERT operation: ~5-20ms
   - Negligible compared to AI API call
   - Mitigation: Use database connection pooling (Django default)

3. **Request Body Parsing:**
   - Max 10,000 characters (~10KB) of text
   - Parsing: <1ms
   - Mitigation: None needed

4. **Serialization/Validation:**
   - Input validation: <5ms
   - Output serialization: <5ms (5-10 flashcards)
   - Mitigation: None needed

### Optimization Strategies

**For MVP (Synchronous):**
1. Single database write (no N+1 queries)
2. Mock service returns immediately
3. No external API calls
4. Expected total response time: <100ms

**For Production (Future):**
1. **Async Task Processing:**
   - Move AI generation to Celery task
   - Return 202 Accepted immediately
   - Client polls for results or uses WebSocket

3. **Connection Pooling:**
   - HTTP connection pool for OpenRouter API (reuse connections)
   - Database connection pooling (Django default)

4. **Rate Limiting:**
   - Throttle requests to prevent abuse
   - Protects AI API quota and database

5. **Database Indexes:**
   - Already present: `ai_session_user_created_idx` for user queries
   - No additional indexes needed for this endpoint

## 9. Implementation Steps

1. **Create Service Layer**
   - Create `flashcards/core/services/flashcard_generation.py`
   - Implement `FlashcardGenerationService` class
   - Implement `_generate_flashcards_mock()` method returning 5-7 hardcoded flashcards
   - Implement `generate_flashcards()` method handling session creation and updates
   - Add logging for errors and analytics

2. **Create Serializers**
   - Create `flashcards/api/serializers/generation.py`
   - Implement `GenerationRequestSerializer` with input validation
   - Implement `GeneratedFlashcardSerializer` for output DTOs
   - Implement `GenerationResponseSerializer` for complete response
   - Add custom validators for input_text trimming and length

3. **Create API View**
   - Create `flashcards/api/views/generation.py`
   - Implement `GenerateFlashcardsView` as DRF `APIView`
   - Configure `SessionAuthentication` and `IsAuthenticated` permission
   - Implement `post()` method calling service layer
   - Handle success and error responses

4. **Configure URL Routing**
   - Add route in `flashcards/api/urls.py`: `path('generations', GenerateFlashcardsView.as_view())`
   - Include API URLs in main `config/urls.py` if not already included

5. **Add Error Handling**
   - Implement custom exception handler for structured error responses
   - Configure DRF settings to use custom exception handler
   - Add user-friendly error messages for common scenarios

6. **Manual Testing**
   - Test happy path with valid input
   - Test validation errors (missing input, too long)
   - Test authentication errors (no session, expired session)
   - Test CSRF protection (missing token)
   - Verify `AIGenerationSession` records created correctly
   - Verify error sessions include error details

7. **Documentation**
   - Update API documentation with endpoint details
   - Document mock service behavior
   - Add example requests/responses to README or API docs
