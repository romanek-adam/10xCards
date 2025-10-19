# REST API Plan

## 1. Resources

### 1.1 User
**Corresponding Model:** `flashcards.users.User` (AUTH_USER_MODEL)
**Description:** Represents authenticated students using the application

### 1.2 Flashcard
**Corresponding Model:** `flashcards.core.models.Flashcard`
**Description:** User-owned flashcards created manually or via AI generation

### 1.3 AIGenerationSession
**Corresponding Model:** `flashcards.core.models.AIGenerationSession`
**Description:** Tracks AI flashcard generation attempts for analytics and success metrics

---

## 2. Endpoints

### 2.3 AI Generation Endpoints

#### POST /api/generations
**Description:** Generate flashcard proposals from text using AI
**Authentication:** Required
**Business logic:**
- Validate inputs (based on Django model validations).
- Call the AI service to generate flashcards proposals (mock it for now)
- Store the generation metadata and return flashcard proposals to the user.

**Request Payload:**
```json
{
  "input_text": "The French Revolution was a period of radical political and societal change in France that began with the Estates General of 1789 and ended with the formation of the French Consulate in November 1799..."
}
```

**Response (200 OK):**
```json
{
  "session_id": 789,
  "generated_count": 7,
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

**Validation Rules:**
- `input_text`: Required, maximum 10,000 characters

**Error Responses:**
- 400 Bad Request: Input validation error
```json
{
  "error": "validation_error",
  "details": {
    "input_text": ["This field is required."]
  }
}
```
- 500 Internal Server Error: AI generation failure
```json
{
  "error": "generation_failed",
  "message": "Couldn't generate flashcards right now. Please try again.",
  "session_id": 789
}
```

**Note:**
- Even on failure, an AIGenerationSession record is created with error details for analytics

---

## 3. Authentication and Authorization

### 3.1 Authentication Mechanism

**Session-Based Authentication**

- Use Django REST Framework's `SessionAuthentication` class (the default in the project - no need to configure in each view)
- Leverages Django's default session framework for maintaining authentication state

### 3.2 Authentication Flow

1. User logs in via a login view, server creates session
2. Server sets session cookie (`sessionid`) in response
3. Client includes session cookie automatically in subsequent requests
4. Server validates session on each request to protected endpoints using `SessionAuthentication`
5. For API requests that modify data (POST, PUT, PATCH, DELETE), client must include CSRF token:
   - Token available via `csrftoken` cookie or Django template tag `{% csrf_token %}`
   - Include in request header: `X-CSRFToken: <token_value>`
   - Or include in request body for form submissions
6. User logs out via a logout view, server destroys session

### 3.3 Authorization Rules

**User Isolation:**
- Users can only access their own resources (flashcards, AI generation sessions)
- Implemented using Django ORM filters: `queryset.filter(user=request.user)`
- Attempted access to other users' resources returns 404 Not Found (not 403 to prevent resource enumeration)

**Endpoint Protection:**
- All endpoints except authentication endpoints require valid session (authenticated user)
- Unauthenticated requests to protected endpoints return 401 Unauthorized or 403 Forbidden
- Invalid or expired sessions return 401 Unauthorized with error details
- Missing CSRF token on unsafe methods (POST, PUT, PATCH, DELETE) returns 403 Forbidden

### 3.4 Security Measures

**Input Validation:**
- All request payloads validated using Django REST Framework serializers
- Minimum and maximum field lengths enforced (based the respective Django model validators)

**CSRF Protection:**
- Django's CSRF middleware enabled for all state-changing requests (POST, PUT, PATCH, DELETE)
- CSRF token required in `X-CSRFToken` header or request body for unsafe methods
- CSRF token available via `csrftoken` cookie or Django template tag
- CSRF exempt only for read-only GET requests

**SQL Injection Prevention:**
- Use Django ORM exclusively (no raw SQL queries)

**XSS Prevention:**
- API returns JSON only (not HTML)
- Frontend responsible for sanitizing user-generated content before display

**Token (JWT) support:**
- NO JWT support in API

---

## 4. Validation and Business Logic

### 4.2 Business Logic Implementation

#### AI Flashcard Generation Flow
1. **Request Validation:**
   - Validate input_text length (max 10,000 characters)

2. **Session Creation:**
   - Create AIGenerationSession record with user and input_text
   - Store timestamp for created_at

3. **AI API Call:**
   - Send input_text to OpenRouter API
   - Include system prompt for educational flashcard generation
   - Request 5-10 flashcards in structured JSON format
   - Track API response time
   - MOCK for now - generate a static/fixed response

4. **Response Processing:**
   - Parse JSON response from AI
   - Validate each flashcard (front/back within limits)
   - Update session with generated_count and model
   - Return flashcards to client for review

5. **Error Handling:**
   - On API failure: Update session with error_message and error_code
   - Return user-friendly error: "Couldn't generate flashcards right now. Please try again."
   - Preserve input_text in error response for retry

### 4.3 Error Handling Strategy

**Client Errors (4xx):**
- 400 Bad Request: Validation errors, malformed JSON
- 401 Unauthorized: Missing or invalid session (not authenticated)
- 403 Forbidden: Email not verified, missing CSRF token, or permission denied
- 404 Not Found: Resource doesn't exist or doesn't belong to user

**Server Errors (5xx):**
- 500 Internal Server Error: AI generation failure, database errors

**Error Response Format Example:**
```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field_name": ["Specific validation error"]
  }
}
```

**User-Friendly Error Messages:**
- AI generation failure: "Couldn't generate flashcards right now. Please try again."
- Validation errors: "Front is required.", "Back must be 500 characters or less."
- Authentication errors: "Invalid email or password.", "Please verify your email address."

---

## 5. Implementation Notes

### 5.1 Technology Stack Alignment
- **Django REST Framework:** Primary framework for API implementation with SessionAuthentication
- **PostgreSQL:** Database with excellent support for Django ORM and session storage
- **OpenRouter API:** AI flashcard generation service
- **Session-Based Authentication:** Django's session framework integrated with django-allauth
- **HTMX Integration:** API designed to support both JSON responses and HTML fragments for HTMX (works seamlessly with session-based auth and CSRF protection)

### 5.2 Assumptions
1. **Spaced Repetition Library:** Assumes integration with external library (e.g., fsrs-py) for scheduling logic
2. **AI Model:** Assumes OpenRouter API with Claude 3.5 Sonnet or similar model
3. **Rate Limiting:** Assumes Redis backend for distributed rate limiting
4. **Email Service:** Assumes email service (e.g., SendGrid, SES) configured for verification and password reset
5. **Frontend:** API designed to support both SPA (React/Vue) and HTMX-based server-rendered frontend

### 5.3 AI Generation Implementation Details

**OpenRouter API Integration:**
- Model: `anthropic/claude-4.5-sonnet` or similar
- System prompt instructs AI to generate 5-10 educational flashcards
- Response format: Structured JSON with array of {front, back} objects
- Timeout: 30 seconds maximum
- Error handling: Graceful degradation with user-friendly messages

**Prompt Template:**
```
Generate 5-10 educational flashcards from the following text. Each flashcard should have a concise question (front) and a clear answer (back). Format your response as JSON with this structure: {"flashcards": [{"front": "question", "back": "answer"}, ...]}

Text: {user_input_text}
```
