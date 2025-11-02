# Authentication Architecture Specification

## Overview

This document describes the authentication architecture for 10xCards, covering user registration, email verification, login, logout, and password recovery functionality. The architecture leverages django-allauth as the authentication foundation and integrates with the existing HTMX + Bootstrap 5 frontend.

**Alignment with PRD:**
This specification has been validated against the PRD (prd.md) to ensure all User Stories (US-001 through US-005, US-019, US-021) can be implemented. Key MVP scope clarifications:
- Navigation includes only three core flashcard views: My Flashcards, Generate Flashcards, Create Flashcard
- User profile functionality exists in codebase but is NOT linked in MVP navigation (out of scope)
- "Remember Me" checkbox on login is an optional enhancement beyond strict PRD requirements
- All authentication-related User Stories are fully implementable with this architecture

## 1. USER INTERFACE ARCHITECTURE

### 1.1 Frontend Layer Components

#### 1.1.1 Pages and Views

**Registration Page (`/accounts/signup/`)**
- Entry point for new users to create accounts
- Server-rendered Django template using allauth's signup view
- Extends the application's entrance layout template
- Accessible only to unauthenticated users (authenticated users redirected to home)
- URL provided by django-allauth routing

**Login Page (`/accounts/login/`)**
- Entry point for existing users to authenticate
- Server-rendered Django template using allauth's login view
- Extends the application's entrance layout template
- Includes link to password reset flow
- Accessible only to unauthenticated users
- URL provided by django-allauth routing

**Email Verification Pending Page (`/accounts/confirm-email/`)**
- Informational page shown after successful registration
- Notifies user to check their email for verification link
- Provides option to resend verification email
- Server-rendered template
- Accessible to both authenticated and unauthenticated users

**Email Verification Confirmation Page (`/accounts/confirm-email/<key>/`)**
- Landing page when user clicks verification link in email
- Validates the verification token
- Displays success message and redirects to login on successful verification
- Shows error message for expired or invalid tokens
- Server-rendered template

**Password Reset Request Page (`/accounts/password/reset/`)**
- Form for users to request password reset via email
- Accepts email address input
- Server-rendered Django template using allauth's password reset view
- Accessible only to unauthenticated users
- URL provided by django-allauth routing

**Password Reset Email Sent Page (`/accounts/password/reset/done/`)**
- Confirmation page after reset request submitted
- Generic message displayed regardless of email existence (security best practice)
- Server-rendered template
- Accessible to unauthenticated users

**Password Reset Confirmation Page (`/accounts/password/reset/key/<uidb36>-<key>/`)**
- Form for setting new password via emailed reset link
- Validates reset token and expiration
- Accepts new password and confirmation fields
- Server-rendered Django template
- Shows error for expired or invalid tokens
- URL provided by django-allauth routing

**Logout Page (`/accounts/logout/`)**
- Terminates user session
- Can be GET request (immediate logout) or POST with confirmation
- Redirects to login page after logout
- Accessible only to authenticated users
- URL provided by django-allauth routing

#### 1.1.2 Navigation Integration

**Unauthenticated State:**
- Navigation bar displays "Sign Up" link (routes to `/accounts/signup/`)
- Navigation bar displays "Sign In" link (routes to `/accounts/login/`)
- No flashcard-related navigation items visible

**Authenticated State:**
- Navigation bar displays "My Flashcards" link
- Navigation bar displays "Generate Flashcards" link
- Navigation bar displays "Create Flashcard" link
- Navigation bar displays "Sign Out" link (routes to `/accounts/logout/`)
- "Sign Up" and "Sign In" links removed from navigation

**Session Behavior:**
- Session persists across all page navigations
- Session maintained via Django's session framework (cookie-based)
- HTMX requests include CSRF token in headers for security

#### 1.1.3 Form Components

**Registration Form Fields:**
- Email field (required, validated for proper format)
- Password field (required, minimum security standards enforced)
- Password confirmation field (required, must match password)
- Submit button labeled "Register" or "Sign Up"
- Link to login page for existing users

**Login Form Fields:**
- Email field (required)
- Password field (required)
- "Remember Me" checkbox (optional enhancement, extends session duration - not explicitly required by PRD)
- Submit button labeled "Login" or "Sign In"
- Link to password reset page ("Forgot Password?")
- Link to registration page for new users

**Password Reset Request Form:**
- Email field (required)
- Submit button labeled "Send Reset Link" or "Reset Password"
- Link back to login page

