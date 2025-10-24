# View Implementation Plan: My Flashcards

## 1. Overview

The My Flashcards view is the primary landing page for authenticated users, displaying a paginated list of all flashcards owned by the user. It serves as the central hub for flashcard management, allowing users to view, edit, and delete their flashcards. The view emphasizes simplicity with a flat list structure, no organizational features, and clear calls-to-action for generating or creating new flashcards.

## 2. View Routing

**Primary URL:** `/flashcards/`

**URL Name:** `flashcards:list`

**Authentication:** Required (redirects unauthenticated users to login)

**Query Parameters:**
- `page` (integer, optional): Page number for pagination, default: 1
- `page_size` (integer, optional): Items per page (25-50), default: 25

**Example URLs:**
- `/flashcards/` - First page with default page size
- `/flashcards/?page=2` - Second page
- `/flashcards/?page=1&page_size=50` - First page with 50 items

## 3. Component Structure

Since this is a Django + HTMX application, components are Django template partials rather than JavaScript components. The structure follows server-rendered HTML patterns with HTMX-enhanced interactivity.

### Template Hierarchy

```
flashcards/flashcard_list.html (Full Page Template)
├── flashcards/base.html (extends)
├── Navigation Bar (from base template)
├── Main Content Container
│   ├── Page Header Section
│   │   ├── Title: "My Flashcards"
│   │   └── Total Count Badge
│   ├── CTA Button Group
│   │   ├── "Generate Flashcards" Button → /flashcards/generate/
│   │   └── "Create Flashcard" Button → /flashcards/create/
│   ├── Alert Messages Container (id="alert-container")
│   │   └── flashcards/_alert.html (conditionally included)
│   ├── Flashcard List Container (id="flashcard-list-container")
│   │   ├── flashcards/_flashcard_list_items.html (if flashcards exist)
│   │   │   └── flashcards/_flashcard_item.html (repeated for each flashcard)
│   │   └── flashcards/_empty_state.html (if no flashcards)
│   └── flashcards/_pagination.html (if total count > page_size)
└── flashcards/_delete_confirmation_modal.html (Bootstrap modal)
```

## 4. Component Details

### 4.1 FlashcardListView (Django Class-Based View)

**Component Description:** Main Django view that handles GET requests for the flashcard list page. Responsible for querying flashcards, applying pagination, and rendering the appropriate template (full page or HTMX fragment).

**Main Elements:**
- Extends `LoginRequiredMixin` and `ListView`
- Queryset filtered to authenticated user's flashcards only
- Pagination with configurable page size (25-50 items)

**Handled Events:**
- GET requests to `/flashcards/`
- Query parameters: `page`, `page_size`

**Validation Conditions:**
- User must be authenticated (enforced by LoginRequiredMixin)
- `page_size` must be between 25-50 (validated in view, defaults to 25)
- `page` must be valid integer (Django Paginator handles invalid values)

**Types:**
- Request: `HttpRequest` with authenticated user
- Response: `HttpResponse` (rendered HTML)
- Context: `FlashcardListContext` (see Types section)

**Props:** N/A (Django view, not a component)

---

### 4.2 flashcard_list.html (Main Template)

**Component Description:** Full page template that serves as the container for the entire My Flashcards view. Used for initial page load and includes all sub-templates.

**Main Elements:**
- `{% extends "flashcards/base.html" %}`
- `<main>` container with Bootstrap classes
- `<div id="flashcard-list-container">` - HTMX swap target
- CTA button group with Bootstrap `.btn-group`
- Alert message container
- Pagination section

**Handled Events:** None (container template only)

**Validation Conditions:** None

**Types:**
- Context: `FlashcardListContext`

**Props:**
- `flashcards`: QuerySet of Flashcard objects for current page
- `page_obj`: Django Paginator Page object
- `is_paginated`: Boolean
- `total_count`: Integer
- `messages`: Django messages framework messages

---

### 4.3 _flashcard_list_items.html (Partial Template)

**Component Description:** Reusable template fragment that renders the list of flashcard items. Used for both initial page load and HTMX pagination updates.

**Main Elements:**
- `<ul class="list-group">` - Bootstrap list group container
- Loops through flashcards with `{% for flashcard in flashcards %}`
- Includes `_flashcard_item.html` for each flashcard
- Conditional rendering based on flashcard existence

**Handled Events:** None (presentational component)

**Validation Conditions:**
- Checks if `flashcards` is empty to conditionally render

**Types:**
- Input: List of `FlashcardItemViewModel`

**Props:**
- `flashcards`: List of flashcard objects for current page

---

### 4.4 _flashcard_item.html (Partial Template)

**Component Description:** Individual flashcard list item displaying truncated front text with Edit and Delete action buttons.

