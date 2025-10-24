# UI Architecture Plan

## Conversation Summary

### Decisions

1. **Navigation Bar Structure:** Use Bootstrap fixed-top navbar with brand logo on left, main navigation links in center (My Flashcards, Generate Flashcards, Create Flashcard), and user controls on right (logout button). On mobile, use Bootstrap's hamburger menu for navigation links.

2. **My Flashcards Empty State:** Display a centered Bootstrap card with friendly message "You don't have any flashcards yet" and two prominent call-to-action buttons: "Generate with AI" (primary) and "Create Manually" (secondary).

3. **AI Generation Review Interface:** Display each generated flashcard as a Bootstrap card in a vertical stack with directly editable front/back text using `contenteditable` or `textarea`. Place Accept (primary green) and Reject (secondary red) buttons in card footer.

4. **Loading States for AI Generation:** Use HTMX with `hx-indicator` to show Bootstrap spinner overlay with message "Generating flashcards... This may take up to 30 seconds." Disable submit button during generation. On failure, swap in alert component with error message while preserving input text.

5. **Flashcard List Item Layout:** Use Bootstrap list group with each flashcard as `list-group-item`. Display front text with CSS `text-overflow: ellipsis` and always-visible Edit/Delete buttons aligned to right using `d-flex justify-content-between`.

6. **Delete Confirmation Pattern:** Use Bootstrap modal triggered by Delete button, containing warning message, danger-styled "Delete" button, and secondary "Cancel" button. Use HTMX to trigger modal and handle actual DELETE request.

7. **Form Validation Display:** Use Bootstrap's form validation classes (`.is-invalid`, `.invalid-feedback`). Display validation errors directly below each input field. When using HTMX, return form fragment with validation classes applied, swapping with `hx-swap="outerHTML"`.

8. **Pagination Controls:** Use 25 cards per page as default. Place Bootstrap pagination component at bottom of list only. Include "Previous", "Next" buttons plus page numbers (current ±2 pages). Use HTMX `hx-get` on pagination links.

9. **Study Session Functionality:** Ignore Study Session functionality for now (out of scope for initial implementation).

10. **CSRF Token Handling:** Use `hx-headers` on `<body>` element to automatically include CSRF token in all HTMX requests (django-htmx package approach).

11. **Generated Flashcards Review - Batch Actions:** Provide individual Accept/Reject buttons only (no bulk actions) to ensure users review each card's quality.

12. **AI Generation Text Input Area:** Use large Bootstrap `textarea` (rows="15" minimum) with `form-control` class. Do NOT display character counter. Validate 10,000 character limit server-side only.

13. **Flashcard Edit Mode:** Navigate to separate edit page (similar to Create Flashcard view). Use HTMX `hx-get` on Edit button to load edit form. After save/cancel, return to My Flashcards view.

14. **Success Messages Display:** Display Bootstrap alerts (`alert alert-success alert-dismissible`) at top of main content area. Use HTMX `hx-swap-oob="true"` to update dedicated message container. Auto-dismiss after 5 seconds with manual close button.

15. **Due Card Count Badge:** Hide Due Card Count Badge altogether (not focusing on studying part for initial implementation).

16. **API Generation Error - Input Preservation:** On generation failure, return form with input text preserved plus Bootstrap danger alert showing error message.

17. **Responsive Flashcard Display:** Use full-width Bootstrap cards stacking vertically on all screen sizes. On mobile, reduce button sizes to `btn-sm`. Edit/Delete buttons remain visible (not hidden).

18. **Login/Registration Flow Integration:** After registration, redirect to dedicated "Email Verification Pending" page with clear instructions and "Resend verification email" button.

19. **Empty Back Content Handling:** Enforce only non-empty validation (no minimum length). Use HTML5 `required` attribute for basic client-side validation, rely on Django serializer validation server-side.

20. **Navigation Active State:** Use Bootstrap's `active` class on current navigation link, conditionally applied based on current view name in Django templates.

### Matched Recommendations

All 20 recommendations provided during the conversation have been accepted and incorporated into the UI architecture plan, with the following modifications:

- **Recommendation 9 (Study Session):** Deferred for later implementation
- **Recommendation 10 (CSRF):** Modified to use `hx-headers` on `<body>` element approach
- **Recommendation 15 (Due Card Count):** Badge hidden entirely instead of conditionally displayed