**Password Reset Confirmation Form:**
- New password field (required, validated against password policies)
- Confirm new password field (required, must match new password)
- Submit button labeled "Reset Password" or "Change Password"

#### 1.1.4 Validation and Error Handling

**Client-Side Validation:**
- HTML5 form validation for email format (type="email")
- Required field validation
- Password confirmation matching (handled by allauth forms)
- Minimal JavaScript validation to maintain simplicity

**Server-Side Validation:**
All critical validation performed on backend:
- Email format validation (RFC 5322 compliant)
- Email uniqueness check against existing users
- Password strength requirements (Django password validators):
  - Minimum 8 characters (MinimumLengthValidator)
  - Not too similar to user attributes (UserAttributeSimilarityValidator)
  - Not a commonly used password (CommonPasswordValidator)
  - Not entirely numeric (NumericPasswordValidator)
- Password confirmation matching
- Reset token validity and expiration
- Verification link validity and expiration

**Error Messages:**
Registration errors:
- "Please enter a valid email address" (invalid email format)
- "This email has already been registered" (duplicate email)
- "Password is too short" (minimum length not met)
- "This password is too common" (common password detected)
- "Password and confirmation do not match" (mismatch)
- "Password is entirely numeric" (all numbers)

Login errors:
- "Please enter a valid email address and password" (generic error for invalid credentials)
- "Please verify your email before logging in" (unverified email)
- "Your account has been disabled" (inactive account)

Password reset errors:
- "This password reset link is invalid or has expired" (expired/invalid token)
- "Password is too short" (minimum length not met)
- "This password is too common" (common password detected)
- "Password and confirmation do not match" (mismatch)

Email verification errors:
- "This verification link is invalid or has already been used" (invalid/used token)
- "This verification link has expired" (expired token)

**Error Display Patterns:**
- Errors displayed using Bootstrap alert components (`.alert .alert-danger`)
- Form field-level errors shown below respective inputs
- Non-field errors (e.g., invalid credentials) shown at form top
- Error messages use crispy-forms Bootstrap 5 styling
- Errors persist until form resubmission

**Success Messages:**
- "Registration successful! Please check your email to verify your account."
- "Email verified successfully. You can now log in."
- "Password reset email sent. Please check your inbox."
- "Password changed successfully. You can now log in with your new password."
- Success messages displayed using Bootstrap `.alert .alert-success` components

### 1.2 Layout System

**Entrance Layout (`allauth/layouts/entrance.html`):**
- Used for registration, login, and password reset pages
- Clean, centered form design with minimal distractions
- Bootstrap 5 card component for form container
- Simple branding (10xCards logo/name)
- No navigation menu for primary actions
- Footer with links to other auth pages (sign up ↔ sign in)

**Base Layout (`base.html`):**
- Used for email verification confirmation pages
- Includes full navigation bar
- Displays authentication state in navigation
- Bootstrap container for content
- Message display area for alerts
- Responsive design with Bootstrap grid

### 1.3 User Interaction Flows

**Registration Flow:**
1. User clicks "Sign Up" in navigation → navigates to `/accounts/signup/`
2. User fills email and password fields → clicks "Register" button
3. Form validates on submit → server processes request
4. Success: redirect to email verification pending page
5. Error: form redisplays with error messages, email field preserved

**Email Verification Flow:**
1. User receives verification email → clicks verification link
2. Browser opens verification URL (`/accounts/confirm-email/<key>/`)
3. Server validates token → marks account as verified
4. Success page displayed → automatic redirect to login after 3 seconds (or manual link)
5. User can now log in

**Login Flow:**
1. User clicks "Sign In" in navigation → navigates to `/accounts/login/`
2. User enters email and password → clicks "Login" button
3. Form validates on submit → server authenticates user
4. Success: session created, redirect to "My Flashcards" page (via `users:redirect`)
5. Error: form redisplays with error message, email field preserved

**Password Reset Flow:**
1. User clicks "Forgot Password?" on login page → navigates to `/accounts/password/reset/`
2. User enters email → clicks "Send Reset Link" button
3. Server sends reset email (if account exists) → redirect to confirmation page
4. User receives email → clicks reset link
5. Browser opens reset form (`/accounts/password/reset/key/<uidb36>-<key>/`)
6. User enters new password and confirmation → clicks "Reset Password" button
7. Server validates and updates password → redirect to login with success message
8. User logs in with new password

**Logout Flow:**
1. User clicks "Sign Out" in navigation → POST request to `/accounts/logout/`
2. Server terminates session → redirect to login page
3. User sees login page with optional logout confirmation message

