# UI Architecture for 10xCards

## 1. UI Structure Overview

10xCards is a minimalist educational flashcard application built with HTMX + Bootstrap 5, featuring server-side rendering with Django templates. The UI follows a mobile-first responsive design philosophy with progressive enhancement, emphasizing simplicity and direct manipulation for student users.

**Core Design Principles:**
- **Simplicity First:** Clean layouts with no onboarding, tooltips, or complex organizational features
- **No Metadata Display:** Hide technical details, timestamps, and creation dates from users
- **Direct Manipulation:** Minimal clicks to accomplish tasks
- **Clear Feedback:** Immediate visual confirmation of actions via success messages and DOM updates
- **Error Recovery:** Preserve user input on failures to prevent data loss

**Technical Architecture:**
- Frontend: HTMX for dynamic interactions + Bootstrap 5 for styling
- Backend: Django 5.2 + Django REST Framework 3.16
- Authentication: Django session-based auth with django-allauth
- State Management: Server-side only (no client-side state)
- JavaScript: Minimal (auto-dismiss alerts, edit detection)

The application consists of 12 distinct views organized into two categories: **unauthenticated** (registration, login, password reset, email verification) and **authenticated** (flashcard management, creation, and AI generation).

---

## 2. View List

### 2.1 Unauthenticated Views

#### View: Registration
- **Path:** `/accounts/signup/`
- **Main Purpose:** Allow new users to create an account using email and password
- **Key Information:**
  - Email input field
  - Password input field
  - Confirm password input field
  - Link to login page
- **Key Components:**
  - Centered Bootstrap card (max-width 400px)
  - Form with `form-control` inputs
  - "Register" button (`btn-primary`)
  - Validation error display (`.is-invalid`, `.invalid-feedback`)
  - Link: "Already have an account? Log in"