---

## UI Architecture Planning Summary

### Main UI Architecture Requirements

**Framework Stack:**
- **Frontend Framework:** HTMX + Bootstrap 5
- **Backend Framework:** Django 5.2 + Django REST Framework 3.16
- **JavaScript:** Minimal (only for auto-dismiss alerts and potential UI enhancements)
- **Authentication:** Django session-based authentication with django-allauth
- **CSRF Protection:** Automatically included in HTMX requests via `hx-headers` on `<body>` element

**Design Philosophy:**
- Minimalist interface with no onboarding, tooltips, or complex organizational features
- Mobile-first responsive design using Bootstrap's grid system and utility classes
- Progressive enhancement: core functionality works without JavaScript, enhanced with HTMX
- Server-side rendering with HTMX for dynamic interactions (no client-side state management)

**Core UI Principles:**
1. **Simplicity First:** Clean layouts optimized for student users
2. **No Metadata Display:** Hide technical details, timestamps, and creation dates from users
3. **Direct Manipulation:** Minimal clicks to accomplish tasks
4. **Clear Feedback:** Immediate visual confirmation of actions
5. **Error Recovery:** Preserve user input on failures

---

### Key Views, Screens, and User Flows

#### 1. Authentication Views

**Registration Flow:**
```
Registration Page → Email Verification Pending Page → Email Verification Link → Login Page → My Flashcards
```

**Components:**
- Registration form with email and password fields
- Email verification pending page (centered Bootstrap card with instructions + resend button)
- Login form with email and password fields
- Password reset flow (Forgot Password link → Reset request → Email with reset link → New password form)

**Layout:**
- Centered card layout on blank page (no navbar for unauthenticated users)
- Bootstrap form controls with validation feedback
- Clear error messages for invalid credentials, unverified emails, etc.

#### 2. My Flashcards View (Main Dashboard)

**Purpose:** Browse all user flashcards with pagination, edit, and delete capabilities

**Layout:**
```
[Fixed Navbar]
[Success/Error Messages Container]
[Page Heading: "My Flashcards"]
[Call-to-Action Buttons: "Generate with AI" | "Create Manually"]
[Flashcard List - Bootstrap List Group]
  - Each item: [Front text (truncated)] [Edit] [Delete]
[Pagination Controls at bottom]
```

**Empty State:**
- Centered Bootstrap card with message and two prominent CTA buttons

**User Flows:**
- **View Flashcards:** Paginated list, 25 cards per page, sorted by creation date (newest first)
- **Edit Flashcard:** Click Edit → Navigate to edit page → Save/Cancel → Return to My Flashcards with success message
- **Delete Flashcard:** Click Delete → Bootstrap modal confirmation → Confirm → Card removed, list updates
- **Pagination:** Click page number/next/previous → HTMX loads new page content

**HTMX Integration:**
- Pagination links use `hx-get` to load new pages without full page reload
- Delete button triggers modal, modal's Delete button uses `hx-delete` to remove card

#### 3. Generate Flashcards View (AI Generation)

**Purpose:** Accept text input, generate flashcards via AI, review and accept/reject proposals

**Layout - Input Phase:**
```
[Fixed Navbar]
[Page Heading: "Generate Flashcards with AI"]
[Large Textarea (15+ rows) for text input]
[Generate Button]
```

**Layout - Review Phase:**
```
[Fixed Navbar]
[Page Heading: "Review Generated Flashcards"]
[Stack of Bootstrap Cards, each containing:]
  - Editable Front text (textarea/contenteditable)
  - Editable Back text (textarea/contenteditable)
  - [Accept] [Reject] buttons in card footer
```

**User Flows:**
- **Generate:** User pastes text → Clicks Generate → Loading spinner (up to 30s) → Review page with 5-10 cards
- **Review:** For each card: Optionally edit front/back → Click Accept (saves with creation_method: ai_full or ai_edited) OR Click Reject (discards)
- **Error Handling:** API failure → Error alert displayed, input text preserved, user can retry