### 1.4 Responsive Design

**Mobile Considerations:**
- Bootstrap responsive grid adapts forms for mobile screens
- Form inputs use full width on small screens
- Touch-friendly button sizes (min 44x44px tap targets)
- Navbar collapses to hamburger menu on mobile
- Email and password inputs use appropriate mobile keyboard types

**Accessibility:**
- Semantic HTML form elements
- Proper label associations with inputs (for attribute)
- ARIA labels for screen readers where needed
- Focus states clearly visible for keyboard navigation
- Error messages announced to screen readers
- Sufficient color contrast ratios (WCAG AA compliance)

## 2. BACKEND LOGIC

### 2.1 API Endpoints and URL Routing

**Authentication Endpoints:**
All authentication URLs provided by django-allauth package under `/accounts/` prefix:

- `POST /accounts/signup/` - Process user registration
- `GET /accounts/signup/` - Display registration form
- `POST /accounts/login/` - Process user login
- `GET /accounts/login/` - Display login form
- `POST /accounts/logout/` - Process user logout
- `GET /accounts/logout/` - Display logout confirmation (optional)
- `GET /accounts/confirm-email/` - Display email verification pending page
- `POST /accounts/confirm-email/` - Resend verification email
- `GET /accounts/confirm-email/<key>/` - Verify email with token
- `GET /accounts/password/reset/` - Display password reset request form
- `POST /accounts/password/reset/` - Process password reset request
- `GET /accounts/password/reset/done/` - Display reset email sent confirmation
- `GET /accounts/password/reset/key/<uidb36>-<key>/` - Display password reset form
- `POST /accounts/password/reset/key/<uidb36>-<key>/` - Process password reset

**Custom User Management Endpoints:**
Provided by `flashcards.users` app under `/users/` prefix:

- `GET /users/~redirect/` - Login redirect handler (redirects to My Flashcards)

Note: User profile views (`/users/<int:pk>/`, `/users/~update/`) exist in the codebase but are not linked in navigation for MVP. Profile management functionality is out of scope for MVP.

**URL Configuration Structure:**
```
config/urls.py:
  /accounts/ → allauth.urls (all auth endpoints)
  /users/ → flashcards.users.urls (custom user endpoints)

flashcards/users/urls.py:
  ~redirect/ → UserRedirectView (used by LOGIN_REDIRECT_URL)
  ~update/ → UserUpdateView (exists but not linked in MVP navigation)
  <int:pk>/ → UserDetailView (exists but not linked in MVP navigation)
```

### 2.2 Data Models

**User Model (`flashcards.users.User`):**
- Extends Django's AbstractUser
- Email as primary identifier (USERNAME_FIELD = "email")
- No username field (username = None)
- Fields:
  - `id` (BigAutoField, primary key)
  - `email` (EmailField, unique, required)
  - `name` (CharField, optional, max 255 chars)
  - `password` (CharField, hashed)
  - `is_active` (BooleanField, default True)
  - `is_staff` (BooleanField, default False)
  - `is_superuser` (BooleanField, default False)
  - `date_joined` (DateTimeField, auto-set on creation)
  - `last_login` (DateTimeField, nullable)
- Custom manager: UserManager (handles email-based user creation)
- Password stored using Argon2 hashing algorithm
- No first_name or last_name fields (removed from AbstractUser)

**Email Address Model (django-allauth):**
- Managed by allauth.account app
- Tracks email verification status
- Fields:
  - `user` (ForeignKey to User)
  - `email` (EmailField)
  - `verified` (BooleanField)
  - `primary` (BooleanField)
- One-to-many relationship with User model
- Enforces email verification requirement

**Email Confirmation Model (django-allauth):**
- Managed by allauth.account app
- Stores email verification tokens
- Fields:
  - `email_address` (ForeignKey to EmailAddress)
  - `key` (CharField, unique token)
  - `created` (DateTimeField)
  - `sent` (DateTimeField, nullable)
- Tokens expire after configurable time period
- Single-use tokens (invalidated after verification)

### 2.3 Business Logic Layer

**User Registration Service:**
- Validates email uniqueness before creating user
- Creates User instance with hashed password (Argon2)
- Creates associated EmailAddress record (verified=False)
- Generates email verification token (EmailConfirmation)
- Sends verification email asynchronously
- Returns user instance or validation errors
- Handles duplicate email gracefully
- Enforces password strength requirements

**Email Verification Service:**
- Validates verification token from URL parameter
- Checks token expiration (default: 3 days)
- Marks EmailAddress as verified=True if valid
- Marks User as active (if configured)
- Returns success/failure status
- Handles expired tokens with clear messaging
- Allows resending verification emails