**Main Elements:**
- `<li class="list-group-item">` - Bootstrap list group item
- `<div class="d-flex justify-content-between align-items-center">`
- `<span class="flashcard-front">` - Truncated front text with ellipsis
- `<div class="btn-group">` - Action buttons container
  - Edit button: `<a href="{% url 'flashcards:edit' flashcard.id %}" class="btn btn-sm btn-outline-primary">`
  - Delete button: `<button class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteModal" data-flashcard-id="{{ flashcard.id }}">`

**Handled Events:**
- Edit button click: Navigate to edit page
- Delete button click: Open delete confirmation modal

**Validation Conditions:**
- Truncate `front` text to 100 characters with ellipsis if longer

**Types:**
- Input: `FlashcardItemViewModel`

**Props:**
- `flashcard`: Single flashcard object with id, front, back

---

### 4.5 _empty_state.html (Partial Template)

**Component Description:** Friendly empty state message displayed when user has no flashcards, encouraging them to create their first flashcard.

**Main Elements:**
- `<div class="text-center py-5">` - Centered container
- `<p class="text-muted">` - Empty state message
- CTA buttons for Generate and Create

**Handled Events:**
- Click Generate button: Navigate to `/flashcards/generate/`
- Click Create button: Navigate to `/flashcards/create/`

**Validation Conditions:** None

**Types:** None

**Props:** None

---

### 4.6 _pagination.html (Partial Template)

**Component Description:** Bootstrap pagination controls with HTMX-enhanced navigation for loading pages without full page refresh.

**Main Elements:**
- `<nav aria-label="Flashcard pagination">`
- `<ul class="pagination justify-content-center">`
- Previous button: `<li class="page-item">` with `hx-get`
- Page number buttons: Loop through page range
- Next button: `<li class="page-item">` with `hx-get`

**Handled Events:**
- Click Previous: HTMX GET request to previous page
- Click Next: HTMX GET request to next page
- Click page number: HTMX GET request to specific page

**Validation Conditions:**
- Disable Previous if on first page (`page_obj.has_previous`)
- Disable Next if on last page (`page_obj.has_next`)
- Highlight current page number

**Types:**
- Input: Django `Page` object

**Props:**
- `page_obj`: Django Paginator Page object with pagination metadata

**HTMX Attributes:**
- `hx-get="/flashcards/?page={number}"` - Load specific page
- `hx-target="#flashcard-list-container"` - Swap target
- `hx-swap="innerHTML"` - Swap strategy
- `hx-push-url="true"` - Update browser URL
- `hx-indicator="#loading-indicator"` - Loading state indicator

---

### 4.7 _delete_confirmation_modal.html (Partial Template)

**Component Description:** Bootstrap modal dialog for confirming flashcard deletion with Delete and Cancel actions.

**Main Elements:**
- `<div class="modal fade" id="deleteModal">`
- Modal header with title "Delete Flashcard"
- Modal body with confirmation message: "Delete this flashcard? This cannot be undone."
- Modal footer with buttons:
  - Cancel: `<button class="btn btn-secondary" data-bs-dismiss="modal">`
  - Delete: `<button class="btn btn-danger" id="confirmDeleteBtn">`

**Handled Events:**
- Cancel button click: Close modal (Bootstrap data-bs-dismiss)
- Delete button click: HTMX DELETE request to delete endpoint

**Validation Conditions:**
- Modal receives flashcard ID via data attribute when opened
- Delete button must have correct flashcard ID before sending request

**Types:** None

**Props:** None (receives flashcard ID dynamically via JavaScript data attributes)

**HTMX Attributes (on Delete button):**
- `hx-delete="/flashcards/{id}/delete/"` - Delete endpoint (set dynamically)
- `hx-target="#flashcard-list-container"` - Reload list after delete
- `hx-swap="innerHTML"` - Replace list content
- `hx-on::after-request="bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide()"` - Close modal after delete

---

### 4.8 _alert.html (Partial Template)

**Component Description:** Bootstrap alert component for displaying success/error messages using Django messages framework.

**Main Elements:**
- `<div class="alert alert-{level} alert-dismissible fade show">`
- `<button class="btn-close" data-bs-dismiss="alert">`
- Message text

**Handled Events:**
- Click close button: Dismiss alert

**Validation Conditions:**
- Set alert level class based on message level (success, error, warning, info)

**Types:**
- Input: Django Message object

**Props:**
- `message`: Django message with level and text

---

### 4.9 FlashcardDeleteView (Django View)

**Component Description:** Django view handling DELETE requests for flashcard deletion with ownership validation.

**Main Elements:**
- Extends `LoginRequiredMixin` and `DeleteView` or custom delete logic
- Validates flashcard ownership
- Returns HTMX-friendly response

**Handled Events:**
- DELETE requests to `/flashcards/{id}/delete/`

**Validation Conditions:**
- User must be authenticated
- Flashcard must exist
- Flashcard must belong to authenticated user (return 404 otherwise)
- CSRF token must be valid

**Types:**
- Request: `HttpRequest` with DELETE method
- Response: `HttpResponse` (HTML fragment with updated list and success message)

