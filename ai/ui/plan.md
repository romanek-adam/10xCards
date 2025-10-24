# UI Architecture for 10xCards

## 1. UI Structure Overview

10xCards implements a minimalist, student-focused flashcard application using a server-rendered architecture with HTMX for dynamic interactions and Bootstrap 5 for styling. The UI consists of three core authenticated views (My Flashcards, Generate Flashcards, Create Flashcard) plus supporting authentication flows. The architecture prioritizes simplicity, mobile-first responsiveness, and progressive enhancement, with all dynamic interactions handled through HTMX-driven HTML fragment updates rather than client-side state management.

## 2. View List

### 2.1 Registration Page

**Path:** `/accounts/signup/`
**Main Purpose:** Allow new students to create an account with email and password.
**Key Information:** Email field, password field, password confirmation, registration button.
**Key Components:** Centered Bootstrap card with form, validation error messages, link to login page.
**UX:** Clear field labels, inline validation feedback, disabled submit during processing.
**Accessibility:** Proper form labels, ARIA attributes for error messages, keyboard navigation.
**Security:** CSRF token, server-side validation via django-allauth, Argon2 password hashing.

### 2.2 Email Verification Pending Page

**Path:** `/accounts/confirm-email/`
**Main Purpose:** Inform users to check their email for verification link after registration.
**Key Information:** Instructional message, resend verification email button, user's email address.
**Key Components:** Centered Bootstrap card with clear instructions and action button.
**UX:** Friendly tone, clear call-to-action, option to resend if not received.
**Accessibility:** Semantic heading structure, clear action button labels.
**Security:** Only accessible immediately after registration, session-based.

### 2.3 Email Verification Success Page

**Path:** `/accounts/confirm-email/<key>/`
**Main Purpose:** Confirm successful email verification and direct users to login.
**Key Information:** Success message, link to login page.
**Key Components:** Centered Bootstrap card with success alert and login button.
**UX:** Positive feedback, clear next step (login).
**Accessibility:** Success message announced to screen readers.
**Security:** Verification token validated server-side, time-limited link.

### 2.4 Login Page

**Path:** `/accounts/login/`
**Main Purpose:** Authenticate existing users with verified email addresses.
**Key Information:** Email field, password field, login button, forgot password link.
**Key Components:** Centered Bootstrap card with form, validation messages, link to registration.
**UX:** Clear error messages for invalid credentials or unverified email, remember me option.
**Accessibility:** Proper labels, error association with fields, focus management.
**Security:** Session creation on success, CSRF protection, rate limiting on failed attempts.

### 2.5 Password Reset Request Page

**Path:** `/accounts/password/reset/`
**Main Purpose:** Allow users to request password reset email.
**Key Information:** Email field, submit button.
**Key Components:** Centered Bootstrap card with single-field form, confirmation message.
**UX:** Same confirmation shown whether email exists or not (security best practice).
**Accessibility:** Clear instructions, form label association.
**Security:** Time-limited reset tokens, generic confirmation to prevent email enumeration.

### 2.6 Password Reset Confirm Page

**Path:** `/accounts/password/reset/key/<uidb64>/<token>/`
**Main Purpose:** Allow users to set new password via reset link.
**Key Information:** New password field, confirm password field, submit button.
**Key Components:** Centered Bootstrap card with form, password strength indicator, validation messages.
**UX:** Password match validation, clear error messages, success redirect to login.
**Accessibility:** Password requirements announced, validation errors associated with fields.
**Security:** Token validation, password strength enforcement, one-time use tokens.

### 2.7 My Flashcards Page

**Path:** `/flashcards/` (default authenticated landing page)
**Main Purpose:** Display paginated list of all user's flashcards with management actions.
**Key Information:** Flashcard list (front text truncated to ~100 chars), edit/delete buttons per card, pagination controls, total count.
**Key Components:** Bootstrap list-group for cards, CTA button group (Generate/Create), pagination component, delete confirmation modal, success/error alerts.
**UX:** Empty state with friendly message and prominent CTAs, newest-first sorting, visual feedback on delete, loading states for HTMX requests.
**Accessibility:** Semantic list structure, button labels, keyboard navigation, modal focus trap.
**Security:** User-isolated queryset, CSRF protection on delete, 404 for unauthorized access.

### 2.8 Create Flashcard Page

**Path:** `/flashcards/create/`
**Main Purpose:** Manually create a single flashcard with front and back text.
**Key Information:** Front text input, back text input, save/cancel buttons.
**Key Components:** Bootstrap form with two form-groups, validation feedback, success message on save.
**UX:** Clear labels, required field indicators, explicit save/cancel actions, redirect to My Flashcards on success.
**Accessibility:** Form labels, validation error association, focus management.
**Security:** Server-side validation (1-200 chars front, 1-500 chars back), user association, CSRF token.