**HTMX Integration:**
- Form submission uses `hx-post` with `hx-indicator` for loading state
- On success: Swap entire content area with review interface
- On error: Swap to show error alert while keeping form with preserved text
- Each Accept button uses `hx-post` to `/api/flashcards/` with appropriate creation_method
- Each Reject button removes card from DOM (client-side, no API call)

**API Interactions:**
- `POST /api/generations/` with `{input_text: "..."}` → Returns `{session_id, generated_flashcards: [{front, back}, ...]}`
- `POST /api/flashcards/` for each accepted card with `{front, back, creation_method, ai_session_id}`

#### 4. Create Flashcard View (Manual Creation)

**Purpose:** Manually create a single flashcard

**Layout:**
```
[Fixed Navbar]
[Page Heading: "Create Flashcard"]
[Form with Bootstrap form-controls:]
  - Front text input (required)
  - Back text input (required)
  - [Save] [Cancel] buttons
```

**User Flows:**
- **Create:** Fill front and back → Click Save → Validation → Success message → Redirect to My Flashcards
- **Cancel:** Click Cancel → Return to My Flashcards without saving
- **Validation Errors:** Empty fields → Display inline error messages below fields

**HTMX Integration:**
- Form submission uses `hx-post` to `/api/flashcards` with `creation_method: "manual"`
- On success: Navigate to My Flashcards with success message (via `hx-redirect` or server redirect)
- On validation error: Swap form with error messages displayed

**API Interactions:**
- `POST /api/flashcards/` with `{front, back, creation_method: "manual"}`

#### 5. Edit Flashcard View

**Purpose:** Edit existing flashcard front and back text

**Layout:**
```
[Fixed Navbar]
[Page Heading: "Edit Flashcard"]
[Form with Bootstrap form-controls:]
  - Front text input (pre-filled, required)
  - Back text input (pre-filled, required)
  - [Save] [Cancel] buttons
```

**User Flows:**
- **Edit:** Modify front/back → Click Save → Validation → Success message → Return to My Flashcards
- **Cancel:** Click Cancel → Return to My Flashcards without changes
- **Validation Errors:** Empty fields → Display inline error messages

**HTMX Integration:**
- Edit button in My Flashcards uses `hx-get` to load edit form
- Form submission uses `hx-put` to `/api/flashcards/{id}/`
- On success: Return to My Flashcards with success message
- On validation error: Swap form with error messages

**API Interactions:**
- `GET /api/flashcards/{id}/` to load flashcard data for editing
- `PUT /api/flashcards/{id}/` with `{front, back}` → May change `creation_method` to `ai_edited` if originally `ai_full`

#### 6. Navigation Structure

**Authenticated Navbar (Fixed-top):**
```
[Brand Logo/10xCards] | [My Flashcards] [Generate Flashcards] [Create Flashcard] | [Logout]
```

**Mobile Navbar (< 768px):**
```
[Brand Logo] [Hamburger Menu Icon]
  Expanded:
  - My Flashcards
  - Generate Flashcards
  - Create Flashcard
  - Logout
```

**Active State Indication:**
- Current view highlighted with Bootstrap `active` class
- Determined by Django template conditional based on `request.resolver_match.url_name`

---

### API Integration and State Management Strategy

#### API Communication Pattern

**HTMX-Driven Architecture:**
- All API interactions handled via HTMX attributes (`hx-get`, `hx-post`, `hx-put`, `hx-delete`)
- Server returns HTML fragments (partial templates) instead of JSON
- No client-side state management required (server is source of truth)

**Request Pattern:**
```
User Action → HTMX Request (with CSRF token) → Django View → DRF API Logic →
→ Render HTML Fragment → HTMX Swap → DOM Update
```

**CSRF Token Handling:**
```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <!-- All HTMX requests automatically include CSRF token -->
</body>
```

#### API Endpoints Usage

| View | HTTP Method | Endpoint                               | Purpose |
|------|-------------|----------------------------------------|---------|
| My Flashcards | GET | `/api/flashcards/?page=1&page_size=25` | List flashcards with pagination |
| Create Flashcard | POST | `/api/flashcards/`                     | Create manual flashcard |
| Edit Flashcard (Load) | GET | `/api/flashcards/{id}/`                | Retrieve flashcard for editing |
| Edit Flashcard (Save) | PUT | `/api/flashcards/{id}/`                | Update flashcard |
| Delete Flashcard | DELETE | `/api/flashcards/{id}/`                | Delete flashcard permanently |
| Generate (Request) | POST | `/api/generations/`                    | Generate flashcards from text |
| Review (Accept) | POST | `/api/flashcards/`                     | Save accepted AI-generated card |