**Props:** N/A (Django view)

## 5. Types

### 5.1 FlashcardDTO (from API)

While the API endpoint exists, for HTMX implementation we work directly with Django model instances. This type represents the shape of data from the API if used:

```python
FlashcardDTO = {
    "id": int,
    "front": str,                    # Max 200 characters
    "back": str,                     # Max 500 characters
    "creation_method": str,          # "ai_full" | "ai_edited" | "manual"
    "created_at": str,               # ISO 8601 datetime string
    "updated_at": str                # ISO 8601 datetime string
}
```

### 5.2 FlashcardListContext (Template Context)

Context dictionary passed to `flashcard_list.html` template:

```python
FlashcardListContext = {
    "flashcards": QuerySet[Flashcard],     # Current page flashcards
    "page_obj": Page,                      # Django Paginator Page object
    "is_paginated": bool,                  # True if pagination needed
    "paginator": Paginator,                # Django Paginator instance
    "total_count": int,                    # Total flashcard count
    "has_flashcards": bool,                # True if user has any flashcards
    "page_size": int,                      # Current page size (25-50)
    "current_page": int,                   # Current page number
    "messages": MessagesList               # Django messages framework
}
```

### 5.3 FlashcardItemViewModel

View model for individual flashcard items with truncation:

```python
FlashcardItemViewModel = {
    "id": int,
    "front": str,                          # Original front text
    "front_truncated": str,                # Truncated to 100 chars with "..."
    "is_truncated": bool,                  # True if front was truncated
    "back": str                            # Full back text (not displayed in list)
}
```

### 5.4 Page Object (Django Paginator)

Django's built-in Page object with pagination metadata:

```python
Page = {
    "object_list": List[Flashcard],        # Flashcards on current page
    "number": int,                         # Current page number
    "paginator": Paginator,                # Reference to Paginator
    "has_next": bool,                      # True if next page exists
    "has_previous": bool,                  # True if previous page exists
    "has_other_pages": bool,               # True if more than one page
    "next_page_number": int,               # Next page number (if exists)
    "previous_page_number": int,           # Previous page number (if exists)
    "start_index": int,                    # Index of first item on page
    "end_index": int                       # Index of last item on page
}
```

### 5.5 Paginator Object (Django Paginator)

Django's Paginator object:

```python
Paginator = {
    "count": int,                          # Total number of items
    "num_pages": int,                      # Total number of pages
    "page_range": range,                   # Range of page numbers
    "per_page": int                        # Items per page
}
```

## 6. State Management

State management in this HTMX + Django application is handled through a combination of server-side and client-side mechanisms:

### 6.1 Server-Side State (Django View)

The primary source of truth for application state:

- **User Session:** Managed by Django's authentication system, persists user login state
- **Database State:** Flashcard data stored in PostgreSQL, queried on each request
- **Queryset Filtering:** `Flashcard.objects.for_user(request.user)` ensures user isolation
- **Pagination State:** Managed by Django Paginator based on query parameters
- **Messages:** Django messages framework stores success/error messages in session

### 6.2 Client-Side State (HTMX + Bootstrap)

Minimal client-side state managed by HTMX and Bootstrap:

- **Current Page Content:** HTMX swaps DOM content based on server responses
- **Modal Visibility:** Bootstrap modal state (open/closed)
- **Selected Flashcard ID:** Stored in modal's data attribute when delete button clicked
- **Loading States:** HTMX manages loading indicators during requests

### 6.3 No Custom State Management Needed

This implementation does not require:
- Custom JavaScript state management libraries (Redux, Vuex, etc.)
- React hooks or Vue composition API
- Client-side data caching beyond browser cache

All complex state logic is handled server-side, with HTMX providing seamless updates to the DOM based on server responses.

### 6.4 State Flow Example: Delete Flashcard

1. User clicks Delete button → Modal opens (Bootstrap state)
2. Modal stores flashcard ID in data attribute (DOM state)
3. User confirms delete → HTMX sends DELETE request with ID
4. Django view deletes flashcard, updates database (server state)
5. View queries updated flashcard list with pagination
6. View renders updated list HTML fragment
7. HTMX receives response, swaps DOM content (client state update)
8. Modal closes via HTMX event callback (Bootstrap state)
9. Success message displayed via Django messages (session state)

## 7. API Integration

### 7.1 Architecture Overview

This Django + HTMX application uses **server-rendered HTML** rather than client-side API consumption. The flow is:

1. Django views query the database directly using the ORM
2. Views render HTML templates with context data
3. HTMX makes requests to Django views (not API endpoints)
4. Django views return HTML fragments for HTMX to swap into the DOM

The existing DRF API endpoint (`GET /api/flashcards`) is available but **not used by this view implementation**. It exists for potential future API consumers.

### 7.2 Django View Implementation

**FlashcardListView** implementation:

```python
# flashcards/views/flashcard_list.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from flashcards.core.models import Flashcard

class FlashcardListView(LoginRequiredMixin, ListView):
    """Display paginated list of user's flashcards."""

    model = Flashcard
    template_name = "flashcards/flashcard_list.html"
    context_object_name = "flashcards"
    paginate_by = 25

    def get_queryset(self):
        """Return only flashcards owned by authenticated user."""
        return Flashcard.objects.for_user(self.request.user)

    def get_paginate_by(self, queryset):
        """Allow page_size override via query param (25-50)."""
        page_size = self.request.GET.get('page_size', 25)
        try:
            page_size = int(page_size)
            # Clamp to valid range
            return max(25, min(50, page_size))
        except (ValueError, TypeError):
            return 25

    def get_template_names(self):
        """Return fragment template for HTMX requests."""
        if self.request.headers.get('HX-Request'):
            return ["flashcards/_flashcard_list_items.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = self.get_queryset().count()
        context['has_flashcards'] = context['total_count'] > 0
        context['page_size'] = self.get_paginate_by(None)
        return context
```

### 7.3 Delete View Implementation

**FlashcardDeleteView** implementation:

```python
# flashcards/views/flashcard_delete.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.views import View
from flashcards.core.models import Flashcard

class FlashcardDeleteView(LoginRequiredMixin, View):
    """Handle flashcard deletion with HTMX support."""

    def delete(self, request, pk):
        """Delete flashcard and return updated list."""
        # Get flashcard or 404 if doesn't exist or doesn't belong to user
        flashcard = get_object_or_404(
            Flashcard,
            pk=pk,
            user=request.user
        )

        flashcard.delete()
        messages.success(request, "Flashcard deleted successfully.")

        # Return updated flashcard list for HTMX swap
        flashcards = Flashcard.objects.for_user(request.user)

        return render(request, "flashcards/_flashcard_list_items.html", {
            "flashcards": flashcards,
            "has_flashcards": flashcards.exists()
        })
```

### 7.4 URL Configuration

```python
# flashcards/urls.py

from django.urls import path
from flashcards.views import FlashcardListView, FlashcardDeleteView

app_name = "flashcards"

urlpatterns = [
    path("", FlashcardListView.as_view(), name="list"),
    path("<int:pk>/delete/", FlashcardDeleteView.as_view(), name="delete"),
    # Other URLs...
]
```

### 7.5 Request/Response Types

**FlashcardListView:**
- Request: `GET /flashcards/?page=1&page_size=25`
- Response Headers (HTMX): `HX-Request: true`
- Response Type: `text/html` (full page or fragment based on HX-Request header)
- Response Content: Rendered HTML template

**FlashcardDeleteView:**
- Request: `DELETE /flashcards/{id}/delete/`
- Request Headers: `HX-Request: true`, `X-CSRFToken: {token}`
- Response Type: `text/html`
- Response Content: Updated flashcard list HTML fragment + alert message

## 8. User Interactions

### 8.1 Initial Page Load

**User Action:** User navigates to `/flashcards/` or logs in

**System Flow:**
1. Django checks authentication (LoginRequiredMixin)
2. FlashcardListView queries `Flashcard.objects.for_user(request.user)`
3. Apply default pagination (25 items, page 1)
4. Render `flashcard_list.html` with full page template
5. Display flashcard list or empty state

**Expected Outcome:**
- If flashcards exist: List of up to 25 flashcards, newest first
- If no flashcards: Empty state with message and CTA buttons
- Pagination controls shown if total > 25

### 8.2 Click Edit Button

**User Action:** User clicks "Edit" button on a flashcard

**System Flow:**
1. Browser navigates to `/flashcards/{id}/edit/`
2. Edit view loads (separate view, out of scope for this document)

**Expected Outcome:**
- Navigate to edit page
- Edit form displays with flashcard data pre-filled

### 8.3 Click Delete Button

**User Action:** User clicks "Delete" button on a flashcard

**System Flow:**
1. Bootstrap modal opens via `data-bs-toggle="modal"`
2. JavaScript sets flashcard ID on modal's delete button via data attribute
3. Modal displays confirmation message

**Expected Outcome:**
- Delete confirmation modal appears
- Focus moves to modal (accessibility)
- Modal shows: "Delete this flashcard? This cannot be undone."
- Delete and Cancel buttons visible

**Implementation Detail:**
```javascript
// Set flashcard ID on modal when opened
document.getElementById('deleteModal').addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget; // Button that triggered modal
  const flashcardId = button.getAttribute('data-flashcard-id');
  const deleteBtn = document.getElementById('confirmDeleteBtn');
  deleteBtn.setAttribute('hx-delete', `/flashcards/${flashcardId}/delete/`);
  htmx.process(deleteBtn); // Re-process HTMX attributes
});
```

### 8.4 Confirm Delete

**User Action:** User clicks "Delete" button in confirmation modal