### 2.9 Edit Flashcard Page

**Path:** `/flashcards/<id>/edit/`
**Main Purpose:** Modify existing flashcard front and back text.
**Key Information:** Front text input (pre-filled), back text input (pre-filled), save/cancel buttons.
**Key Components:** Bootstrap form with pre-populated fields, validation feedback, success message on save.
**UX:** Clear indication of edit mode, discard changes on cancel, redirect to My Flashcards on success, creation_method updated to ai_edited if originally ai_full.
**Accessibility:** Same as Create, with clear indication of pre-filled values.
**Security:** Verify flashcard ownership (404 if not owner), CSRF protection, validation.

### 2.10 Generate Flashcards (Input) Page

**Path:** `/flashcards/generate/`
**Main Purpose:** Accept text input for AI-powered flashcard generation.
**Key Information:** Large textarea for input text (max 10,000 chars), generate button.
**Key Components:** Bootstrap form with large textarea (15+ rows), loading spinner overlay, error alert with input preservation.
**UX:** No character counter (server-side validation only), loading message "Generating flashcards... This may take up to 30 seconds", disabled button during processing, input preserved on failure.
**Accessibility:** Textarea label, loading state announced, error messages.
**Security:** Server-side text length validation, rate limiting on API calls, CSRF protection.

### 2.11 Generate Flashcards (Review) Page

**Path:** `/flashcards/generate/review/<session_id>/`
**Main Purpose:** Review AI-generated flashcards and accept/reject each one.
**Key Information:** Stack of 5-10 generated flashcards with editable front/back, accept/reject buttons per card.
**Key Components:** Vertical stack of Bootstrap cards, each with textarea/contenteditable front/back, button group (Accept: success, Reject: danger), visual feedback on actions.
**UX:** All cards displayed simultaneously, inline editing capability, accept saves to database (with creation_method: ai_full or ai_edited based on edits), reject removes from DOM, return to My Flashcards via navbar after review.
**Accessibility:** Card structure semantic, edit fields labeled, button actions clear.
**Security:** Session ownership validation, CSRF on accept POST, XSS prevention via Django template escaping.

### 2.12 Study Session Page (Future/Deferred)

**Path:** `/study/` (not implemented in initial MVP)
**Main Purpose:** Practice flashcards using spaced repetition algorithm.
**Key Information:** Current flashcard (front/back), rating buttons, session progress, remaining cards count.
**Key Components:** Card display with flip interaction, rating buttons, progress indicator, session complete message.
**UX:** One card at a time, front shown first, user action reveals back, rating determines next review date.
**Accessibility:** Flip interaction keyboard-accessible, progress announced.
**Security:** User-isolated flashcard selection, session state management.

## 3. User Journey Map

### Primary Journey: Student Generates Flashcards with AI

1. **Account Setup (First-Time User)**
   - Visit site → Registration Page → Enter email/password → Submit
   - Email Verification Pending Page → Check email → Click verification link
   - Email Verification Success Page → Click login link
   - Login Page → Enter credentials → Submit
   - Redirect to My Flashcards (empty state)

2. **AI Generation Flow**
   - My Flashcards (empty) → Click "Generate with AI" button
   - Generate Flashcards (Input) → Paste study material → Click "Generate"
   - Loading overlay (spinner, message, 30s timeout)
   - Generate Flashcards (Review) → 5-10 cards displayed
   - For each card: Review quality → Optional: Edit front/back → Click "Accept" OR "Reject"
   - Navigate to My Flashcards via navbar → See accepted flashcards in list

3. **Flashcard Management**
   - **Edit:** My Flashcards → Click "Edit" on card → Edit Flashcard Page → Modify text → Click "Save" → Success message → My Flashcards
   - **Delete:** My Flashcards → Click "Delete" on card → Confirmation modal → Click "Delete" → Card removed, list updates
   - **Pagination:** My Flashcards → Click page number/next → HTMX loads new page content

4. **Manual Creation (Alternative)**
   - My Flashcards → Click "Create Manually" → Create Flashcard Page
   - Enter front/back text → Click "Save" → Validation → Success message → My Flashcards

5. **Subsequent Sessions**
   - Login Page → Enter credentials → My Flashcards (with existing cards)
   - Navigate to Generate/Create via navbar as needed

### Secondary Journeys

**Password Reset:**
- Login Page → Click "Forgot Password" → Password Reset Request → Enter email → Submit
- Check email → Click reset link → Password Reset Confirm → Enter new password → Submit
- Success message → Login Page → Login with new password

**AI Generation Failure:**
- Generate Flashcards (Input) → Enter text → Click "Generate" → Loading
- API failure/timeout → Error alert: "Couldn't generate flashcards right now. Please try again."
- Input text preserved in textarea → Fix issue (if text too long) → Click "Generate" again