**Login Authentication Service:**
- Validates email and password combination
- Checks if user account is active
- Checks if email is verified (mandatory per settings)
- Creates Django session on successful authentication
- Logs last login timestamp
- Returns authenticated user or None
- Rate limiting handled by django-allauth (prevents brute force)
- Generic error messages for invalid credentials (security)

**Password Reset Service:**
- Validates email existence (silent failure for security)
- Generates time-limited password reset token
- Sends password reset email with reset link
- Token embedded in URL (`<uidb36>-<key>`)
- Returns success regardless of email existence
- Token expiration: configurable (default: 3 days)
- Tokens invalidated after single use

**Logout Service:**
- Terminates user session
- Clears session cookies
- Optionally requires POST with CSRF token (security)
- Redirects to login page after logout
- No complex state management needed

### 2.4 Input Validation

**Email Validation:**
- Format validation: RFC 5322 compliance via Django EmailField
- Uniqueness validation: database query to check existing users
- Case-insensitive matching (emails normalized to lowercase)
- Maximum length: 254 characters (EmailField default)
- Empty value rejection (required field)

**Password Validation:**
Enforced via Django's AUTH_PASSWORD_VALIDATORS:
- MinimumLengthValidator: minimum 8 characters
- UserAttributeSimilarityValidator: not too similar to email/name
- CommonPasswordValidator: checks against list of common passwords
- NumericPasswordValidator: prevents all-numeric passwords
- Password and confirmation must match
- Maximum length: 128 characters (security best practice)

**Token Validation:**
- Verification tokens: UUID-based, single-use, time-limited
- Reset tokens: UID + timestamped key, single-use, time-limited
- Constant-time comparison to prevent timing attacks
- Expired tokens rejected with specific error message
- Invalid tokens rejected with generic error message

### 2.5 Exception Handling

**User-Facing Errors:**
- ValidationError: form field validation failures → displayed as form errors
- IntegrityError (duplicate email): caught and converted to user-friendly message
- Token expiration: specific message indicating need to request new token
- Invalid credentials: generic message (no disclosure of which field is wrong)
- Rate limiting: temporary lockout with retry-after message

**System Errors:**
- SMTP failures: email sending errors logged, user sees generic "try again" message
- Database connection errors: handled by Django, displayed as 500 page
- Permission denied: 403 page for accessing unauthorized resources
- Not found: 404 page for invalid URLs
- All exceptions logged with full context for debugging

**Error Recovery:**
- Failed email sends: retry mechanism with exponential backoff
- Session expiration: automatic redirect to login with "session expired" message
- CSRF token errors: clear message prompting page refresh
- Form validation errors: preserve user input for correction

### 2.6 Server-Side Rendering

**Template Rendering Strategy:**
- All authentication pages server-rendered (no client-side SPA)
- Django template engine with Jinja2-style syntax
- Templates extend base layouts (entrance.html or base.html)
- Context data passed from views to templates
- Forms rendered using django-crispy-forms with Bootstrap 5 styling
- No HTMX for auth flows (full page loads for security clarity)

**Template Inheritance Structure:**
```
base.html (root)
  ├─ allauth/layouts/entrance.html (auth pages)
  │   ├─ account/signup.html
  │   ├─ account/login.html
  │   ├─ account/password_reset.html
  │   └─ account/password_reset_from_key.html
  └─ allauth/layouts/manage.html (account management)
      └─ account/email.html (manage email addresses)
```

**Context Data Provided:**
- Form instances with validation state
- Error messages (field-level and non-field)
- Success messages (via Django messages framework)
- CSRF tokens for all POST forms
- User authentication state (request.user)
- ACCOUNT_ALLOW_REGISTRATION setting (controls signup link visibility)

**Performance Considerations:**
- Template caching in production (Django template cache)
- Static file serving via WhiteNoise
- Database query optimization (select_related, prefetch_related)
- Session storage in database (default) or cache backend (Redis for scale)

## 3. AUTHENTICATION SYSTEM

### 3.1 Authentication Framework

**Django-allauth Integration:**
- Primary authentication provider for the application
- Provides complete user account management infrastructure
- Handles email verification, password reset, session management
- Customized via settings and custom adapters
- Version: latest stable (configured in requirements)