#### Response Handling

**Success Responses:**
- Server returns HTML fragment with updated content
- HTMX swaps content using `hx-swap` strategy (innerHTML, outerHTML, etc.)
- Success messages displayed via out-of-band swap to `#messages` container

**Error Responses:**
- Validation errors (400): Return form fragment with `.is-invalid` classes and error messages
- Not found (404): Return error page or redirect to My Flashcards
- Server errors (500): Display user-friendly error message ("Couldn't generate flashcards right now. Please try again.")

**Loading States:**
- Use `hx-indicator` attribute pointing to spinner element
- Disable submit buttons during request processing
- Display context-appropriate loading messages (e.g., "Generating flashcards...")

#### State Management

**Server-Side State:**
- User session managed by Django (session cookie)
- All data persisted in PostgreSQL database
- No client-side caching or state beyond DOM

**Client-Side Interaction:**
- Minimal JavaScript for UI enhancements (auto-dismiss alerts)
- Form state preserved in DOM (no application state management needed)
- HTMX handles request/response cycle and DOM updates

---

### Responsiveness, Accessibility, and Security Considerations

#### Responsiveness

**Mobile-First Approach:**
- All layouts designed for mobile first, enhanced for larger screens
- Bootstrap breakpoints: xs (< 576px), sm (≥ 576px), md (≥ 768px), lg (≥ 992px), xl (≥ 1200px)

**Responsive Patterns:**
- **Navigation:** Hamburger menu on mobile, full navbar on desktop
- **Flashcard Cards:** Full-width stacking on all sizes, `btn-sm` on mobile
- **Forms:** Full-width inputs on mobile, constrained width on desktop (max-width with centered layout)
- **Pagination:** Responsive button sizes, fewer visible page numbers on mobile

**Bootstrap Utility Classes:**
- `d-none d-md-block` for hiding elements on small screens
- `col-12 col-md-8 col-lg-6` for responsive column widths
- `flex-column flex-md-row` for responsive flex direction

#### Security

**Authentication & Authorization:**
- Session-based authentication via Django
- All API endpoints require authentication (401/403 for unauthorized)
- User isolation: `queryset.filter(user=request.user)` in all views
- Attempted access to other users' resources returns 404 (not 403)

**CSRF Protection:**
- Django CSRF middleware enabled
- CSRF token included in all state-changing requests (POST, PUT, DELETE)
- HTMX automatically includes token via `hx-headers` on `<body>`

**Input Validation:**
- Client-side: HTML5 `required` attributes for basic validation
- Server-side: Django REST Framework serializers validate all inputs
- Field length limits enforced (front: 1-200 chars, back: 1-500 chars)

**SQL Injection Prevention:**
- Django ORM used exclusively (no raw SQL queries)

**XSS Prevention:**
- API returns HTML fragments (Django templates auto-escape by default)
- User-generated content sanitized before rendering
- Bootstrap components don't execute inline scripts

**Email Verification:**
- Mandatory email verification before login (`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`)
- Verification links time-limited
- Unverified users see appropriate error message on login attempt