- **UX Considerations:**
  - Clear error messages for validation failures (email exists, weak password, passwords don't match)
  - Focus on email field on page load
  - Client-side validation with HTML5 `required` and `type="email"`
- **Accessibility:**
  - Proper label-input associations
  - Error messages announced to screen readers
  - Keyboard navigation support
- **Security:**
  - CSRF token included in form
  - Password strength validation (server-side)
  - Email uniqueness check

---

#### View: Email Verification Pending
- **Path:** `/accounts/verify-email/`
- **Main Purpose:** Inform user to check email for verification link after registration
- **Key Information:**
  - Confirmation message with user's email address
  - Instructions to check email
  - Option to resend verification email
- **Key Components:**
  - Centered Bootstrap card (max-width 500px)
  - Heading: "Verify Your Email"
  - Informational text with user's email address highlighted
  - "Resend Verification Email" button (`btn-secondary`)
  - Link: "Back to Login"
- **UX Considerations:**
  - Friendly, encouraging tone
  - Clear next steps
  - Resend button shows loading state while processing
- **Accessibility:**
  - Clear heading hierarchy
  - Button purposes clearly labeled
- **Security:**
  - Rate limiting on resend to prevent abuse

---

#### View: Email Verification Confirm
- **Path:** `/accounts/confirm-email/<key>/`
- **Main Purpose:** Activate user account when they click verification link from email
- **Key Information:**
  - Success or error status
  - Next steps (login or request new link)
- **Key Components:**
  - **Success State:**
    - Centered card with success icon
    - Heading: "Email Verified"
    - Text: "Your account is now active."
    - "Go to Login" button (`btn-primary`)
  - **Error State:**
    - Centered card with error icon
    - Heading: "Verification Failed"
    - Text: "This link is invalid or has expired."
    - "Request New Link" button (`btn-primary`)
- **UX Considerations:**
  - Automatic verification on page load
  - Clear distinction between success and error states
  - Immediate call-to-action
- **Accessibility:**
  - Status communicated via heading and text
  - Color not the only indicator (icons + text)
- **Security:**
  - Verification links expire after reasonable time period
  - Invalid/expired links show appropriate error

---

#### View: Login
- **Path:** `/accounts/login/`
- **Main Purpose:** Allow registered users with verified email to authenticate and access their flashcards
- **Key Information:**
  - Email input field
  - Password input field
  - Links to registration and password reset
- **Key Components:**
  - Centered Bootstrap card (max-width 400px)
  - Form with `form-control` inputs
  - "Log In" button (`btn-primary`)
  - Link: "Forgot password?"
  - Link: "Don't have an account? Sign up"
  - Error alert for invalid credentials or unverified email
- **UX Considerations:**
  - Clear error messages: "Invalid email or password" or "Please verify your email address before logging in"
  - Focus on email field on page load
  - Password field with toggle visibility option (optional)
- **Accessibility:**
  - Labels associated with inputs
  - Error messages in ARIA live region
  - Keyboard accessible
- **Security:**
  - CSRF token in form
  - Session created on successful login
  - Unverified users cannot log in

---

#### View: Password Reset Request
- **Path:** `/accounts/password/reset/`
- **Main Purpose:** Allow users who forgot password to request a reset link via email
- **Key Information:**
  - Email input field
  - Instructions
- **Key Components:**
  - Centered Bootstrap card (max-width 400px)
  - Heading: "Reset Password"
  - Instructional text: "Enter your email and we'll send you a reset link."
  - Email input field
  - "Send Reset Link" button (`btn-primary`)
  - Link: "Back to Login"
- **UX Considerations:**
  - Confirmation message shows regardless of email existence (security best practice)
  - Clear next steps after submission
- **Accessibility:**
  - Clear instructions
  - Label for email field
- **Security:**
  - Same confirmation message whether email exists or not
  - Rate limiting to prevent enumeration attacks
  - CSRF token in form

---

#### View: Password Reset Confirm
- **Path:** `/accounts/password/reset/key/<key>/`
- **Main Purpose:** Allow users to set a new password via the reset link from email
- **Key Information:**
  - New password input field
  - Confirm password input field
- **Key Components:**
  - Centered Bootstrap card (max-width 400px)
  - Heading: "Set New Password"
  - Form with two password fields
  - "Reset Password" button (`btn-primary`)
  - Validation errors displayed inline
- **UX Considerations:**
  - Password strength indicator (optional)
  - Clear validation: passwords must match, meet strength requirements
  - Success redirect to login with message
- **Accessibility:**
  - Labels for password fields
  - Validation errors announced
- **Security:**
  - Reset links expire after reasonable time
  - Password strength validation
  - Invalid/expired links show error with "Request New Link" option
  - CSRF token in form

---

### 2.2 Authenticated Views

#### View: My Flashcards (List)
- **Path:** `/flashcards/`
- **Main Purpose:** Browse all user's flashcards with pagination, edit and delete capabilities
- **Key Information:**
  - Paginated list of flashcards (25 per page)
  - Flashcard front text (truncated to ~100 characters)
  - Edit and Delete buttons per card
  - Total count (implicit in pagination)
  - Call-to-action buttons for creating/generating flashcards
- **Key Components:**
  - **Fixed-top navbar** with navigation links
  - **Messages container** (`#messages`) at top of main content for success/error alerts
  - **Page heading:** "My Flashcards"
  - **Action buttons row:**
    - "Generate with AI" button
    - "Create Manually" button
  - **Flashcard list**
    - Each item (`list-group-item`) with `d-flex justify-content-between`:
      - Flashcard front text (class: `flashcard-front` with `text-overflow: ellipsis`)
      - Button group:
        - "Edit" button (`btn-sm btn-outline-primary`)
        - "Delete" button (`btn-sm btn-outline-danger`)
  - **Pagination controls** at bottom (Bootstrap pagination):
    - "Previous" button
    - Page numbers (current ± 2 pages)
    - "Next" button
  - **Empty state** (when no flashcards):
    - Centered Bootstrap card
    - Icon/illustration (optional)
    - Message: "You don't have any flashcards yet"
    - "Generate with AI" button (`btn-primary`)
    - "Create Manually" button (`btn-secondary`)
- **UX Considerations:**
  - Front text truncation with ellipsis for long content
  - Edit/Delete buttons always visible (not hidden on mobile)
  - Empty state provides clear next actions
  - Pagination shows current page and nearby pages
  - Success messages auto-dismiss after 5 seconds
- **Accessibility:**
  - Proper heading hierarchy (h1 for page title)
  - Button labels are descriptive
  - List semantics with `list-group`
  - Pagination accessible via keyboard
- **Security:**
  - Only user's own flashcards visible (filtered by `user=request.user`)
  - Edit/Delete actions verify ownership
- **Responsive:**
  - Mobile (< 768px): Buttons reduced to `btn-sm`, front text truncation adjusted
  - Desktop: Full layout with more visible page numbers
- **HTMX Integration:**
  - Pagination links: `hx-get="/api/flashcards?page=X&page_size=25" hx-target="#flashcard-list" hx-swap="outerHTML"`
  - Delete button: Opens confirmation modal, modal's delete button uses `hx-delete="/api/flashcards/{id}"`

---

#### View: Create Flashcard
- **Path:** `/flashcards/create/`
- **Main Purpose:** Allow users to manually create a single flashcard
- **Key Information:**
  - Front text input (empty by default)
  - Back text input (empty by default)
- **Key Components:**
  - Fixed-top navbar
  - Messages container
  - Page heading: "Create Flashcard"
  - **Form** with Bootstrap `form-control`:
    - **Front field:**
      - Label: "Front"
      - Textarea (rows=3, maxlength=200, required)
    - **Back field:**
      - Label: "Back"
      - Textarea (rows=5, maxlength=500, required)
    - **Button group:**
      - "Save" button (`btn-primary`)
      - "Cancel" button (`btn-secondary`)
  - Validation errors displayed below fields (`.invalid-feedback`)
- **UX Considerations:**
  - Clear labels for fields
  - Save button validates before submission
  - Cancel returns to My Flashcards without saving
  - Success message shown after save
  - Automatic redirect to My Flashcards after save
- **Accessibility:**
  - Labels properly associated with textareas
  - Required fields indicated
  - Validation errors announced to screen readers
  - Keyboard navigation support
- **Security:**
  - CSRF token included in form via `hx-headers`
  - Server-side validation of field lengths
  - User association on backend
- **Responsive:**
  - Container max-width ~800px
  - Full-width inputs on mobile
- **HTMX Integration:**
  - Form: `hx-post="/api/flashcards" hx-swap="outerHTML"`
  - On success: Redirect to My Flashcards with success message (via `HX-Redirect` header or server redirect)
  - On validation error: Swap form with error messages displayed
  - Cancel button: Navigate to `/flashcards/`
- **Validation:**
  - Client-side: HTML5 `required`, `maxlength`
  - Server-side: Non-empty, max length (front: 200, back: 500)
  - Error messages: "Front is required", "Back is required", "Front must be 200 characters or less"

---

#### View: Edit Flashcard
- **Path:** `/flashcards/{id}/edit/`
- **Main Purpose:** Allow users to modify existing flashcard front and back text
- **Key Information:**
  - Front text input (pre-filled with current value)
  - Back text input (pre-filled with current value)
  - Flashcard ID (hidden)
- **Key Components:**
  - Fixed-top navbar
  - Messages container
  - Page heading: "Edit Flashcard"
  - **Form** with Bootstrap `form-control`:
    - **Front field:**
      - Label: "Front"
      - Textarea (rows=3, maxlength=200, required, pre-filled)
    - **Back field:**
      - Label: "Back"
      - Textarea (rows=5, maxlength=500, required, pre-filled)
    - **Button group:**
      - "Save" button (`btn-primary`)
      - "Cancel" button (`btn-secondary`)
  - Validation errors displayed below fields
- **UX Considerations:**
  - Form pre-filled with current flashcard data
  - Save validates and updates flashcard
  - Cancel returns to My Flashcards without changes
  - Success message shown after save
  - Automatic redirect to My Flashcards after save
  - If flashcard was `ai_full` and user edits, `creation_method` changes to `ai_edited`
- **Accessibility:**
  - Same as Create Flashcard view
  - Pre-filled values don't interfere with screen readers
- **Security:**
  - Verify flashcard belongs to authenticated user
  - CSRF token included
  - Server-side validation
- **Responsive:**
  - Same as Create Flashcard view
- **HTMX Integration:**
  - Edit button from My Flashcards: `hx-get="/flashcards/{id}/edit" hx-target="main" hx-swap="innerHTML"`
  - Form: `hx-put="/api/flashcards/{id}" hx-swap="outerHTML"`
  - On success: Return to My Flashcards with success message
  - On validation error: Swap form with error messages
  - Cancel button: Navigate to `/flashcards/`
- **API Interactions:**
  - Load: GET `/api/flashcards/{id}/` to retrieve current data
  - Save: PUT `/api/flashcards/{id}/` with `{front, back}`
  - Server may update `creation_method` from `ai_full` to `ai_edited`

---

#### View: Generate Flashcards (Input Phase)
- **Path:** `/flashcards/generate/`
- **Main Purpose:** Accept text input from user for AI-powered flashcard generation
- **Key Information:**
  - Large text input area (up to 10,000 characters)
  - Instructions for users
- **Key Components:**
  - Fixed-top navbar
  - Messages container
  - Page heading: "Generate Flashcards with AI"
  - Instructional text: "Paste your study material below and we'll generate flashcards for you."
  - **Form:**
    - Large textarea:
      - Rows: 15
      - Placeholder: "Paste your text here..."
      - No visible character counter (validation server-side only)
      - No maxlength attribute (allows typing, validated server-side)
    - "Generate" button (`btn-primary btn-lg`)
  - **Loading indicator** (hidden by default, shown via `hx-indicator`):
    - Bootstrap spinner overlay (fixed position, centered)
    - Text: "Generating flashcards... This may take up to 30 seconds."
- **UX Considerations:**
  - Large, comfortable textarea for pasting text
  - No character counter visible (PRD requirement)
  - Clear instructions
  - Loading state with message sets expectations (up to 30s)
  - Generate button disabled during request
  - On error: Input text preserved, error message displayed
  - User can retry after error
- **Accessibility:**
  - Textarea labeled clearly
  - Loading state announced to screen readers
  - Error messages in ARIA live region
- **Security:**
  - CSRF token via `hx-headers`
  - Server-side validation of input length
  - User association on backend
- **Responsive:**
  - Container max-width ~1000px
  - Textarea adjusts height on mobile (may auto-expand or scroll)
- **HTMX Integration:**
  - Form: `hx-post="/api/generations" hx-indicator="#loading-spinner" hx-target="main" hx-swap="innerHTML"`
  - On success: Swap entire main content to Review Phase
  - On error: Swap to show error alert (`alert-danger`) while preserving input text in form
  - Generate button: `hx-disabled-elt="this"` to disable during request
- **API Interactions:**
  - POST `/api/generations/` with `{input_text: "..."}`
  - Response (success): `{session_id, generated_count, generated_flashcards: [{front, back}, ...]}`
  - Response (error 500): `{error: "generation_failed", message: "Couldn't generate flashcards right now. Please try again.", session_id}`
- **Error Handling:**
  - Input too long (>10,000 chars): "Input text is too long (maximum 10,000 characters)"
  - Empty input: "Please enter some text to generate flashcards"
  - API failure: "Couldn't generate flashcards right now. Please try again."
  - Input text preserved in all error cases

---

#### View: Generate Flashcards (Review Phase)
- **Path:** Same as Input Phase (content swapped via HTMX)
- **Main Purpose:** Allow users to review AI-generated flashcards, edit them, and decide which to accept or reject
- **Key Information:**
  - List of 5-10 generated flashcards
  - Each card: front text, back text (both editable)
  - Session ID (hidden, for tracking)
- **Key Components:**
  - Fixed-top navbar
  - Messages container
  - Page heading: "Review Generated Flashcards"
  - Instructional text: "Review each flashcard. You can edit the text before accepting."
  - **Stack of flashcard cards** (Bootstrap `card`, stacked vertically):
    - Each card has:
      - **Card body:**
        - "Front" label
        - Editable front text (textarea with rows=2, or contenteditable div)
        - "Back" label
        - Editable back text (textarea with rows=3, or contenteditable div)
        - Hidden inputs for original front/back (for edit detection)
      - **Card footer:**
        - "Accept" button (`btn-success`)
        - "Reject" button (`btn-danger`)
  - Hidden input: `session_id` from generation response
- **UX Considerations:**
  - All cards visible on one page (no pagination)
  - Users can edit text directly before accepting
  - Accept immediately saves flashcard and removes from review
  - Reject immediately removes card (no API call)
  - Visual feedback when card accepted/rejected (card removed with animation)
  - After all cards processed, user navigates away via navbar (no auto-redirect)
  - Edit detection: JavaScript compares current vs original text
- **Accessibility:**
  - Clear labels for "Front" and "Back"
  - Button purposes clear ("Accept", "Reject")
  - Editable areas keyboard accessible
  - Card removal announced to screen readers
- **Security:**
  - CSRF token via `hx-headers`
  - Session ID validated on backend
  - User association verified
- **Responsive:**
  - Cards stack vertically on all screen sizes
  - On mobile: Buttons reduced to `btn-sm`
  - Textarea/contenteditable adjusts width
- **HTMX Integration:**
  - **Accept button:**
    - JavaScript detects if text was edited (compare to original)
    - `hx-post="/api/flashcards"`
    - `hx-vals` includes: `{front, back, creation_method: "ai_full" or "ai_edited", ai_session_id}`
    - `hx-target="#card-{index}"` (the specific card)
    - `hx-swap="outerHTML"` (remove card, optionally show brief confirmation)
    - On success: Card removed from DOM
  - **Reject button:**
    - Pure JavaScript: Remove card from DOM (no API call)
    - Optional: Brief animation before removal
- **Edit Detection Logic:**
  - On page load: Store original front/back for each card in data attributes or hidden inputs
  - On Accept click: JavaScript compares current textarea value vs original
  - If different: Set `creation_method = "ai_edited"`
  - If unchanged: Set `creation_method = "ai_full"`
- **API Interactions:**
  - Accept: POST `/api/flashcards/` with `{front, back, creation_method, ai_session_id}`
  - Reject: No API call (client-side removal only)

---

#### View: Delete Confirmation Modal
- **Path:** Not a separate page; modal triggered by Delete button
- **Main Purpose:** Confirm user's intention to permanently delete a flashcard
- **Key Information:**
  - Warning message
  - Flashcard to be deleted (context from triggering button)
- **Key Components:**
  - **Bootstrap modal** (triggered by Delete button from My Flashcards):
    - **Modal header:** "Delete Flashcard"
    - **Modal body:** "Delete this flashcard? This cannot be undone."
    - **Modal footer:**
      - "Cancel" button (`btn-secondary`, `data-bs-dismiss="modal"`)
      - "Delete" button (`btn-danger`)
- **UX Considerations:**
  - Clear warning about permanent deletion
  - Cancel button easily accessible
  - Modal focus on open (keyboard trap)
  - Escape key closes modal without deleting
  - On delete: Modal closes, card removed from list
- **Accessibility:**
  - Modal proper ARIA attributes (role="dialog")
  - Focus management (trapped in modal, returns to trigger on close)
  - Warning clearly stated
- **Security:**
  - Actual deletion verified on backend (user owns flashcard)
  - CSRF token in delete request
- **HTMX Integration:**
  - Delete button in My Flashcards: Opens modal (Bootstrap JS or HTMX)
  - Delete button in modal: `hx-delete="/api/flashcards/{id}" hx-target="#flashcard-{id}" hx-swap="outerHTML"`
  - On success: Card removed from list, modal closes automatically
  - On error: Show error message in modal or as alert

---

### 2.3 Navigation Structure

#### Authenticated Navbar (Fixed-top)
```
[Brand: 10xCards] | [My Flashcards] [Generate Flashcards] [Create Flashcard] | [Logout]
```

- **Brand/Logo:** Left-aligned, links to My Flashcards
- **Main Navigation (center):**
  - "My Flashcards" - `/flashcards/`
  - "Generate Flashcards" - `/flashcards/generate/`
  - "Create Flashcard" - `/flashcards/create/`
- **User Controls (right):**
  - "Logout" link - POST to `/accounts/logout/`

**Active State:**
- Current view highlighted with Bootstrap `active` class
- Determined by Django template conditional based on `request.resolver_match.url_name`

**Mobile Navbar (< 768px):**
```
[Brand: 10xCards] [☰ Hamburger Menu]
```
When hamburger clicked, expands to show:
- My Flashcards
- Generate Flashcards
- Create Flashcard
- Logout

**Implementation:**
- Bootstrap navbar component with `navbar-expand-md`
- Collapse behavior for mobile
- Active state managed via Django template logic

---

## 3. User Journey Map

### 3.1 Primary Journey: New User - AI Generation Flow

1. **Registration**
   - User visits site → Redirected to Login
   - Clicks "Sign up" → Registration View
   - Fills email, password, confirms password → Submits
   - **Transition:** Redirect to Email Verification Pending

2. **Email Verification**
   - Email Verification Pending View shows instructions
   - User checks email inbox
   - Clicks verification link in email
   - **Transition:** Email Verification Confirm View → Success state
   - Clicks "Go to Login"
   - **Transition:** Navigate to Login View

3. **First Login**
   - Enters email and password → Submits
   - **Transition:** Session created, redirect to My Flashcards (empty state)

4. **Empty State → AI Generation**
   - My Flashcards View shows empty state card
   - User clicks "Generate with AI"
   - **Transition:** Navigate to Generate Flashcards (Input Phase)

5. **AI Generation**
   - User pastes study material into textarea
   - Clicks "Generate" button
   - **Loading:** Spinner shows "Generating flashcards... up to 30 seconds"
   - **Transition:** On success, swap to Review Phase

6. **Review AI-Generated Flashcards**
   - Review Phase shows 5-10 cards in stack
   - For each card:
     - User reviews front and back
     - Optionally edits text
     - Clicks "Accept" → Card saved, removed from review
     - OR clicks "Reject" → Card discarded, removed from review
   - **Transition:** After reviewing all cards, user clicks navbar link to My Flashcards

7. **View Accepted Flashcards**
   - My Flashcards View now shows accepted cards
   - Success message: "X flashcards added to your collection"
   - User can browse, paginate, edit, or delete cards

---

### 3.2 Secondary Journey: Returning User - Manual Creation

1. **Login**
   - User visits site → Login View
   - Enters credentials → Submits
   - **Transition:** Redirect to My Flashcards

2. **Manual Creation**
   - My Flashcards View shows existing cards
   - User clicks "Create Manually"
   - **Transition:** Navigate to Create Flashcard View

3. **Create Flashcard**
   - User fills front and back fields
   - Clicks "Save"
   - **Validation:** Server validates
   - **Transition:** On success, redirect to My Flashcards with success message

4. **View New Flashcard**
   - My Flashcards View shows new card at top of list
   - Success message: "Flashcard created successfully"

---

### 3.3 Flashcard Management Journey

1. **Edit Flashcard**
   - User in My Flashcards View
   - Clicks "Edit" on a card
   - **Transition:** Navigate to Edit Flashcard View (form pre-filled)
   - User modifies front or back
   - Clicks "Save"
   - **Validation:** Server validates
   - **Transition:** On success, redirect to My Flashcards with success message
   - Updated card visible in list

2. **Delete Flashcard**
   - User in My Flashcards View
   - Clicks "Delete" on a card
   - **Modal:** Delete Confirmation Modal appears
   - User clicks "Delete" in modal
   - **API Call:** DELETE request sent
   - **Transition:** On success, card removed from list, modal closes
   - List updates (if last card on page, adjust pagination)

---

### 3.4 Password Reset Journey

1. **Request Reset**
   - User at Login View
   - Clicks "Forgot password?"
   - **Transition:** Navigate to Password Reset Request View
   - Enters email → Submits
   - **Confirmation:** Message shown regardless of email existence

2. **Complete Reset**
   - User checks email
   - Clicks reset link
   - **Transition:** Password Reset Confirm View
   - Enters new password, confirms
   - Clicks "Reset Password"
   - **Validation:** Server validates
   - **Transition:** On success, redirect to Login with success message

3. **Login with New Password**
   - User enters email and new password
   - **Transition:** Login successful, redirect to My Flashcards

---

### 3.5 Error Recovery Journeys

1. **AI Generation Failure**
   - User in Generate Flashcards (Input Phase)
   - Clicks "Generate"
   - **Loading:** Spinner shows
   - **Error:** API fails (timeout, server error)
   - **Transition:** Error alert displayed, input text preserved
   - User can modify text and retry
   - OR navigate away via navbar

2. **Validation Error on Create/Edit**
   - User in Create or Edit Flashcard View
   - Leaves front or back empty, clicks "Save"
   - **Validation:** Server returns error
   - **Transition:** Form swapped with error messages below fields
   - User fills missing fields, clicks "Save" again
   - **Validation:** Success
   - **Transition:** Redirect to My Flashcards with success message

---

## 4. Layout and Navigation Structure

### 4.1 Page Layout Template Structure

All authenticated pages follow this base structure:

```
┌─────────────────────────────────────────────────┐
│ Fixed-top Navbar                                │
│ [Brand] | [Nav Links]           | [Logout]      │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ Messages Container (#messages)                  │
│ [Success/Error Alerts with auto-dismiss]        │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                                                 │
│ Main Content Area (container, mt-4)            │
│                                                 │
│ [Page-specific content]                         │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Unauthenticated pages:**
- No navbar
- Centered card layout on blank page
- Messages container (for errors)

**Authenticated pages:**
- Fixed-top navbar (always visible)
- Messages container (sticky at top of content)
- Main content in Bootstrap container

---

### 4.2 Navigation Patterns

**Between Views:**
- **Navbar links:** Direct navigation to core views
- **Action buttons:** Navigate to related views (e.g., "Generate with AI" → Generate View)
- **Form submissions:** Redirect to origin view with success message (Create/Edit → My Flashcards)
- **Cancel buttons:** Navigate back to origin view (usually My Flashcards)

**Within Views:**
- **Pagination:** HTMX loads new page content without full reload
- **Modals:** Overlay on current view, close returns to view
- **HTMX swaps:** Replace portions of page (form errors, review phase)

**Browser Navigation:**
- **Back button:** Should navigate to previous view (requires HTMX `hx-push-url` configuration)
- **Forward button:** Standard browser behavior
- **Direct URL access:** All views accessible via direct URL (with auth check)

---

### 4.3 Responsive Behavior

**Desktop (≥ 992px):**
- Full navbar with all links visible
- Wider containers (max-width ~1200px for My Flashcards)
- More page numbers visible in pagination
- Buttons standard size

**Tablet (768px - 991px):**
- Full navbar with all links visible
- Medium container widths
- Fewer page numbers in pagination
- Buttons standard size

**Mobile (< 768px):**
- Hamburger menu for navbar
- Full-width containers
- Minimal page numbers in pagination (current + adjacent)
- Buttons reduced to `btn-sm` in lists
- Textareas full-width
- Cards full-width

---

## 5. Key Components

### 5.1 Navbar Component (Authenticated)

**Purpose:** Provide consistent navigation across all authenticated views

**Structure:**
```html
<nav class="navbar navbar-expand-md navbar-light bg-light fixed-top">
  <div class="container">
    <a class="navbar-brand" href="/flashcards/">10xCards</a>
    <button class="navbar-toggler" ...>☰</button>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto">
        <li class="nav-item"><a class="nav-link" href="/flashcards/">My Flashcards</a></li>
        <li class="nav-item"><a class="nav-link" href="/flashcards/generate/">Generate Flashcards</a></li>
        <li class="nav-item"><a class="nav-link" href="/flashcards/create/">Create Flashcard</a></li>
      </ul>
      <ul class="navbar-nav">
        <li class="nav-item"><a class="nav-link" href="/accounts/logout/">Logout</a></li>
      </ul>
    </div>
  </div>
</nav>
```

**Active State Logic:**
```django
<a class="nav-link {% if request.resolver_match.url_name == 'flashcard_list' %}active{% endif %}" ...>
```

**Responsive:** Collapses to hamburger menu on mobile (< 768px)

---

### 5.2 Messages Component

**Purpose:** Display success, error, and info messages to users

**Structure:**
```html
<div id="messages" class="container mt-4">
  {% for message in messages %}
  <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
  {% endfor %}
</div>
```

**Behavior:**
- Auto-dismiss after 5 seconds (JavaScript)
- Manual close via X button
- Updated via HTMX out-of-band swaps (`hx-swap-oob="true"`)
- ARIA live region for screen reader announcements

**JavaScript (Auto-dismiss):**
```javascript
document.body.addEventListener('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'messages') {
    setTimeout(() => {
      const alerts = event.detail.target.querySelectorAll('.alert');
      alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      });
    }, 5000);
  }
});
```

---

### 5.3 Flashcard List Item Component

**Purpose:** Display individual flashcard in My Flashcards list

**Structure:**
```html
<li class="list-group-item d-flex justify-content-between align-items-center" id="flashcard-{{ flashcard.id }}">
  <span class="flashcard-front">{{ flashcard.front }}</span>
  <div>
    <a href="/flashcards/{{ flashcard.id }}/edit/" class="btn btn-sm btn-outline-primary">Edit</a>
    <button class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteModal-{{ flashcard.id }}">Delete</button>
  </div>