**Configuration Settings:**
```python
# config/settings/base.py

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Custom user model
AUTH_USER_MODEL = "users.User"

# Login/logout behavior
LOGIN_REDIRECT_URL = "users:redirect"  # Redirects to My Flashcards
LOGIN_URL = "account_login"

# django-allauth settings
ACCOUNT_ALLOW_REGISTRATION = True  # Can be toggled via env var
ACCOUNT_LOGIN_METHODS = {"email"}  # Email-only authentication
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # No username field
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Must verify before login
ACCOUNT_ADAPTER = "flashcards.users.adapters.AccountAdapter"
ACCOUNT_FORMS = {"signup": "flashcards.users.forms.UserSignupForm"}
```

### 3.2 Registration Implementation

**Registration Workflow:**
1. User submits registration form (email, password, password confirmation)
2. AccountAdapter.is_open_for_signup() checks if registration is allowed
3. UserSignupForm validates input fields
4. Password validators check password strength
5. Email uniqueness validated against User model
6. User instance created with email and hashed password
7. EmailAddress record created (verified=False, primary=True)
8. EmailConfirmation record created with unique verification key
9. Verification email sent via Django's email backend
10. User redirected to email verification pending page
11. User remains unauthenticated until email verified

**Custom Components:**
- UserSignupForm (flashcards.users.forms.UserSignupForm)
  - Extends allauth.account.forms.SignupForm
  - Adds any custom validation or fields if needed
  - Uses crispy-forms for Bootstrap 5 rendering

- AccountAdapter (flashcards.users.adapters.AccountAdapter)
  - Controls registration availability via ACCOUNT_ALLOW_REGISTRATION
  - Can customize email sending, validation, or user creation
  - Implements is_open_for_signup() method

**Security Measures:**
- Passwords hashed using Argon2 (memory-hard algorithm)
- CSRF protection on registration form
- Rate limiting on registration endpoint (via middleware)
- Email verification prevents automated account creation
- Password strength enforcement via Django validators

### 3.3 Login Implementation

**Login Workflow:**
1. User submits login form (email, password)
2. AuthenticationBackend validates credentials against User model
3. Password verified using Argon2 hasher (secure comparison)
4. Email verification status checked (must be verified)
5. User account active status checked (must be is_active=True)
6. Django session created upon successful authentication
7. last_login timestamp updated on User model
8. User redirected to LOGIN_REDIRECT_URL (users:redirect view)
9. UserRedirectView determines final destination (My Flashcards page)

**Session Management:**
- Django session framework (django.contrib.sessions)
- Session data stored in database (default) or cache (Redis for production)
- Session cookie: httponly, secure (HTTPS), samesite=Lax
- Session expiration: configurable (default: 2 weeks)
- "Remember Me" option extends session to 4 weeks
- Session cookie name: sessionid (Django default)

**Authentication State:**
- request.user populated by AuthenticationMiddleware
- request.user.is_authenticated boolean property
- Template access: {{ request.user }} in all templates
- View access: self.request.user in class-based views
- Middleware enforces authentication for protected views

**Security Measures:**
- Generic error messages for failed login (no email disclosure)
- Rate limiting on login attempts (django-allauth built-in)
- CSRF protection on login form
- Password comparison using constant-time algorithm
- Session fixation protection (new session ID after login)
- Secure session cookies in production (HTTPS only)

### 3.4 Logout Implementation

**Logout Workflow:**
1. User clicks "Sign Out" link in navigation
2. POST request sent to /accounts/logout/ (CSRF token included)
3. Django session invalidated and deleted
4. Session cookie cleared from browser
5. User marked as unauthenticated
6. Redirect to login page with optional confirmation message

**Security Measures:**
- Logout requires POST request with valid CSRF token (prevents CSRF logout attacks)
- Session completely destroyed (no partial logout)
- All session data cleared from storage
- Redirect prevents back-button access to authenticated pages

### 3.5 Email Verification Implementation

**Email Sending Configuration:**
- Email backend: SMTP (configurable via DJANGO_EMAIL_BACKEND)
- Production: configured SMTP server (SendGrid, AWS SES, etc.)
- Development: console backend or MailHog for testing
- Email timeout: 5 seconds (EMAIL_TIMEOUT setting)
- Async sending: optional Celery integration for production

**Verification Email Content:**
- From address: configured in DEFAULT_FROM_EMAIL setting
- Subject: "Please Confirm Your Email Address - 10xCards"
- Body includes:
  - Greeting with user's email
  - Clear call-to-action: "Verify Email Address" button/link
  - Plain text version for accessibility
  - Link expiration notice (valid for 3 days)
  - Contact information for support
- HTML and plain text versions rendered from templates