**Password Security:**
- Argon2 password hashing (Django's primary hasher)
- Password strength requirements enforced during registration
- Secure password reset flow with time-limited tokens

---

## Unresolved Issues

### Areas Requiring Further Clarification

1. **AI Generation Review - After All Actions Taken:** When user has accepted/rejected all generated flashcards, should there be a "Back to My Flashcards" button, or should they navigate via navbar? Auto-redirect after last action?

2. **Edit Detection Logic:** For AI-generated flashcards, when should `creation_method` change from `ai_full` to `ai_edited`? During initial review (before first save) or only on subsequent edits? PRD suggests during initial review if user modifies before accepting.

3. **Pagination State Preservation:** When user edits a flashcard from page 3 and returns to My Flashcards, should they return to page 3 or page 1? Requires query parameter preservation.

4. **Maximum Text Length UI Feedback:** While character counter is not displayed, should there be any visual indication when approaching the 10,000 character limit during AI generation, or rely entirely on server-side validation error?

5. **Study Session Integration Points:** When Study Session functionality is implemented later, what changes will be needed to current views? Should we reserve space/structure for future integration?

6. **Logout Confirmation:** Should logout require confirmation, or immediate logout on click? Security vs. UX trade-off.

7. **Mobile Textarea Sizing:** On mobile devices, should the AI generation textarea auto-expand as user types, or maintain fixed height with scrolling?

8. **Flashcard Character Limits in UI:** While front is 1-200 chars and back is 1-500 chars per API plan, should these be enforced with `maxlength` attribute in HTML forms, or allow over-typing and show validation error on submit?

9. **Empty Flashcard List After Deletion:** If user deletes the last flashcard on a page, should they be redirected to previous page, or show empty state for that page?

10. **Browser Back Button Behavior:** With HTMX navigation, should browser back button work as expected (return to previous view), or does it require special HTMX configuration (`hx-push-url`)?

### Implementation Priorities

**Phase 1 (Core MVP):**
- Authentication views (register, login, password reset, email verification)
- My Flashcards view with pagination, edit, delete
- Create Flashcard view (manual creation)
- Basic navigation structure

**Phase 2 (AI Generation):**
- Generate Flashcards view with AI integration
- Review interface with accept/reject
- Error handling for AI failures

**Phase 3 (Polish):**
- Success message auto-dismiss
- Responsive refinements
- Accessibility audit and fixes
- Browser back button support

**Deferred:**
- Study Session functionality
- Due card count badge
- Advanced spaced repetition features

---

## Technical Implementation Notes

### Django Template Structure

**Base Template (`base.html`):**
```django
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token }}">
  <title>{% block title %}10xCards{% endblock %}</title>
  <link href="[Bootstrap 5 CSS]" rel="stylesheet">
  <script src="[HTMX]"></script>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  {% if user.is_authenticated %}
    {% include "navbar.html" %}
  {% endif %}

  <main class="container mt-4">
    <div id="messages">
      {% include "messages.html" %}
    </div>

    {% block content %}{% endblock %}
  </main>

  <script src="[Minimal JS for auto-dismiss]"></script>
</body>
</html>
```

Note that a `base.html` file already exists - it was created by django-cookiecutter (see `flashcards/templates/base.html`). It will need to be adapted to the above structure.

**Partial Templates:**
- `_flashcard_list.html` - Flashcard list fragment for HTMX swapping
- `_flashcard_card.html` - Individual flashcard list item
- `_pagination.html` - Pagination controls
- `_messages.html` - Success/error alerts
- `_generated_card.html` - AI-generated flashcard in review interface
- `_delete_modal.html` - Delete confirmation modal

### Django View Architecture

**View Pattern:**
```python
class FlashcardListView(LoginRequiredMixin, ListView):
    model = Flashcard
    template_name = 'flashcards/list.html'  # Full page
    partial_template_name = 'flashcards/_flashcard_list.html'  # HTMX fragment
    paginate_by = 25

    def get_queryset(self):
        return Flashcard.objects.filter(user=self.request.user).order_by('-created_at')

    def get_template_names(self):
        # Return partial template for HTMX requests and full template for regular requests
        return [self.partial_template_name] if self.request.htmx else [self.template_name]
```

### HTMX Configuration

**Global Event Listeners:**
```javascript
// Auto-dismiss success messages
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

### Bootstrap Customization

**Custom CSS (Minimal):**
```css
/* Truncate flashcard front text in list */
.flashcard-front {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 600px;
}

/* Loading spinner overlay */
.htmx-indicator {
  display: none;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1050;
}

.htmx-request .htmx-indicator {
  display: block;
}
```

---

## Next Steps

1. **Create Django templates** based on layout specifications
2. **Implement Django views** using class-based views with HTMX support
3. **Configure HTMX** in base template with CSRF token handling
4. **Implement DRF serializers and viewsets** for API endpoints
5. **Create partial templates** for HTMX fragment responses
6. **Test responsive layouts** across device sizes
7. **Accessibility audit** using automated tools and manual testing
8. **User testing** to validate flows and identify UX issues
