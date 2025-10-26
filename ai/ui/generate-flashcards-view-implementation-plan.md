# View Implementation Plan: Generate Flashcards

## 1. Overview

Two views for AI-powered flashcard generation: (1) **Generate Flashcards (Input)** where users paste text into a large textarea and submit for AI generation, and (2) **Generate Flashcards (Review)** where users review AI-generated flashcards and accept/reject each one with inline editing capability. The flow creates an AIGenerationSession, generates 5-10 flashcards via Gemini API, and allows users to curate results before saving to their collection.

## 2. View Routing

- **Generate Flashcards (Input):** `/flashcards/generate/`
- **Generate Flashcards (Review):** `/flashcards/generate/review/<session_id>/`

## 3. Component Structure

```
GenerateFlashcardsInputView (Django Template View)
├── Form (Bootstrap form)
│   ├── Textarea (large input, 15+ rows)
│   ├── SubmitButton (Generate button)
│   └── LoadingSpinner (overlay during processing)
└── ErrorAlert (displayed on failure with input preservation)

GenerateFlashcardsReviewView (Django Template View)
├── FlashcardReviewList (vertical stack)
│   └── FlashcardReviewCard (repeated for each generated card)
│       ├── EditableFront (textarea/contenteditable)
│       ├── EditableBack (textarea/contenteditable)
│       └── ActionButtons
│           ├── AcceptButton (success style)
│           └── RejectButton (danger style)
└── NavigationMessage (return to My Flashcards instruction)
```

## 4. Component Details

### GenerateFlashcardsInputView
- **Component description:** Main view for text input and submission. Displays a large textarea for pasting study material (max 10,000 chars), a Generate button, and handles loading/error states.
- **Main elements:** Bootstrap form container with textarea (15+ rows), submit button, hidden loading spinner overlay with message, hidden error alert div (Bootstrap alert-danger).
- **Handled interactions:** Form submit (POST), loading state during AI generation, error display on failure.
- **Handled validation:** Server-side only - validates text length up to 10,000 characters. No client-side character counter or validation feedback.
- **Types:** None (standard Django form view).
- **Props:** None (top-level Django template view).

### LoadingSpinner
- **Component description:** Overlay spinner displayed during AI generation with message "Generating flashcards... This may take up to 30 seconds".
- **Main elements:** Bootstrap spinner component, overlay div with semi-transparent background, centered loading message text.
- **Handled interactions:** Shown on form submit, hidden when response received or error occurs.
- **Handled validation:** None.
- **Types:** None.
- **Props:** None (controlled by HTMX loading states).

### ErrorAlert
- **Component description:** Bootstrap alert-danger component displaying user-friendly error message on generation failure.
- **Main elements:** Bootstrap alert div with message "Couldn't generate flashcards right now. Please try again."
- **Handled interactions:** Displayed when generation fails, dismissible.
- **Handled validation:** None.
- **Types:** None.
- **Props:** error_message (string from server response).

### GenerateFlashcardsReviewView
- **Component description:** Review view displaying all AI-generated flashcards in vertical stack for accept/reject decisions.
- **Main elements:** Container div with vertical stack of FlashcardReviewCard components, return navigation message.
- **Handled interactions:** None (delegates to child components).
- **Handled validation:** Session ownership validation (server-side).
- **Types:** SessionFlashcardsDTO (list of flashcard proposals).
- **Props:** session_id (from URL parameter).

### FlashcardReviewCard
- **Component description:** Single flashcard card with editable front/back text and accept/reject action buttons.
- **Main elements:** Bootstrap card component containing two textareas (front/back) or contenteditable divs, button group with Accept (btn-success) and Reject (btn-danger) buttons.
- **Handled interactions:**
  - Edit front/back text inline (textarea change events)
  - Accept button click (POST to save endpoint with CSRF)
  - Reject button click (remove from DOM without server call)
- **Handled validation:**
  - Front: non-empty, max 200 characters (validated on accept)
  - Back: non-empty, max 500 characters (validated on accept)
  - Determines creation_method based on whether text was edited
- **Types:** FlashcardProposalDTO (front: str, back: str, index: int).
- **Props:** flashcard (FlashcardProposalDTO), session_id (int).

### AcceptButton
- **Component description:** Success-styled button that saves flashcard to database when clicked.
- **Main elements:** Bootstrap btn-success button with "Accept" text.
- **Handled interactions:** Click event triggers HTMX POST to `/flashcards/generate/review/<session_id>/accept/`, removes card from DOM on success.
- **Handled validation:** Server validates front/back constraints, returns validation errors if invalid.
- **Types:** None.
- **Props:** session_id (int), flashcard_id (int).

### RejectButton
- **Component description:** Danger-styled button that discards flashcard without saving.
- **Main elements:** Bootstrap btn-danger button with "Reject" text.
- **Handled interactions:** Click event removes parent card from DOM (client-side only, no server call).
- **Handled validation:** None.
- **Types:** None.
- **Props:** None.

## 5. Types

### FlashcardProposalDTO
```python
@dataclass
class FlashcardProposalDTO:
    """DTO for a single flashcard proposal in review stage."""
    flashcard_id: int
    front: str
    back: str
```

### SessionFlashcardsDTO
```python
@dataclass
class SessionFlashcardsDTO:
    """DTO for flashcard review session data."""
    session_id: int
    flashcards: list[FlashcardProposalDTO]
```