**Verification Token Security:**
- Tokens generated using Django's signing framework
- UUID-based key (128-bit entropy)
- Single-use tokens (invalidated after verification)
- Time-limited (default: 3 days, configurable)
- Stored in EmailConfirmation model
- Constant-time comparison for validation

**Resend Verification Email:**
- Available on email verification pending page
- Rate limited to prevent abuse (1 per minute per user)
- Invalidates previous tokens
- Generates new token and sends new email
- Same security properties as initial verification

### 3.6 Password Recovery Implementation

**Password Reset Request:**
1. User enters email on reset request form
2. System checks if email exists (silent check for security)
3. If exists: generate password reset token and send email
4. If not exists: display same success message (prevent email enumeration)
5. User redirected to "email sent" confirmation page
6. Reset email contains time-limited reset link

**Password Reset Token:**
- Generated using Django's PasswordResetTokenGenerator
- Token format: <uidb36>-<timestamped-key>
- uidb36: base36-encoded user ID
- key: HMAC-SHA256 hash of user ID, timestamp, password hash
- Time-limited: default 3 days (PASSWORD_RESET_TIMEOUT setting)
- Single-use: invalidated by password change
- Secure: includes user's password hash (invalidates if password changed)

**Password Reset Confirmation:**
1. User clicks reset link in email
2. View validates token (expiration, hash, user existence)
3. If valid: display password reset form
4. If invalid/expired: display error with option to request new reset
5. User enters new password and confirmation
6. Password validated against password validators
7. If valid: update user's password (hashed)
8. Invalidates all existing sessions for security
9. User redirected to login with success message

**Reset Email Content:**
- From address: configured in DEFAULT_FROM_EMAIL setting
- Subject: "Password Reset Request - 10xCards"
- Body includes:
  - Greeting
  - Clear call-to-action: "Reset Password" button/link
  - Security notice: ignore if not requested
  - Link expiration notice (valid for 3 days)
  - Contact information for support
- HTML and plain text versions

**Security Measures:**
- Silent failure for non-existent emails (prevent enumeration)
- Token tied to user's current password hash (auto-invalidates)
- Time-limited tokens (3 days default)
- Single-use tokens
- Rate limiting on reset requests (prevent abuse)
- All existing sessions invalidated after password reset
- CSRF protection on reset confirmation form

### 3.7 Session Security

**Session Configuration:**
- SESSION_COOKIE_HTTPONLY = True (prevents JavaScript access)
- SESSION_COOKIE_SECURE = True in production (HTTPS only)
- SESSION_COOKIE_SAMESITE = 'Lax' (CSRF protection)
- SESSION_COOKIE_AGE = 1209600 (2 weeks default)
- SESSION_SAVE_EVERY_REQUEST = False (performance)
- SESSION_ENGINE = 'django.contrib.sessions.backends.db' (default)

**Session Lifecycle:**
- Created on successful login
- Validated on every request by AuthenticationMiddleware
- Refreshed on activity (timestamp updated)
- Expired after inactivity period or absolute age
- Cleared on logout or password change
- Stored in database (sessions table)

**Session Data:**
- User ID (primary authentication identifier)
- Session key (random 32-character string)
- Session expiry date
- Minimal additional data (avoid storing sensitive info)

### 3.8 Authorization and Access Control

**View-Level Protection:**
- LoginRequiredMixin: enforces authentication for class-based views
- @login_required decorator: enforces authentication for function views
- Unauthenticated users redirected to LOGIN_URL
- Next parameter preserves intended destination

**Protected Resources:**
- My Flashcards page (requires authentication)
- Generate Flashcards page (requires authentication)
- Create Flashcard page (requires authentication)
- Study Session page (requires authentication)
- User profile pages (requires authentication)
- Admin interface (requires is_staff=True)

**Object-Level Authorization:**
- Users can only access their own flashcards
- Implemented via queryset filtering: Flashcard.objects.filter(owner=request.user)
- Attempts to access other users' flashcards return 404 (not 403, prevents enumeration)
- Admin users can access all objects (superuser check)

**CSRF Protection:**
- All POST, PUT, PATCH, DELETE requests require valid CSRF token
- Token included in forms via {% csrf_token %} template tag
- HTMX requests include token in hx-headers attribute
- Token validated by CsrfViewMiddleware
- Failed validation returns 403 Forbidden

### 3.9 Password Security

**Password Hashing:**
- Primary hasher: Argon2PasswordHasher (memory-hard, GPU-resistant)
- Fallback hashers: PBKDF2, BCrypt (for legacy compatibility)
- Argon2 parameters: time cost, memory cost, parallelism (Django defaults)
- Passwords automatically rehashed on login if using deprecated hasher