**System Flow:**
1. HTMX sends DELETE request to `/flashcards/{id}/delete/`
2. Django view validates ownership and deletes flashcard
3. Django view queries updated flashcard list
4. Django view renders `_flashcard_list_items.html` or `_empty_state.html`
5. HTMX swaps content into `#flashcard-list-container`
6. Modal closes via HTMX callback
7. Success message displays

**Expected Outcome:**
- Flashcard removed from list
- Modal closes
- Success alert appears: "Flashcard deleted successfully."
- List updates to show remaining flashcards or empty state
- If last flashcard on page deleted and previous page exists, show previous page

### 8.5 Cancel Delete

**User Action:** User clicks "Cancel" button in confirmation modal

**System Flow:**
1. Bootstrap modal closes via `data-bs-dismiss="modal"`
2. No server request made

**Expected Outcome:**
- Modal closes
- No changes to flashcard list
- No server request

### 8.6 Navigate to Next Page

**User Action:** User clicks "Next" button or page number in pagination

**System Flow:**
1. HTMX sends GET request to `/flashcards/?page={n}&page_size={size}`
2. Django view queries next page of flashcards
3. Django view renders `_flashcard_list_items.html` fragment
4. HTMX swaps content into `#flashcard-list-container`
5. Browser URL updates via `hx-push-url`
6. Pagination controls update to reflect new page

**Expected Outcome:**
- List updates with next page flashcards
- URL updates to show current page
- Pagination controls highlight new current page
- Previous/Next buttons enable/disable appropriately
- Smooth transition without full page reload

### 8.7 Click Generate Flashcards CTA

**User Action:** User clicks "Generate Flashcards" button (in header or empty state)

**System Flow:**
1. Browser navigates to `/flashcards/generate/`
2. Generate view loads (separate view)

**Expected Outcome:**
- Navigate to Generate Flashcards page
- Text input form displays

### 8.8 Click Create Flashcard CTA

**User Action:** User clicks "Create Flashcard" button (in header or empty state)

**System Flow:**
1. Browser navigates to `/flashcards/create/`
2. Create view loads (separate view)

**Expected Outcome:**
- Navigate to Create Flashcard page
- Manual creation form displays

## 9. Conditions and Validation

### 9.1 Authentication Validation

**Condition:** User must be authenticated to access the view

**Components Affected:**
- `FlashcardListView`
- `FlashcardDeleteView`

**Implementation:**
- Use `LoginRequiredMixin` on all views
- Django middleware redirects unauthenticated users to login page

**Effect on Interface:**
- Unauthenticated users redirected to `/accounts/login/`
- After login, redirect to `/flashcards/`

### 9.2 Flashcard Ownership Validation

**Condition:** Users can only view/delete their own flashcards

**Components Affected:**
- `FlashcardListView.get_queryset()`
- `FlashcardDeleteView.delete()`

**Implementation:**
- Filter queryset: `Flashcard.objects.for_user(request.user)`
- Use `get_object_or_404(Flashcard, pk=pk, user=request.user)`

**Effect on Interface:**
- List shows only user's flashcards
- Attempting to delete another user's flashcard returns 404
- No indication that other users' flashcards exist (security)

### 9.3 Page Size Validation

**Condition:** `page_size` must be between 25 and 50

**Components Affected:**
- `FlashcardListView.get_paginate_by()`

**Implementation:**
```python
page_size = max(25, min(50, int(page_size)))
```

**Effect on Interface:**
- Invalid page sizes clamped to valid range
- Default to 25 if not specified or invalid
- Pagination controls reflect validated page size

### 9.4 Page Number Validation

**Condition:** `page` must be valid integer within available pages

**Components Affected:**
- Django `Paginator` in `FlashcardListView`

**Implementation:**
- Django Paginator handles invalid pages automatically
- Can customize behavior for `EmptyPage` exception

**Effect on Interface:**
- Invalid page numbers show last page or first page
- Out-of-range pages handled gracefully without errors

### 9.5 Empty State Validation

**Condition:** Show empty state when user has no flashcards

**Components Affected:**
- `flashcard_list.html`
- `_flashcard_list_items.html`

**Implementation:**
```django
{% if has_flashcards %}
  {% include "flashcards/_flashcard_list_items.html" %}
{% else %}
  {% include "flashcards/_empty_state.html" %}
{% endif %}
```

**Effect on Interface:**
- Empty state displays friendly message and CTAs
- No empty list or confusing blank page
- Encourages user action (generate or create)

### 9.6 Truncation Validation

**Condition:** Front text must be truncated to ~100 characters with ellipsis

**Components Affected:**
- `_flashcard_item.html`

**Implementation:**
```django
{{ flashcard.front|truncatechars:100 }}
```

**Effect on Interface:**
- Long front text truncated to 100 characters
- Ellipsis (...) appended to truncated text
- Full text available on edit/detail view

### 9.7 CSRF Validation

**Condition:** All POST/DELETE requests must include valid CSRF token

