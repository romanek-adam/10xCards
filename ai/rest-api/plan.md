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

### 2.1 Authentication Endpoints

None

### 2.2 Flashcard Endpoints

#### GET /api/flashcards
**Description:** List all flashcards for authenticated user with pagination
**Authentication:** Required

**Query Parameters:**
- `page` (integer, optional): Page number, default 1
- `page_size` (integer, optional): Items per page (25-50), default 25
- `sort` (string, optional): Sort order, default "-created_at" (newest first)

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "https://api.10xcards.com/api/flashcards?page=2",
  "previous": null,
  "results": [
    {
      "id": 456,
      "front": "What is the capital of France?",
      "back": "Paris",
      "creation_method": "ai_full",
      "created_at": "2025-01-18T14:22:00Z",
      "updated_at": "2025-01-18T14:22:00Z"
    },
    {
      "id": 455,
      "front": "Define photosynthesis",
      "back": "The process by which plants convert light energy into chemical energy",
      "creation_method": "manual",
      "created_at": "2025-01-17T09:15:00Z",
      "updated_at": "2025-01-17T09:15:00Z"
    }
  ]
}
```

---

#### POST /api/flashcards
**Description:** Create a new flashcard (manual or accepted AI-generated)
**Authentication:** Required

**Request Payload (Manual):**
```json
{
  "front": "What is the Pythagorean theorem?",
  "back": "a² + b² = c² for right triangles",
  "creation_method": "manual"
}
```

**Request Payload (AI-generated, accepted without edits):**
```json
{
  "front": "What is the Pythagorean theorem?",
  "back": "a² + b² = c² for right triangles",
  "creation_method": "ai_full",
  "ai_session_id": 789
}
```

**Request Payload (AI-generated, edited before accepting):**
```json
{
  "front": "What is the Pythagorean theorem formula?",
  "back": "In a right triangle: a² + b² = c² where c is the hypotenuse",
  "creation_method": "ai_edited",
  "ai_session_id": 789
}
```

**Response (201 Created):**
```json
{
  "id": 457,
  "front": "What is the Pythagorean theorem?",
  "back": "a² + b² = c² for right triangles",
  "creation_method": "manual",
  "ai_session": null,
  "created_at": "2025-01-18T15:30:00Z",
  "updated_at": "2025-01-18T15:30:00Z"
}
```

**Validation Rules:**
- `front`: Required, 1-200 characters
- `back`: Required, 1-500 characters
- `creation_method`: Required, must be one of: "ai_full", "ai_edited", "manual"
- `ai_session_id`: Optional, required if creation_method is "ai_full" or "ai_edited"

**Error Responses:**
- 400 Bad Request: Validation errors
```json
{
  "error": "validation_error",
  "details": {
    "front": ["This field is required."],
    "back": ["Ensure this field has no more than 500 characters."]
  }
}
```

---

#### GET /api/flashcards/{id}
**Description:** Retrieve a specific flashcard
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 456,
  "front": "What is the capital of France?",
  "back": "Paris",
  "creation_method": "ai_full",
  "ai_session": {
    "id": 789,
    "created_at": "2025-01-18T14:20:00Z"
  },
  "created_at": "2025-01-18T14:22:00Z",
  "updated_at": "2025-01-18T14:22:00Z"
}
```

**Error Responses:**
- 404 Not Found: Flashcard doesn't exist or doesn't belong to user
```json
{
  "error": "not_found",
  "message": "Flashcard not found."
}
```

---

#### PUT /api/flashcards/{id}
**Description:** Update an existing flashcard, also changing the source method to "AI-edited" if it was "AI-full" before
**Authentication:** Required

**Request Payload:**
```json
{
  "front": "What is the capital of France?",
  "back": "Paris, France"
}
```

**Response (200 OK):**
```json
{
  "id": 456,
  "front": "What is the capital of France?",
  "back": "Paris, France",
  "creation_method": "ai_edited",
  "ai_session": {
    "id": 789,
    "created_at": "2025-01-18T14:20:00Z"
  },
  "created_at": "2025-01-18T14:22:00Z",
  "updated_at": "2025-01-18T16:45:00Z"
}
```

**Validation Rules:**
- `front`: Required, 1-200 characters
- `back`: Required, 1-500 characters

**Error Responses:**
- 400 Bad Request: Validation errors
- 404 Not Found: Flashcard doesn't exist or doesn't belong to user

---

#### DELETE /api/flashcards/{id}
**Description:** Delete a flashcard permanently
**Authentication:** Required

**Response (204 No Content):** No response body

**Error Responses:**
- 404 Not Found: Flashcard doesn't exist or doesn't belong to user

---

### 2.3 AI Generation Endpoints