**Password Storage:**
- Format: `<algorithm>$<salt>$<hash>`
- Example: `argon2$argon2i$v=19$m=512,t=2,p=2$<salt>$<hash>`
- Never stored in plain text
- Never transmitted in plain text (HTTPS required)
- Never logged or cached

**Password Validation:**
- Enforced on registration and password change
- Validators:
  1. UserAttributeSimilarityValidator: prevents email/name in password
  2. MinimumLengthValidator: minimum 8 characters
  3. CommonPasswordValidator: checks 20,000 most common passwords
  4. NumericPasswordValidator: prevents all-numeric passwords
- Validation errors displayed to user with specific guidance

**Password Change:**
- Out of scope for MVP (no profile settings page)
- Future implementation will require:
  - Current password for verification
  - New password validation against all validators
  - Invalidation of all existing sessions (security measure)
  - Notification email to user's address

### 3.10 Integration Points

**With Flashcard Management:**
- Authenticated user automatically set as flashcard owner
- Flashcard queries filtered by request.user
- Study sessions scoped to authenticated user
- Generation history tracked per user

**With Navigation:**
- Navigation bar adapts based on authentication state
- Conditional rendering: {% if request.user.is_authenticated %}
- Dynamic links to user-specific pages (My Flashcards, Generate Flashcards, Create Flashcard)
- Logout link only visible when authenticated

**With Redirects:**
- LOGIN_REDIRECT_URL points to users:redirect view
- UserRedirectView determines appropriate landing page
- First-time users redirected to My Flashcards (empty state)
- Returning users redirected to My Flashcards (with content)
- Next parameter preserves intended destination after login

**With Email System:**
- Verification emails sent on registration
- Password reset emails sent on request
- Future: notification emails for study reminders (out of scope for MVP)
- Configured via Django email settings (SMTP backend)

**With Admin Interface:**
- Staff users can access Django admin
- Admin login flows through django-allauth (if DJANGO_ADMIN_FORCE_ALLAUTH=True)
- Superusers can manage users, emails, sessions
- Admin interface at /admin/ URL

### 3.11 Testing Considerations

**Unit Testing:**
- Test user registration with valid/invalid data
- Test email verification token generation and validation
- Test login with verified/unverified accounts
- Test password reset token generation and validation
- Test password hashing and verification
- Test session creation and management
- Test authorization checks on protected views

**Integration Testing:**
- Test complete registration-verification-login flow
- Test complete password reset flow
- Test logout and session invalidation
- Test email sending (using test email backend)
- Test CSRF protection on forms
- Test redirect behavior after authentication

**Security Testing:**
- Test rate limiting on login/registration
- Test CSRF token validation
- Test session fixation prevention
- Test password enumeration prevention
- Test token expiration enforcement
- Test constant-time comparison for tokens

## 4. ARCHITECTURAL DECISIONS

### 4.1 Why Django-allauth?

**Rationale:**
- Battle-tested authentication solution with 10+ years of development
- Comprehensive feature set covers all MVP requirements
- Active maintenance and security updates
- Excellent Django integration
- Extensible via adapters and custom forms
- Well-documented with large community
- Handles edge cases and security best practices
- Reduces development time and security risks

**Alternatives Considered:**
- Custom authentication: too time-consuming, security risk
- django.contrib.auth only: insufficient for email verification, password reset
- djoser: REST-focused, not ideal for server-rendered views

### 4.2 Email-Only Authentication

**Rationale:**
- Simpler user experience (one fewer field to remember)
- Email required anyway for verification and password reset
- Modern authentication best practice
- Prevents username enumeration attacks
- Reduces cognitive load for target audience (students)

**Implementation:**
- USERNAME_FIELD = "email" on User model
- ACCOUNT_USER_MODEL_USERNAME_FIELD = None in settings
- username field set to None on User model (type: ignore)

### 4.3 Mandatory Email Verification

**Rationale:**
- Prevents fake account creation (spam, abuse)
- Ensures user has access to email for password recovery
- Validates email address is legitimate
- Requirement explicitly stated in PRD (US-002)
- Industry best practice for user account systems

**Implementation:**
- ACCOUNT_EMAIL_VERIFICATION = "mandatory" in settings
- Login blocked until email verified
- Clear messaging to users about verification requirement

### 4.4 Server-Side Rendering for Auth