### AcceptFlashcardRequest
```python
@dataclass
class AcceptFlashcardRequest:
    """Request data for accepting a flashcard."""
    session_id: int
    flashcard_id: int
    front: str
    back: str
    was_edited: bool  # Determines creation_method (ai_full vs ai_edited)
```

## 6. State Management

State is managed server-side with minimal client state:

**Server-side state:**
- AIGenerationSession stores input_text, generated_count, error state, individual flashcard proposals are stored as `Flashcard`s with
- Session ID passed via URL parameter to review view
- Proposed flashcards saved to Flashcard model with `ai_review_state=pending`
- Accepted flashcards updated with `creation_method` (ai-full vs ai-edited) and `ai_review_state=accepted`

**Client-side state:**
- Input text preserved in textarea on error (Django form repopulation)
- Loading state managed by HTMX indicators and disabled button state
- Rejected cards removed from DOM (no persistence needed)
- Edit tracking: Compare current textarea value to original data-original-front/back attributes to determine was_edited flag

No custom hooks required - standard HTMX patterns with Bootstrap components.

## 7. API Integration

**Input View Endpoint:**
- **URL:** `POST /flashcards/generate/`
- **Request:** Form data with `input_text` field (max 10,000 chars)
- **Response:**
  - Success: Redirect to `/flashcards/generate/review/<session_id>/`
  - Failure: Re-render form with error alert and preserved input
- **CSRF:** Required (Django CSRF token in form)

**Review View Endpoint:**
- **URL:** `GET /flashcards/generate/review/<session_id>/`
- **Request:** None (session_id in URL)
- **Response:** Render review template with SessionFlashcardsDTO
- **Validation:** Verify session.user == request.user (403 if mismatch)

**Accept Flashcard Endpoint:**
- **URL:** `POST /flashcards/generate/review/<session_id>/accept/`
- **Request:** HTMX POST with form data: `flashcard_id`, `front`, `back`, `was_edited`
- **Response:**
  - Success: Return empty 200 response (HTMX removes card from DOM via hx-swap="delete")
  - Validation error: Return 400 with error message in Bootstrap alert fragment
- **Business Logic:**
  - Update Flashcard by `flashcard_id` with `creation_method` = "ai_edited" if was_edited else "ai_full" and `ai_review_state=accepted`
  - Update session accepted_count
- **CSRF:** Required

## 8. User Interactions

**Input View:**
1. User pastes text into textarea (up to 10,000 chars)
2. User clicks "Generate" button
3. Loading spinner appears with message, button disabled
4. On success: Redirect to review view with generated flashcards
5. On failure: Error alert displays, input text preserved, button re-enabled

**Review View:**
1. User sees vertical stack of 5-10 generated flashcards
2. User edits front/back text inline (optional)
3. User clicks "Accept" for desired cards:
   - Card saved to database
   - Card removed from review list with fade animation
   - Success confirmation (optional Bootstrap toast)
4. User clicks "Reject" for unwanted cards:
   - Card immediately removed from DOM
   - No server interaction
5. After reviewing all cards, user returns to My Flashcards via navbar

## 9. Conditions and Validation

**Input View:**
- Server-side validation only:
  - input_text required (non-empty)
  - input_text max 10,000 characters
  - Rate limiting on API calls (server-side middleware)
- No client-side validation or character counter
- Input preserved in form on validation failure

**Review View:**
- Session ownership: `session.user == request.user` (403 if invalid)
- Flashcard validation on accept:
  - front: non-empty, max 200 characters
  - back: non-empty, max 500 characters
- Edit detection: Compare textarea values to data-original-* attributes
- If validation fails on accept: Return 400 with error message, card remains in DOM

## 10. Error Handling

**Input View Errors:**
- LLM API failure/timeout: Display "Couldn't generate flashcards right now. Please try again."
- Validation error (>10,000 chars): Display "Input text too long (max 10,000 characters)"
- Network error: Standard Django error page or HTMX error handling
- Input text always preserved on error

**Review View Errors:**
- Invalid session_id: 404 error page
- Session ownership mismatch: 403 forbidden page
- Accept validation failure: Return Bootstrap alert fragment with specific error (e.g., "Front text too long (max 200 characters)")
- Network error during accept: Display retry message, keep card in DOM

**Security:**
- CSRF protection on all POST endpoints
- XSS prevention via Django template escaping ({{ front|escape }}, {{ back|escape }})

## 11. Implementation Steps

1. Create Django view for input page (`flashcards/core/views/generate_input.py`) with GET/POST handling
2. Create input template (`flashcards/templates/flashcards/generate_input.html`) with form, textarea, loading spinner, error alert
3. Wire up URL routing for `/flashcards/generate/` to input view
4. Implement POST handler that calls `FlashcardGenerationService.generate_flashcards()` and redirects to review view
5. Create Django view for review page (`flashcards/core/views/generate_review.py`) with session ownership validation
6. Create review template (`flashcards/templates/flashcards/generate_review.html`) with flashcard cards stack and action buttons
7. Add HTMX attributes to Accept buttons (`hx-post`, `hx-target`, `hx-swap="delete"`)
8. Add client-side Reject button handler (simple JavaScript to remove parent card)
9. Create accept endpoint (`POST /flashcards/generate/review/<session_id>/accept/`) with validation and Flashcard creation
10. Implement edit detection logic (compare textarea values to data-original-* attributes)
11. Add CSRF tokens to all forms
12. Test error scenarios (API failure, validation errors, session ownership)
13. Add loading states and visual feedback (spinner, button disable, fade animations)
14. Verify XSS protection and rate limiting configuration