#### POST /api/generations
**Description:** Generate flashcard proposals from text using AI
**Authentication:** Required
**Business logic:**
- Validate inputs (based on Django model validations).
- Call the AI service to generate flashcards proposals.
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

#### GET /api/generations
**Description:** List AI generation sessions for analytics
**Authentication:** Required

**Query Parameters:**
- `page` (integer, optional): Page number, default 1
- `page_size` (integer, optional): Items per page, default 25

**Response (200 OK):**
```json
{
  "count": 45,
  "next": "https://api.10xcards.com/api/ai/sessions?page=2",
  "previous": null,
  "results": [
    {
      "id": 789,
      "input_text": "The French Revolution was a period...",
      "generated_count": 7,
      "model": "openrouter/anthropic/claude-3.5-sonnet",
      "error_message": null,
      "error_code": null,
      "api_response_time_ms": 2340,
      "created_at": "2025-01-18T14:20:00Z"
    },
    {
      "id": 788,
      "input_text": "Photosynthesis is the process...",
      "generated_count": 0,
      "model": "openrouter/anthropic/claude-3.5-sonnet",
      "error_message": "API timeout",
      "error_code": "timeout_error",
      "api_response_time_ms": null,
      "created_at": "2025-01-17T11:15:00Z"
    }
  ]
}
```

---

#### GET /api/generations/{id}
**Description:** Get details of a specific AI generation session
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 789,
  "input_text": "The French Revolution was a period of radical political and societal change...",
  "generated_count": 7,
  "accepted_flashcards": [
    {
      "id": 456,
      "front": "When did the French Revolution begin?",
      "back": "The French Revolution began in 1789 with the Estates General.",
      "creation_method": "ai_full"
    },
    {
      "id": 457,
      "front": "When did the French Revolution end?",
      "back": "The French Revolution ended in November 1799 with the formation of the French Consulate.",
      "creation_method": "ai_edited"
    }
  ],
  "model": "openrouter/anthropic/claude-3.5-sonnet",
  "error_message": null,
  "error_code": null,
  "api_response_time_ms": 2340,
  "created_at": "2025-01-18T14:20:00Z"
}
```

**Error Responses:**
- 404 Not Found: Session doesn't exist or doesn't belong to user

---

## 3. Authentication and Authorization

### 3.1 Authentication Mechanism

**Session-Based Authentication**

- Use Django REST Framework's `SessionAuthentication` class (the default in the project - no need to configure in each view)
- Leverages Django's default session framework for maintaining authentication state

### 3.2 Authentication Flow

1. User registers via a registration view
2. System sends verification email with confirmation link
3. User verifies email by clicking confirmation link
4. User logs in via a login view, server creates session
5. Server sets session cookie (`sessionid`) in response
6. Client includes session cookie automatically in subsequent requests
7. Server validates session on each request to protected endpoints using `SessionAuthentication`
8. For API requests that modify data (POST, PUT, PATCH, DELETE), client must include CSRF token:
   - Token available via `csrftoken` cookie or Django template tag `{% csrf_token %}`
   - Include in request header: `X-CSRFToken: <token_value>`
   - Or include in request body for form submissions
10. User logs out via a logout view, server destroys session

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

### 3.5 Additional notes

**Token (JWT) support:**
- DO NOT add any JWT support

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

4. **Response Processing:**
   - Parse JSON response from AI
   - Validate each flashcard (front/back within limits)
   - Update session with generated_count and model
   - Return flashcards to client for review

5. **Error Handling:**
   - On API failure: Update session with error_message and error_code
   - Return user-friendly error: "Couldn't generate flashcards right now. Please try again."
   - Preserve input_text in error response for retry

#### Flashcard Accept/Reject Logic
1. **Accept Flow:**
   - Client submits flashcard data to POST /api/flashcards
   - Include ai_session_id and creation_method ("ai_full" or "ai_edited")
   - Server creates Flashcard record linked to session

2. **Reject Flow:**
   - Client simply doesn't submit rejected flashcards
   - No API call needed

3. **Edit Detection:**
   - Client tracks if user modified front/back before accepting
   - If modified: creation_method = "ai_edited"
   - If unchanged: creation_method = "ai_full"

#### Flashcard CRUD Business Logic
1. **Create (Manual):**
   - Validate front and back fields
   - Set creation_method = "manual"
   - Set ai_session = null
   - Associate with authenticated user

2. **Update:**
   - Verify flashcard belongs to user
   - Validate front and back fields
   - Update updated_at timestamp
   - Return success message

3. **Delete:**
   - Verify flashcard belongs to user
   - Perform hard delete (permanent removal)
   - Return 204 No Content

4. **List:**
   - Filter by authenticated user automatically
   - Sort by created_at descending (newest first)
   - Paginate with 25-50 items per page
   - Include total count for UI

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