**Components Affected:**
- `FlashcardDeleteView`
- All forms and HTMX requests

**Implementation:**
- Django CSRF middleware validates tokens
- HTMX automatically includes CSRF token from cookie

**Effect on Interface:**
- Invalid CSRF tokens result in 403 Forbidden
- User must refresh page to get new token

## 10. Error Handling

### 10.1 No Flashcards (Empty State)

**Scenario:** User has no flashcards in their collection

**Handling:**
- Check `has_flashcards` in template context
- Render `_empty_state.html` instead of list
- Display friendly message: "You don't have any flashcards yet. Get started by generating flashcards from your study materials or creating one manually."
- Show prominent CTA buttons for Generate and Create

**User Experience:**
- Clear next steps
- No confusing empty list
- Encourages engagement

### 10.2 Delete Fails (Server Error)

**Scenario:** Database error or exception during flashcard deletion

**Handling:**
- Wrap delete logic in try/except block
- Use Django messages framework for error message
- Return error alert HTML fragment
- Log error details for debugging

**Implementation:**
```python
try:
    flashcard.delete()
    messages.success(request, "Flashcard deleted successfully.")
except Exception as e:
    logger.exception("Failed to delete flashcard %s", pk)
    messages.error(request, "Failed to delete flashcard. Please try again.")
```

**User Experience:**
- Error alert displayed: "Failed to delete flashcard. Please try again."
- Flashcard remains in list
- Modal closes
- User can retry

### 10.3 Unauthorized Delete Attempt

**Scenario:** User attempts to delete another user's flashcard

**Handling:**
- Use `get_object_or_404(Flashcard, pk=pk, user=request.user)`
- Returns 404 Not Found (not 403 Forbidden)
- Don't reveal whether flashcard exists

**User Experience:**
- 404 error page displayed
- No indication whether flashcard exists or belongs to another user
- Security: prevents information disclosure

### 10.4 Network Error (HTMX Request Fails)

**Scenario:** Network connection lost during HTMX request

**Handling:**
- Listen for `htmx:responseError` event
- Display generic error message
- Optionally retry request

**Implementation:**
```javascript
document.body.addEventListener('htmx:responseError', function(event) {
  alert('Network error. Please check your connection and try again.');
});
```

**User Experience:**
- Clear error message
- User understands issue is network-related
- Can retry action manually

### 10.5 Invalid Page Number

**Scenario:** User navigates to page that doesn't exist (e.g., page 999)

**Handling:**
- Django Paginator raises `EmptyPage` exception
- Catch exception and show last available page
- Or redirect to page 1 with error message

**Implementation:**
```python
from django.core.paginator import EmptyPage, PageNotAnInteger

try:
    page_obj = paginator.page(page_number)
except PageNotAnInteger:
    page_obj = paginator.page(1)
except EmptyPage:
    page_obj = paginator.page(paginator.num_pages)
```

**User Experience:**
- Shows last page instead of error
- Or shows first page with message
- No broken state

### 10.6 Session Expired

**Scenario:** User's authentication session expires during use

**Handling:**
- Django authentication middleware checks session
- Redirect to login page with `next` parameter
- After login, redirect back to flashcards list

**Implementation:**
- Automatic via `LoginRequiredMixin`
- `LOGIN_URL` setting in Django configuration

**User Experience:**
- Redirected to login page
- Message: "Please log in to continue"
- After login, returns to intended page

### 10.7 CSRF Token Mismatch

**Scenario:** CSRF token invalid or missing on DELETE request

**Handling:**
- Django CSRF middleware rejects request with 403 Forbidden
- Display error message
- User must refresh page to get new token

**Implementation:**
- Automatic via Django CSRF middleware
- Ensure HTMX includes CSRF token in requests

**User Experience:**
- Error message: "CSRF verification failed. Please refresh the page."
- User refreshes and can retry action

### 10.8 Slow API Response

**Scenario:** Database query takes longer than expected

**Handling:**
- Display loading indicator during HTMX request
- Use `hx-indicator` attribute
- Show Bootstrap spinner

**Implementation:**
```html
<div id="loading-indicator" class="htmx-indicator">
  <div class="spinner-border" role="status">
    <span class="visually-hidden">Loading...</span>
  </div>
</div>
```

**User Experience:**
- Loading spinner visible during request
- User knows system is working
- No confusion about frozen interface

## 11. Implementation Steps

### Step 1: Create Django Views

1. Create `flashcards/views/flashcard_list.py`
2. Implement `FlashcardListView` extending `LoginRequiredMixin` and `ListView`
3. Override `get_queryset()` to filter by user
4. Override `get_paginate_by()` to support page_size parameter
5. Override `get_template_names()` to return fragment for HTMX requests
6. Override `get_context_data()` to add total_count and has_flashcards

### Step 2: Create Delete View

1. Create `flashcards/views/flashcard_delete.py`
2. Implement `FlashcardDeleteView` extending `LoginRequiredMixin` and `View`
3. Implement `delete()` method with ownership validation
4. Add success message via Django messages framework
5. Return updated list HTML fragment for HTMX swap