**Rationale:**
- Security: full page loads make CSRF protection clearer
- Simplicity: no client-side state management needed
- Compatibility: works with JavaScript disabled
- Consistency: matches rest of HTMX-based application
- SEO: authentication pages indexable (login, signup)

**Implementation:**
- Django template rendering for all auth pages
- No HTMX for authentication flows
- Traditional form submissions with POST requests
- Full page redirects after successful actions

### 4.5 Argon2 Password Hashing

**Rationale:**
- Winner of Password Hashing Competition (2015)
- Memory-hard algorithm (resistant to GPU/ASIC attacks)
- Configurable time/memory trade-offs
- Industry best practice for new applications
- Recommended by OWASP and security experts

**Implementation:**
- Argon2PasswordHasher as first PASSWORD_HASHER
- Automatic rehashing of legacy passwords on login
- Django handles all hashing complexity

## 5. COMPATIBILITY WITH EXISTING SYSTEM

### 5.1 Database Schema

**No Migrations Required:**
- User model already exists with email authentication
- EmailAddress model provided by django-allauth (already installed)
- EmailConfirmation model provided by django-allauth
- All necessary tables present from initial setup
- No changes to existing Flashcard, AIGenerationSession models

### 5.2 URL Structure

**No Conflicts:**
- /accounts/ prefix reserved for django-allauth
- /users/ prefix reserved for custom user views
- /flashcards/ prefix (implied) for flashcard functionality
- Clear separation of concerns in URL routing

### 5.3 Templates

**Extension Points:**
- Custom templates in flashcards/templates/account/ override allauth defaults
- Base templates (base.html, entrance.html) already exist
- Bootstrap 5 styling applied via crispy-forms
- Consistent look and feel with flashcard pages

### 5.4 Navigation

**Integration:**
- Navigation bar already conditional on authentication state
- Links to Sign Up, Sign In, Sign Out already present
- My Flashcards link visible only when authenticated
- No breaking changes to existing navigation

### 5.5 Middleware

**Compatibility:**
- AccountMiddleware already in MIDDLEWARE stack (allauth requirement)
- HtmxMiddleware compatible with authentication middleware
- SessionMiddleware, AuthenticationMiddleware, CsrfViewMiddleware already present
- Correct middleware ordering maintained

### 5.6 Static Files

**No Conflicts:**
- Authentication pages use same Bootstrap 5 CDN as flashcard pages
- No custom CSS required for auth pages (Bootstrap classes sufficient)
- No custom JavaScript required (server-side forms)

## 6. DEPLOYMENT CONSIDERATIONS

### 6.1 Environment Variables

**Required Settings:**
- DJANGO_ACCOUNT_ALLOW_REGISTRATION: controls registration availability
- DJANGO_EMAIL_BACKEND: email sending configuration
- EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD: SMTP settings
- DEFAULT_FROM_EMAIL: sender address for verification/reset emails
- SECRET_KEY: Django secret for session/token signing (already configured)
- DJANGO_ALLOWED_HOSTS: allowed domains for security
- DATABASE_URL: database connection string (already configured)

### 6.2 Email Configuration

**Production Setup:**
- Use dedicated email service (SendGrid, AWS SES, Mailgun)
- Configure SPF, DKIM, DMARC records for domain
- Monitor email deliverability and bounce rates
- Set up email templates with proper branding
- Test email sending before deployment

### 6.3 HTTPS Requirement

**Security:**
- SESSION_COOKIE_SECURE = True in production (HTTPS only cookies)
- CSRF_COOKIE_SECURE = True in production
- Password transmission requires HTTPS
- Email reset links require HTTPS
- DigitalOcean hosting should provide SSL certificate

### 6.4 Database Indexes

**Performance:**
- email field on User model already indexed (unique=True)
- session table indexed on session_key (Django default)
- EmailAddress table indexed on email (allauth default)
- No additional indexes required for MVP

### 6.5 Monitoring

**Operational Metrics:**
- Registration success/failure rate
- Email verification completion rate
- Login success/failure rate
- Password reset request rate
- Session duration statistics
- Email sending failures
- Authentication errors (logged to stderr/logging system)

## 7. FUTURE ENHANCEMENTS (Out of Scope for MVP)

- Multi-factor authentication (MFA)
- Social authentication (Google, Facebook)
- Password change functionality in user profile
- Account deletion functionality
- Email address change functionality
- Session management (view/revoke active sessions)
- Login history and security log
- Account activity notifications
- Configurable session timeout per user
- "Remember this device" functionality
- OAuth 2.0 API authentication for mobile apps