**Validation Errors:**
- Create/Edit Flashcard → Leave field(s) empty → Click "Save"
- Validation errors displayed below fields → Fill required fields → Click "Save" → Success

## 4. Layout and Navigation Structure

### Authenticated Navigation (Fixed-Top Bootstrap Navbar)

**Desktop Layout (≥ 768px):**
```
┌─────────────────────────────────────────────────────────────┐
│ [10xCards] │ My Flashcards* │ Generate │ Create │ │ Logout │
└─────────────────────────────────────────────────────────────┘
```
*Active link has Bootstrap `.active` class (determined by `request.resolver_match.url_name`)

**Mobile Layout (< 768px):**
```
┌──────────────────────────────────┐
│ [10xCards]              [☰ Menu] │
└──────────────────────────────────┘
  Expanded hamburger menu:
  - My Flashcards*
  - Generate Flashcards
  - Create Flashcard
  - Logout
```

**Unauthenticated Pages:**
- No navbar displayed
- Only centered card layouts for registration/login/password reset

### Page Layout Pattern (Authenticated Views)

```
┌─────────────────────────────────────────┐
│ [Fixed Navbar]                          │
├─────────────────────────────────────────┤
│ <main class="container mt-4">          │
│   <div id="messages">                   │
│     [Success/Error Alerts - auto-dismiss│
│      after 5s, updated via hx-swap-oob] │
│   </div>                                │
│                                         │
│   [Page Heading (h1)]                   │
│                                         │
│   [View-Specific Content]               │
│   - My Flashcards: CTA buttons + list + │
│     pagination                          │
│   - Generate (Input): Textarea + button │
│   - Generate (Review): Card stack       │
│   - Create/Edit: Form with fields +     │
│     buttons                             │
│                                         │
│ </main>                                 │
└─────────────────────────────────────────┘
```

### Navigation Behavior

- **Active State:** Current view link highlighted with `.active` class
- **Logout:** Terminates session and redirects to Login Page
- **Responsive:** Hamburger menu on mobile, full navbar on desktop
- **HTMX Integration:** Most navigation uses full page loads (not HTMX), except pagination and in-page actions
- **First-Time User:** Redirect to My Flashcards after login (empty state guides to Generate/Create)

## 5. Key Components

### 5.1 Flashcard List Item Component (`_flashcard_card.html`)

Reusable Bootstrap list-group-item for displaying single flashcard in My Flashcards view with truncated front text and action buttons aligned right using flexbox.

### 5.2 Pagination Component (`_pagination.html`)

Bootstrap pagination controls (Previous, page numbers with ±2 from current, Next) using HTMX `hx-get` to load new pages without full reload, defaults to 25 cards per page.

### 5.3 Success/Error Message Component (`_messages.html`)

Bootstrap alert components (`.alert-success`, `.alert-danger`) with auto-dismiss after 5 seconds and manual close button, updated via HTMX out-of-band swap to `#messages` container.

### 5.4 Delete Confirmation Modal Component (`_delete_modal.html`)

Bootstrap modal triggered by Delete button with warning message "Delete this flashcard? This cannot be undone.", danger-styled Delete button using HTMX `hx-delete`, and secondary Cancel button.

### 5.5 Generated Flashcard Card Component (`_generated_card.html`)

Bootstrap card for AI-generated flashcard review with editable front/back text (textarea or contenteditable), footer containing Accept (primary green) and Reject (secondary red) buttons, used in vertical stack on review page.

### 5.6 Form Validation Component (Pattern)

Bootstrap form validation classes (`.is-invalid`, `.invalid-feedback`) applied to form fields with validation errors, inline error messages displayed below each field, returned via HTMX form fragment swap on validation failure.

### 5.7 Loading Spinner Overlay Component

Fixed-position overlay with Bootstrap spinner and message ("Generating flashcards... This may take up to 30 seconds"), triggered by HTMX `hx-indicator` attribute, disabled during async operations.

### 5.8 Empty State Component

Centered Bootstrap card displayed when My Flashcards list is empty with friendly message "You don't have any flashcards yet" and two prominent CTA buttons: "Generate with AI" (primary) and "Create Manually" (secondary).

### 5.9 Navigation Bar Component (`navbar.html`)

Bootstrap fixed-top navbar with brand logo on left, main navigation links in center with active state indication, and logout button on right, collapses to hamburger menu on mobile (< 768px).

### 5.10 Base Template (`base.html`)

Root Django template with Bootstrap 5 CSS, HTMX script, CSRF token in `hx-headers` on `<body>` element for automatic inclusion in all HTMX requests, navbar include for authenticated users, messages container, and content block for view-specific content.