### Step 3: Configure URLs

1. Create or update `flashcards/urls.py`
2. Add URL pattern for list view: `path("", FlashcardListView.as_view(), name="list")`
3. Add URL pattern for delete: `path("<int:pk>/delete/", FlashcardDeleteView.as_view(), name="delete")`
4. Set `app_name = "flashcards"` for namespacing

### Step 4: Create Base Template

1. Create `flashcards/templates/flashcards/base.html` (if not exists)
2. Add Bootstrap 5 CSS and JS includes
3. Add HTMX script include
4. Create navigation bar with "My Flashcards", "Generate Flashcards", "Create Flashcard" links
5. Add main content block: `{% block content %}{% endblock %}`
6. Include Django messages display area

### Step 5: Create Main List Template

1. Create `flashcards/templates/flashcards/flashcard_list.html`
2. Extend `base.html`
3. Add page header with title "My Flashcards" and total count badge
4. Add CTA button group (Generate and Create buttons)
5. Add alert container: `<div id="alert-container">`
6. Add flashcard list container: `<div id="flashcard-list-container">`
7. Conditionally include `_flashcard_list_items.html` or `_empty_state.html`
8. Include pagination: `{% include "flashcards/_pagination.html" %}`
9. Include delete modal: `{% include "flashcards/_delete_confirmation_modal.html" %}`

### Step 6: Create Flashcard List Items Partial

1. Create `flashcards/templates/flashcards/_flashcard_list_items.html`
2. Add `<ul class="list-group">`
3. Loop through flashcards: `{% for flashcard in flashcards %}`
4. Include `_flashcard_item.html` for each: `{% include "flashcards/_flashcard_item.html" %}`
5. Close list and add pagination include

### Step 7: Create Flashcard Item Partial

1. Create `flashcards/templates/flashcards/_flashcard_item.html`
2. Add `<li class="list-group-item">`
3. Add flex container for layout
4. Add truncated front text: `{{ flashcard.front|truncatechars:100 }}`
5. Add button group with Edit and Delete buttons
6. Edit button: `<a href="{% url 'flashcards:edit' flashcard.id %}" class="btn btn-sm btn-outline-primary">Edit</a>`
7. Delete button with modal trigger: `<button data-bs-toggle="modal" data-bs-target="#deleteModal" data-flashcard-id="{{ flashcard.id }}">Delete</button>`

### Step 8: Create Empty State Partial

1. Create `flashcards/templates/flashcards/_empty_state.html`
2. Add centered container with padding
3. Add friendly message: "You don't have any flashcards yet."
4. Add encouragement text: "Get started by generating flashcards from your study materials or creating one manually."
5. Add CTA buttons for Generate and Create
6. Style with Bootstrap classes: `text-center`, `py-5`, `text-muted`

### Step 9: Create Pagination Partial

1. Create `flashcards/templates/flashcards/_pagination.html`
2. Check if pagination needed: `{% if is_paginated %}`
3. Add `<nav aria-label="Flashcard pagination">`
4. Add `<ul class="pagination justify-content-center">`
5. Add Previous button with HTMX attributes:
   - `hx-get="{% url 'flashcards:list' %}?page={{ page_obj.previous_page_number }}"`
   - `hx-target="#flashcard-list-container"`
   - `hx-swap="innerHTML"`
   - `hx-push-url="true"`
   - Disable if no previous page
6. Loop through page numbers with current page highlighted
7. Add Next button with similar HTMX attributes
8. Add loading indicator reference: `hx-indicator="#loading-indicator"`

### Step 10: Create Delete Confirmation Modal

1. Create `flashcards/templates/flashcards/_delete_confirmation_modal.html`
2. Add Bootstrap modal structure with `id="deleteModal"`
3. Add modal header with title "Delete Flashcard"
4. Add modal body with message: "Delete this flashcard? This cannot be undone."
5. Add modal footer with Cancel and Delete buttons
6. Cancel button: `data-bs-dismiss="modal"`
7. Delete button: `id="confirmDeleteBtn"` (HTMX attributes set dynamically)

### Step 11: Create Alert Partial

1. Create `flashcards/templates/flashcards/_alert.html`
2. Loop through Django messages: `{% if messages %}`
3. Create Bootstrap alert for each message
4. Set alert level class: `alert-{{ message.tags }}`
5. Add dismiss button: `<button class="btn-close" data-bs-dismiss="alert">`
6. Style with `alert-dismissible fade show`

### Step 12: Add JavaScript for Modal

1. Create `flashcards/static/flashcards/js/flashcard-list.js`
2. Add event listener for modal show event
3. Get flashcard ID from triggering button's data attribute
4. Set HTMX delete URL on confirm button
5. Re-process HTMX attributes with `htmx.process()`
6. Add event listener for modal close after successful delete