</li>
```

**CSS:**
```css
.flashcard-front {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 600px;
}
```

**Responsive:** On mobile, buttons become `btn-sm`, max-width adjusts

---

### 5.4 Pagination Component

**Purpose:** Navigate between pages of flashcards

**Structure:**
```html
<nav aria-label="Flashcard pagination">
  <ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
    <li class="page-item">
      <a class="page-link" href="?page={{ page_obj.previous_page_number }}"
         hx-get="/api/flashcards?page={{ page_obj.previous_page_number }}"
         hx-target="#flashcard-list" hx-swap="outerHTML">Previous</a>
    </li>
    {% endif %}

    {% for num in page_obj.paginator.page_range %}
      {% if num >= page_obj.number|add:'-2' and num <= page_obj.number|add:'2' %}
      <li class="page-item {% if num == page_obj.number %}active{% endif %}">
        <a class="page-link" href="?page={{ num }}"
           hx-get="/api/flashcards?page={{ num }}"
           hx-target="#flashcard-list" hx-swap="outerHTML">{{ num }}</a>
      </li>
      {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
    <li class="page-item">
      <a class="page-link" href="?page={{ page_obj.next_page_number }}"
         hx-get="/api/flashcards?page={{ page_obj.next_page_number }}"
         hx-target="#flashcard-list" hx-swap="outerHTML">Next</a>
    </li>
    {% endif %}
  </ul>
</nav>
```

**HTMX Behavior:**
- Clicking page link loads new page content without full reload
- Target: `#flashcard-list` (the list container)
- Swap: `outerHTML` (replace entire list including pagination)

**Responsive:** On mobile, show fewer page numbers (current ± 1)

---

### 5.5 Delete Modal Component

**Purpose:** Confirm flashcard deletion

**Structure:**
```html
<div class="modal fade" id="deleteModal-{{ flashcard.id }}" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Delete Flashcard</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        Delete this flashcard? This cannot be undone.
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-danger"
                hx-delete="/api/flashcards/{{ flashcard.id }}"
                hx-target="#flashcard-{{ flashcard.id }}"
                hx-swap="outerHTML"
                data-bs-dismiss="modal">Delete</button>
      </div>
    </div>
  </div>
</div>
```

**Behavior:**
- Triggered by Delete button in flashcard list
- Delete button in modal sends DELETE request
- On success: Flashcard removed from DOM, modal closes

---

### 5.6 Generated Flashcard Card Component (Review Phase)

**Purpose:** Display AI-generated flashcard for review with edit and accept/reject actions

**Structure:**
```html
<div class="card mb-3" id="generated-card-{{ forloop.counter }}" data-original-front="{{ card.front }}" data-original-back="{{ card.back }}">
  <div class="card-body">
    <label class="form-label">Front</label>
    <textarea class="form-control front-text" rows="2" maxlength="200">{{ card.front }}</textarea>

    <label class="form-label mt-2">Back</label>
    <textarea class="form-control back-text" rows="3" maxlength="500">{{ card.back }}</textarea>
  </div>
  <div class="card-footer d-flex justify-content-end gap-2">
    <button class="btn btn-success accept-btn"
            hx-post="/api/flashcards"
            hx-vals='js:{front: getCardValue("front"), back: getCardValue("back"), creation_method: detectEdit(), ai_session_id: {{ session_id }}}'
            hx-target="#generated-card-{{ forloop.counter }}"
            hx-swap="outerHTML">Accept</button>
    <button class="btn btn-danger reject-btn" onclick="removeCard(this)">Reject</button>
  </div>
</div>
```

**JavaScript (Edit Detection):**
```javascript
function detectEdit() {
  const card = event.target.closest('.card');
  const originalFront = card.dataset.originalFront;
  const originalBack = card.dataset.originalBack;
  const currentFront = card.querySelector('.front-text').value;
  const currentBack = card.querySelector('.back-text').value;

  return (currentFront !== originalFront || currentBack !== originalBack)
    ? 'ai_edited'
    : 'ai_full';
}

function removeCard(button) {
  button.closest('.card').remove();
}
```

---

### 5.7 Empty State Component

**Purpose:** Guide users when they have no flashcards

**Structure:**
```html
<div class="card text-center mt-5" style="max-width: 600px; margin: 0 auto;">
  <div class="card-body py-5">
    <h2 class="card-title mb-4">You don't have any flashcards yet</h2>
    <p class="card-text mb-4">Get started by generating flashcards from your study material or creating them manually.</p>
    <a href="/flashcards/generate/" class="btn btn-primary btn-lg me-2">Generate with AI</a>
    <a href="/flashcards/create/" class="btn btn-secondary btn-lg">Create Manually</a>
  </div>
</div>
```

**Displayed:** When user has zero flashcards in My Flashcards view

---

### 5.8 Loading Indicator Component (AI Generation)

**Purpose:** Show loading state during AI generation

**Structure:**
```html
<div id="loading-spinner" class="htmx-indicator">
  <div class="text-center">
    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-3">Generating flashcards... This may take up to 30 seconds.</p>
  </div>
</div>
```

**CSS:**
```css
.htmx-indicator {
  display: none;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1050;
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.htmx-request .htmx-indicator {
  display: block;
}
```

**HTMX:** Shown when `hx-indicator="#loading-spinner"` is triggered

---

### 5.9 Form Validation Error Component

**Purpose:** Display inline validation errors below form fields

**Structure:**
```html
<div class="mb-3">
  <label for="front" class="form-label">Front</label>
  <textarea class="form-control {% if errors.front %}is-invalid{% endif %}"
            id="front" name="front" rows="3" maxlength="200" required>{{ form.front.value }}</textarea>
  {% if errors.front %}
  <div class="invalid-feedback">
    {{ errors.front.0 }}
  </div>
  {% endif %}
</div>
```

**Bootstrap Classes:**
- `.is-invalid` on input for error state
- `.invalid-feedback` for error message below field

**Returned by:** Server on validation failure (400 Bad Request)

---

## 6. API Integration and State Management

### 6.1 HTMX-Driven Architecture

**Request Pattern:**
```
User Action → HTMX Request (with CSRF token) → Django View →
→ DRF API Logic → Render HTML Fragment → HTMX Swap → DOM Update
```

**Key Principles:**
- Server returns HTML fragments, not JSON
- No client-side state management (server is source of truth)
- HTMX handles request/response cycle and DOM updates
- Forms submit via HTMX, responses swap portions of page

**CSRF Token Handling:**
```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <!-- All HTMX requests automatically include CSRF token -->
</body>
```

### 6.2 API Endpoint Usage Mapping

| View | User Action | HTTP Method | Endpoint | HTMX Attributes | Response |
|------|-------------|-------------|----------|-----------------|----------|
| My Flashcards | Load page | GET | `/api/flashcards?page=1&page_size=25` | Initial load (server-rendered) | HTML list |
| My Flashcards | Click pagination | GET | `/api/flashcards?page=X` | `hx-get`, `hx-target="#flashcard-list"` | HTML list fragment |
| Create Flashcard | Submit form | POST | `/api/flashcards` | `hx-post`, `hx-swap="outerHTML"` | Redirect or form with errors |
| Edit Flashcard | Load form | GET | `/api/flashcards/{id}` | `hx-get`, `hx-target="main"` | HTML form fragment |
| Edit Flashcard | Submit form | PUT | `/api/flashcards/{id}` | `hx-put`, `hx-swap="outerHTML"` | Redirect or form with errors |
| Delete Flashcard | Confirm delete | DELETE | `/api/flashcards/{id}` | `hx-delete`, `hx-target="#flashcard-{id}"` | 204 No Content (remove card) |
| Generate (Input) | Submit text | POST | `/api/generations` | `hx-post`, `hx-indicator`, `hx-target="main"` | HTML review phase or error |
| Generate (Review) | Accept card | POST | `/api/flashcards` | `hx-post`, `hx-vals`, `hx-target="#card-{id}"` | 201 Created (remove card) |
| Generate (Review) | Reject card | N/A | N/A | JavaScript (no API call) | Card removed client-side |

### 6.3 Response Handling Patterns

**Success Responses:**
- **200 OK (GET):** Return HTML fragment for swap
- **201 Created (POST):** Return success indicator or redirect
- **204 No Content (DELETE):** HTMX removes target element
- **Redirect:** Use `HX-Redirect` header or server redirect

**Error Responses:**
- **400 Bad Request:** Return form fragment with `.is-invalid` classes and error messages
- **404 Not Found:** Return error message or redirect to My Flashcards
- **500 Internal Server Error:** Return user-friendly error message with preserved input

**Loading States:**
- Use `hx-indicator` attribute pointing to spinner element
- Disable submit buttons during request: `hx-disabled-elt="this"`
- Display context-appropriate loading messages

**Out-of-Band Swaps:**
- Use `hx-swap-oob="true"` on elements outside target to update multiple areas
- Example: Update `#messages` container while swapping main content

---

## 7. Responsiveness, Accessibility, and Security

### 7.1 Responsive Design

**Mobile-First Approach:**
- Designs start with mobile layout (< 768px)
- Enhanced for larger screens using Bootstrap breakpoints
- Breakpoints: xs (< 576px), sm (≥ 576px), md (≥ 768px), lg (≥ 992px), xl (≥ 1200px)

**Responsive Patterns:**
- **Navigation:** Hamburger menu on mobile, full navbar on desktop
- **Flashcard Cards:** Full-width stacking on all sizes, `btn-sm` on mobile
- **Forms:** Full-width inputs on mobile, constrained width (max-width 800px, centered) on desktop
- **Pagination:** Fewer visible page numbers on mobile (current ± 1 vs current ± 2)
- **Buttons:** Standard size on desktop, `btn-sm` in lists on mobile

**Bootstrap Utility Classes:**
- `d-none d-md-block` - Hide on mobile, show on desktop
- `col-12 col-md-8 col-lg-6` - Responsive column widths
- `flex-column flex-md-row` - Stack on mobile, row on desktop

### 7.2 Accessibility

**Semantic HTML:**
- Proper heading hierarchy (h1, h2, h3)
- Use `<nav>` for navigation
- Use `<main>` for main content
- Use `<form>` for forms

**ARIA Attributes:**
- `role="dialog"` on modals
- `aria-label` for navigation and buttons where needed
- `aria-live="polite"` for messages container (screen reader announcements)
- `role="status"` for loading indicators

**Keyboard Navigation:**
- All interactive elements keyboard accessible
- Modal focus trap (focus stays in modal)
- Logical tab order
- Enter/Space activate buttons

**Form Accessibility:**
- Labels associated with inputs via `for` attribute
- Required fields indicated with `required` attribute and asterisk (optional)
- Error messages associated with fields via `aria-describedby`
- Validation errors announced to screen readers

**Color Contrast:**
- Bootstrap default colors meet WCAG AA standards
- Error messages use color + icons (not color alone)
- Links underlined or clearly distinguished

**Screen Reader Support:**
- Descriptive button labels ("Edit flashcard", not just "Edit")
- Alt text for images (if any)
- Visually hidden text for context where needed (`.visually-hidden`)

### 7.3 Security

**Authentication & Authorization:**
- Session-based authentication via Django
- All API endpoints require authentication (401/403 for unauthorized)
- User isolation: `queryset.filter(user=request.user)` in all views
- Attempted access to other users' resources returns 404 (prevents enumeration)

**CSRF Protection:**
- Django CSRF middleware enabled
- CSRF token included in all POST/PUT/DELETE requests via `hx-headers` on `<body>`
- Token from `{{ csrf_token }}` template tag

**Input Validation:**
- **Client-side:** HTML5 `required` attributes, `maxlength`, `type="email"`
- **Server-side:** Django REST Framework serializers validate all inputs
- Field length limits enforced (front: 1-200 chars, back: 1-500 chars, input_text: max 10,000 chars)

**SQL Injection Prevention:**
- Django ORM used exclusively (no raw SQL queries)

**XSS Prevention:**
- Django templates auto-escape output by default
- User-generated content sanitized before rendering
- Bootstrap components don't execute inline scripts

**Email Verification:**
- Mandatory email verification before login (`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`)
- Verification links time-limited
- Unverified users cannot log in

**Password Security:**
- Argon2 password hashing (Django's primary hasher)
- Password strength requirements enforced during registration
- Secure password reset flow with time-limited tokens

**Session Security:**
- Secure session cookies (HTTPS only in production)
- Session timeout after inactivity
- Logout clears session securely

---

## 8. Edge Cases and Error States

### 8.1 Edge Cases

**Empty Flashcard List After Deletion:**
- If user deletes last card on a page:
  - Show "No flashcards on this page" message
  - Provide link to previous page or My Flashcards home
  - Keep pagination controls functional

**All Flashcards Rejected in Review:**
- User rejects all AI-generated cards in review phase
- State: Empty review area
- Action: Display message "All flashcards rejected. Generate new ones or return to My Flashcards."
- Provide "Back to My Flashcards" button or rely on navbar

**AI Generation Timeout:**
- Request takes >30 seconds (server timeout)
- Action: Show error message "Couldn't generate flashcards right now. Please try again."
- Input text preserved in form
- Allow user to retry

**Invalid/Expired Email Verification Link:**
- User clicks old or invalid verification link
- Action: Email Verification Confirm View shows error state
- Provide "Request New Link" button

**Concurrent Edits (Multiple Devices):**
- User edits same flashcard on two devices simultaneously
- Behavior: Last save wins (no conflict resolution in MVP)
- Note: Could cause confusion, but acceptable for MVP

**Browser Back Button During Review:**
- User in Review Phase, clicks browser back
- Decision: Requires HTMX `hx-push-url` configuration
- Recommendation: Enable URL history, back navigates to input phase

**Pagination State After Edit:**
- User on page 3 of My Flashcards, edits a card, saves
- Behavior: Return to page 1 (simplest implementation)
- Alternative: Preserve page number in session or query param

**Long Flashcard Text Exceeding Maxlength:**
- User pastes text exceeding maxlength in form
- Client-side: `maxlength` attribute prevents input (truncates on paste)
- Alternative: No `maxlength`, server validates and returns error

### 8.2 Error States

**Registration Errors:**
- Email already exists: "An account with this email already exists."
- Weak password: "Password must be at least 8 characters and include..."
- Passwords don't match: "Passwords do not match."

**Login Errors:**
- Invalid credentials: "Invalid email or password."
- Unverified email: "Please verify your email address before logging in."
- Account locked (if implemented): "Your account has been locked. Contact support."

**AI Generation Errors:**
- API failure: "Couldn't generate flashcards right now. Please try again."
- Input too long: "Input text is too long (maximum 10,000 characters)."
- Empty input: "Please enter some text to generate flashcards."

**Flashcard CRUD Errors:**
- Empty front field: "Front is required."
- Empty back field: "Back is required."
- Front too long: "Front must be 200 characters or less."
- Back too long: "Back must be 500 characters or less."
- Network error: "Something went wrong. Please try again."
- Not found (404): "Flashcard not found." (redirect to My Flashcards)

**Authentication Errors:**
- Session expired: Redirect to login with message "Your session has expired. Please log in again."
- CSRF token missing/invalid: "Security verification failed. Please refresh and try again."

---

## 9. User Story Mapping to UI Elements

| User Story | View(s) | UI Elements |
|------------|---------|-------------|
| US-001: Registration | Registration View | Email input, password input, confirm password input, Register button, validation errors, link to login |
| US-002: Email Verification | Email Verification Pending, Email Verification Confirm | Instructions, resend button, success/error messages, link to login |
| US-003: Login | Login View | Email input, password input, Login button, Forgot Password link, validation errors |
| US-004: Password Reset Request | Password Reset Request View | Email input, Send Reset Link button, confirmation message |
| US-005: Password Reset Completion | Password Reset Confirm View | New password input, confirm password input, Reset Password button, validation errors |
| US-006: AI Generation from Text | Generate Flashcards (Input) | Large textarea, Generate button, loading spinner, error handling |
| US-007: Review AI-Generated | Generate Flashcards (Review) | Stack of cards, editable front/back per card, Accept/Reject buttons per card |
| US-009: Manual Creation | Create Flashcard View | Front textarea, back textarea, Save/Cancel buttons, validation errors |
| US-010: My Flashcards | My Flashcards View | List of flashcards, truncated front text, Edit/Delete buttons, pagination, empty state |
| US-011: Edit Flashcard | Edit Flashcard View | Pre-filled front/back textareas, Save/Cancel buttons, validation errors |
| US-012: Delete Flashcard | Delete Confirmation Modal | Warning message, Delete/Cancel buttons, modal overlay |
| US-013: Study Session | (Deferred for MVP) | Not implemented |
| US-019: Logout | Navbar | Logout link/button, redirect to login |
| US-021: Security | All authenticated views | Authentication checks, user isolation, CSRF protection |

---

## 10. Implementation Priorities

### Phase 1: Core MVP (Authentication & Basic Flashcards)
1. Base template structure with navbar
2. Registration View
3. Email Verification Pending & Confirm Views
4. Login View
5. Password Reset Request & Confirm Views
6. My Flashcards View with pagination, edit, delete
7. Create Flashcard View
8. Edit Flashcard View
9. Delete Confirmation Modal
10. Logout functionality

### Phase 2: AI Generation
1. Generate Flashcards View (Input Phase)
2. API integration with OpenRouter
3. Generate Flashcards View (Review Phase)
4. Edit detection logic for ai_full vs ai_edited
5. Error handling for AI failures

### Phase 3: Polish & Refinement
1. Success message auto-dismiss functionality
2. Responsive refinements for mobile/tablet
3. Accessibility audit and fixes
4. Browser back button support (HTMX history)
5. Loading state improvements
6. Error message refinements

### Phase 4: Deferred (Future Enhancements)
1. Study Session functionality
2. Due card count badge in navbar
3. Advanced spaced repetition features
4. Analytics dashboards

---

## 11. Technical Implementation Notes

### 11.1 Django Template Structure

**Base Template (`base.html`):**
- Located at `flashcards/templates/base.html`
- Includes Bootstrap 5 CSS, HTMX script
- Body element with `hx-headers` for CSRF token
- Conditional navbar (authenticated users only)
- Messages container (`#messages`)
- Content block for view-specific content

**Partial Templates:**
- `_flashcard_list.html` - Flashcard list fragment for HTMX swapping
- `_flashcard_card.html` - Individual flashcard list item
- `_pagination.html` - Pagination controls
- `_messages.html` - Success/error alerts
- `_generated_card.html` - AI-generated flashcard in review interface
- `_delete_modal.html` - Delete confirmation modal
- `_navbar.html` - Navigation bar

### 11.2 Django View Architecture

**View Pattern for HTMX Support:**
```python
class FlashcardListView(LoginRequiredMixin, ListView):
    model = Flashcard
    template_name = 'flashcards/list.html'  # Full page
    partial_template_name = 'flashcards/_flashcard_list.html'  # HTMX fragment
    paginate_by = 25

    def get_queryset(self):
        return Flashcard.objects.filter(user=self.request.user).order_by('-created_at')

    def get_template_names(self):
        # Return partial template for HTMX requests, full template for regular requests
        return [self.partial_template_name] if self.request.htmx else [self.template_name]
```

**HTMX Request Detection:**
- Use `django-htmx` package for `request.htmx` detection
- Or check header: `request.headers.get('HX-Request')`

### 11.3 HTMX Configuration

**Global Event Listeners (JavaScript):**
```javascript
// Auto-dismiss success messages after 5 seconds
document.body.addEventListener('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'messages') {
    setTimeout(() => {
      const alerts = event.detail.target.querySelectorAll('.alert');
      alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      });
    }, 5000);
  }
});
```

**Edit Detection for AI Review (JavaScript):**
```javascript
function detectEditAndSubmit(button, sessionId) {
  const card = button.closest('.card');
  const originalFront = card.dataset.originalFront;
  const originalBack = card.dataset.originalBack;
  const currentFront = card.querySelector('.front-text').value;
  const currentBack = card.querySelector('.back-text').value;

  const creationMethod = (currentFront !== originalFront || currentBack !== originalBack)
    ? 'ai_edited'
    : 'ai_full';

  // Set values for HTMX request
  card.querySelector('.accept-btn').setAttribute('hx-vals', JSON.stringify({
    front: currentFront,
    back: currentBack,
    creation_method: creationMethod,
    ai_session_id: sessionId
  }));
}
```

### 11.4 Bootstrap Customization

**Custom CSS (Minimal):**
```css
/* Truncate flashcard front text in list */
.flashcard-front {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 600px;
}

@media (max-width: 767px) {
  .flashcard-front {
    max-width: 250px;
  }
}

/* Loading spinner overlay */
.htmx-indicator {
  display: none;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1050;
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.htmx-request .htmx-indicator {
  display: block;
}

/* Ensure navbar doesn't overlap content */
body {
  padding-top: 56px; /* Height of fixed navbar */
}
```

---

## 12. Unresolved Design Decisions

### Areas Requiring Clarification Before Implementation

1. **AI Generation Review - After All Actions:**
   - When user has accepted/rejected all generated flashcards, should there be an explicit "Back to My Flashcards" button?
   - Or rely solely on navbar navigation?
   - Or auto-redirect to My Flashcards after last card processed?
   - **Recommendation:** Provide "Back to My Flashcards" button at bottom of review area for clarity.

2. **Pagination State Preservation After Edit:**
   - User edits flashcard from page 3, returns to My Flashcards
   - Should they return to page 3 or page 1?
   - **Recommendation:** Return to page 1 for MVP simplicity. Consider session/query param preservation in future.

3. **Character Limit Enforcement in UI:**
   - Should HTML `maxlength` attribute be used on textareas (front: 200, back: 500)?
   - Or allow unlimited typing and show server validation error?
   - **Recommendation:** Use `maxlength` for better UX (prevents over-typing), plus server validation as backup.

4. **AI Generation Textarea on Mobile:**
   - Should textarea auto-expand as user types?
   - Or maintain fixed height with scrolling?
   - **Recommendation:** Fixed height (rows=15) with scrolling for simplicity.

5. **Logout Confirmation:**
   - Should logout require confirmation modal?
   - Or immediate logout on click?
   - **Recommendation:** Immediate logout for simplicity. Most users expect this behavior.

6. **Empty Page After Deletion:**
   - User deletes last flashcard on page 3
   - Show empty state or redirect to previous page?
   - **Recommendation:** Redirect to previous page if current page becomes empty.

7. **Browser Back Button Support:**
   - Enable HTMX history with `hx-push-url`?
   - Or let back button reload full page?
   - **Recommendation:** Enable `hx-push-url` for better UX, especially in Generate and Edit flows.

8. **Study Session Placeholder:**
   - Should navbar include disabled/placeholder "Study Session" link for future?
   - Or add it later when implementing?
   - **Recommendation:** Add later to avoid confusion in MVP.

---

## Appendix: User Pain Points & UI Solutions

| User Pain Point | UI Solution | How It Helps |
|----------------|-------------|--------------|
| Flashcard creation is time-consuming | Prominent "Generate with AI" button, large text input, quick review process | Makes AI generation the primary path, reduces manual effort |
| Users don't know where to start (empty state) | Empty state with clear CTAs and friendly message | Guides users to either generate or create flashcards immediately |
| AI-generated cards may need editing | Editable text in review phase before accepting | Users can refine cards without extra steps or navigation |
| Users may accidentally delete cards | Confirmation modal with clear warning message | Prevents accidental deletions, gives users chance to cancel |
| Long text input is tedious on mobile | Large textarea, mobile-optimized layout | Makes text input comfortable on all devices |
| Users lose work when errors occur | Input preservation on AI generation failure | Users don't have to re-enter text after errors |
| Users don't know what went wrong | Clear, user-friendly error messages in plain language | Explains errors simply, suggests corrective actions |
| Pagination is confusing | Standard Bootstrap pagination with clear Previous/Next controls | Familiar pattern, easy navigation between pages |
| Users don't know if actions succeeded | Success messages with auto-dismiss, immediate UI updates | Clear feedback confirms actions completed successfully |
| Complex navigation is overwhelming | Minimalist navigation with only 3 core links | Reduces cognitive load, focuses on core tasks |