**Implementation:**
```javascript
document.getElementById('deleteModal').addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;
  const flashcardId = button.getAttribute('data-flashcard-id');
  const deleteBtn = document.getElementById('confirmDeleteBtn');
  deleteBtn.setAttribute('hx-delete', `/flashcards/${flashcardId}/delete/`);
  deleteBtn.setAttribute('hx-target', '#flashcard-list-container');
  deleteBtn.setAttribute('hx-swap', 'innerHTML');
  htmx.process(deleteBtn);
});

// Close modal after successful delete
document.body.addEventListener('htmx:afterRequest', function(event) {
  if (event.detail.successful) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
    if (modal) modal.hide();
  }
});
```

### Step 13: Configure HTMX

1. Add HTMX script to base.html: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
2. Configure HTMX CSRF token handling in meta tag:
   ```html
   <meta name="htmx-config" content='{"getCacheBusterParam": false}'>
   ```
3. Ensure CSRF token available for HTMX: Django's `{% csrf_token %}` tag

### Step 14: Add Loading Indicators

1. Create loading spinner component in base.html or list template
2. Add `id="loading-indicator"` with `htmx-indicator` class
3. Style to be hidden by default, shown during HTMX requests
4. Reference in HTMX attributes: `hx-indicator="#loading-indicator"`

### Step 15: Test View Rendering

1. Run Django development server: `uv run python manage.py runserver`
2. Navigate to `/flashcards/`
3. Test empty state (if no flashcards)
4. Create test flashcards via Django admin or Create view
5. Verify list displays with correct data
6. Check truncation works for long front text
7. Verify pagination appears if > 25 flashcards

### Step 16: Test HTMX Interactions

1. Test pagination: Click next/previous, verify HTMX swap works
2. Test page number clicks
3. Verify URL updates with `hx-push-url`
4. Test loading indicator appears during requests
5. Verify no full page reload on pagination

### Step 17: Test Delete Functionality

1. Click Delete button, verify modal opens
2. Click Cancel, verify modal closes without delete
3. Click Delete in modal, verify:
   - HTMX DELETE request sent
   - Flashcard removed from database
   - List updates to show remaining flashcards
   - Modal closes
   - Success message displays
4. Test deleting last flashcard, verify empty state shows

### Step 18: Test Error Scenarios

1. Test delete with network disconnected (mock error)
2. Test invalid page numbers
3. Test unauthorized delete (manually craft request)
4. Verify 404 for non-existent flashcards
5. Test CSRF validation (remove token, verify 403)

### Step 19: Add Accessibility Features

1. Add ARIA labels to buttons: `aria-label="Edit flashcard"`
2. Add ARIA labels to pagination: `aria-label="Flashcard pagination"`
3. Ensure modal has proper ARIA attributes (Bootstrap default)
4. Test keyboard navigation (Tab, Enter, Escape)
5. Test screen reader compatibility
6. Verify focus management on modal open/close

### Step 20: Style and Polish

1. Add custom CSS for flashcard list items if needed
2. Ensure Bootstrap spacing utilities used consistently
3. Add hover states for interactive elements
4. Ensure mobile responsiveness (Bootstrap grid)
5. Test on different screen sizes
6. Add transitions for smooth interactions
7. Ensure color contrast meets WCAG standards

### Step 21: Write Tests

1. Write unit tests for FlashcardListView:
   - Test queryset filtering by user
   - Test pagination
   - Test page_size validation
   - Test HTMX request detection
2. Write unit tests for FlashcardDeleteView:
   - Test successful delete
   - Test ownership validation
   - Test 404 for non-existent flashcard
3. Write integration tests:
   - Test full page load
   - Test pagination workflow
   - Test delete workflow
4. Run tests: `uv run pytest`

### Step 22: Documentation

1. Update project documentation with new view details
2. Document HTMX patterns used
3. Document template structure
4. Add comments to complex JavaScript
5. Update CHANGELOG.md with new feature

### Step 23: Code Review and Refinement

1. Review code for adherence to Django best practices
2. Check CODING_PRACTICES in CLAUDE.md
3. Ensure proper error handling throughout
4. Verify security best practices (CSRF, authentication, authorization)
5. Optimize database queries (use select_related/prefetch_related if needed)
6. Check for N+1 query issues

### Step 24: Final Testing

1. Test entire user workflow end-to-end
2. Test with different user accounts (isolation)
3. Test edge cases (no flashcards, 1 flashcard, many flashcards)
4. Test performance with large datasets
5. Test cross-browser compatibility (Chrome, Firefox, Safari)
6. Test mobile devices (responsive design)
7. Verify all acceptance criteria met from US-010

### Step 25: Deploy and Monitor

1. Commit changes with meaningful commit message
2. Push to repository
3. Deploy to staging environment
4. Run smoke tests on staging
5. Deploy to production
6. Monitor logs for errors
7. Gather user feedback
8. Iterate based on feedback and metrics
