# Product Requirements Document (PRD) - 10xCards

## 1. Product Overview

10xCards is an educational flashcard application designed to make spaced repetition accessible to students by automating the time-consuming process of flashcard creation. The MVP targets primary and secondary school students and combines AI-powered flashcard generation with a proven spaced repetition algorithm to help students retain information more effectively.

The MVP follows a minimalist design philosophy with three core views: My Flashcards, Generate Flashcards, and Create Flashcard. The interface emphasizes simplicity with no onboarding tutorials, tooltips, or complex organizational features.

## 2. User Problem

Students from primary and secondary school face a significant barrier to effective learning through spaced repetition: the manual creation of high-quality educational flashcards is extremely time-consuming.

10xCards solves this problem by using AI to automatically generate high-quality flashcards from student input text, reducing the time from hours to minutes while maintaining the effectiveness of the spaced repetition learning method.

## 3. Functional Requirements

### 3.1 User Authentication and Account Management

- Email/password registration system with new user account creation
- User login functionality with email and password validation
- Email verification process requiring users to confirm their email address
- Password reset functionality allowing users to recover access via email
- Individual student accounts only (no teacher or parent account types)

### 3.2 AI Flashcard Generation

- Text input interface accepting up to 10,000 words of plain text
- Generation of 5-10 flashcards per text input automatically
- Single input mode without additional user configuration options
- Review interface displaying all generated cards simultaneously on a single page
- Each card in review showing front and back in editable form with "Accept" and "Reject" buttons
- Accept action immediately saves flashcard to user's database
- Reject action discards the flashcard without saving
- User-friendly error handling displaying "Couldn't generate flashcards right now. Please try again."
- Input text preservation in form on generation failure to prevent data loss
- No character counter or input validation display to users

### 3.3 Manual Flashcard Creation

- Simple creation form with two fields: front and back
- Required field validation ensuring both front and back are non-empty
- No minimum character length requirements beyond non-empty validation
- Explicit "Save" and "Cancel" buttons requiring user action
- Success message display after successful save
- Automatic return to My Flashcards view after save
- Simple validation error messages like "Front is required" or "Back is required"

### 3.4 Flashcard Management ("My Flashcards" View)

- Flat list display of all user flashcards without folders or categories
- Front text display truncated to approximately 100 characters
- "Edit" and "Delete" action buttons beside each flashcard item
- Edit functionality opening form with current front and back
- Explicit "Save" and "Cancel" buttons in edit mode
- Return to Browse view with success message after saving edits
- Delete action triggering confirmation dialog: "Delete this flashcard? This cannot be undone."
- Confirmation dialog with "Delete" and "Cancel" buttons
- Immediate removal from collection upon delete confirmation
- Pagination with 25-50 cards per page
- Sorting by creation date with newest first
- No search, filter, tag, or category functionality
- No metadata display to users

### 3.5 Spaced Repetition Study System Integration

- Automatic card assignment to Spaced Repetition Study schedule (based on an existing algorithm)
- Lack of extra metadata and notifications in MVP

### 3.6 Navigation and User Interface

- Top menu bar with three core view links: My Flashcards, Generate Flashcards, Create Flashcard
- Due card count display in navigation bar
- First-time user redirect to My Flashcards page after login (empty initially)
- Minimalist interface with no metadata, timestamps, or technical details visible
- No onboarding flow, tutorials, or tooltips
- Clean, simple layout optimized for student users


## 4. Product Boundaries

### 4.1 In Scope for MVP

- Integration with OpenRouter API for AI flashcard generation
- Integration with open-source spaced repetition library
- Web application only (no mobile apps)
- Email/password authentication with email verification and password reset
- Basic flashcard CRUD operations
- AI-powered flashcard generation from plain text
- Spaced repetition study sessions with simple rating system
- Flat list organization of flashcards
- Pagination for browsing flashcards
- No usage limits on flashcard creation or AI generations

### 4.2 Out of Scope for MVP

- Cost optimization and API expense management
- Mobile applications (iOS, Android)
- Advanced authentication features (OAuth, 2FA, SSO)
- Content moderation for inappropriate content
- Teacher or parent account functionality
- Advanced analytics and engagement metrics beyond success criteria
- Search functionality in flashcard list
- Filter functionality in flashcard list
- Organizational features (tags, folders, categories, decks)
- Multi-format import capabilities (PDF, DOCX, images)
- Flashcard sharing between users or public flashcard sets
- Integration with other educational platforms
- Custom or advanced spaced repetition algorithms (like SuperMemo, Anki)
- Monetization features, pricing models, or freemium tiers
- User guidance options during AI generation (e.g., "focus on vocabulary")
- Persistent session progress (save and resume later)
- Dashboard view with statistics and insights
- Customizable study session length
- Card difficulty settings or manual scheduling
- Progress tracking visualizations
- Streak tracking or gamification features
- Dark mode or theme customization
- Accessibility features beyond browser defaults
- Internationalization or multi-language support
- Bulk operations (select all, delete multiple)
- Card history or version control
- Rich text formatting in front and back
- Image support in flashcards
- Audio or pronunciation features
- Collaborative study features
- Export functionality for flashcards

## 5. User Stories

### US-001: User Registration
Title: Create New User Account

Description: As a new student user, I want to register for an account using my email and password so that I can start creating and studying flashcards.

Acceptance Criteria:
- Registration form displays email and password input fields
- Email field validates proper email format
- Password field requires minimum security standards
- Form includes "Register" button to submit
- System creates new user account in database upon valid submission
- System sends verification email to provided email address
- User cannot log in until email is verified
- System displays appropriate error messages for invalid inputs (invalid email format, weak password, email already registered)
- System redirects user to email verification pending page after successful registration

### US-002: Email Verification
Title: Verify Email Address

Description: As a newly registered user, I want to verify my email address so that I can activate my account and log in.

Acceptance Criteria:
- User receives email with verification link after registration
- Verification email contains clear instructions and clickable link
- Clicking verification link marks user account as verified in database
- System displays success message after successful verification
- Verified users can proceed to login
- Unverified users see message directing them to check email when attempting login
- Verification links expire after reasonable time period
- System provides option to resend verification email

### US-003: User Login
Title: Log In to Existing Account

Description: As a registered user with verified email, I want to log in using my email and password so that I can access my flashcards and study using them.

Acceptance Criteria:
- Login form displays email and password input fields
- Form includes "Login" button to submit
- System validates email and password against database
- Successful login creates user session and redirects to My Flashcards page
- System displays error message for invalid credentials
- System prevents login for unverified email addresses with appropriate message
- User session persists across page navigations
- System provides "Forgot Password" link on login page

### US-004: Password Reset Request
Title: Request Password Reset

Description: As a user who forgot my password, I want to request a password reset via email so that I can regain access to my account.

Acceptance Criteria:
- "Forgot Password" link accessible from login page
- Password reset form displays email input field
- Form includes "Send Reset Link" button
- System sends password reset email to provided address if account exists
- System displays same confirmation message whether email exists or not (security best practice)
- Reset email contains secure time-limited reset link
- Reset link expires after reasonable time period
- User can request multiple reset emails if needed

### US-005: Password Reset Completion
Title: Complete Password Reset

Description: As a user who requested password reset, I want to set a new password via the reset link so that I can access my account again.

Acceptance Criteria:
- Clicking reset link opens password reset form
- Form displays new password and confirm password fields
- Form includes "Reset Password" button
- System validates new password meets security standards
- System validates new password matches confirmation
- System updates password in database upon valid submission
- System displays success message and redirects to login page
- System shows error for expired or invalid reset links
- User can log in immediately with new password after reset

### US-006: AI Flashcard Generation from Text
Title: Generate Flashcards Using AI

Description: As a student studying a subject, I want to paste my study material text into the app so that flashcards are automatically generated for me without manual effort.

Acceptance Criteria:
- Generate Flashcards view displays large text input area
- Text input accepts up to 10,000 words of plain text
- Form includes "Generate" button to submit
- System sends user input to an LLM API to generate flashcards
- AI generates between 5 and 10 flashcards based on input content
- Generated flashcards contain only fron and back fields
- System displays all generated flashcards on review page after generation
- Generation completes within reasonable time frame
- If LLM API fails or times out, system displays user-friendly message: "Couldn't generate flashcards right now. Please try again."

### US-007: Review AI-Generated Flashcards
Title: Review and Accept/Reject Generated Flashcards

Description: As a student who generated flashcards using AI, I want to review all generated cards and decide which ones to keep so that I only save high-quality flashcards to my collection.

Acceptance Criteria:
- All generated flashcards display on single review page in list format
- Each flashcard shows complete front and back text, in editable form
- Each flashcard includes "Accept" button
- Each flashcard includes "Reject" button
- Clicking "Accept" immediately saves flashcard to user's database
- Clicking "Reject" discards flashcard without saving
- System provides visual feedback when card is accepted (e.g., confirmation, removal from review list)

### US-009: Manual Flashcard Creation
Title: Create Flashcard Manually

Description: As a student, I want to manually create flashcards for specific concepts or edge cases so that I can customize my study materials beyond AI generation.

Acceptance Criteria:
- Create Flashcard view displays form with front and back input fields
- Both fields are empty by default (not pre-filled)
- Form includes "Save" button
- Form includes "Cancel" button
- Clicking "Save" validates both fields are non-empty
- System displays validation error message if front or back are empty
- Upon valid submission, system saves flashcard to database
- System redirects to My Flashcards view after save
- Clicking "Cancel" discards input and returns to Browse view without saving

### US-010: My Flashcards
Title: View All My Flashcards

Description: As a student, I want to view a list of all my flashcards so that I can see what I've created and manage my collection.

Acceptance Criteria:
- My Flashcards view displays flat list of all user's flashcards
- Each list item shows question text truncated to approximately 100 characters
- Long questions end with ellipsis (...) to indicate truncation
- Each list item includes "Edit" button
- Each list item includes "Delete" button
- Flashcards are sorted by creation date with newest first
- List displays all cards on a single page (no pagination)
- Empty state displays when user has no flashcards
- No metadata (creation date, timestamps, tags) visible to user
- No search or filter functionality available
- No folders, categories, or organizational structure

### US-011: Edit Existing Flashcard
Title: Edit Flashcard Question or Answer

Description: As a student, I want to edit my existing flashcards so that I can correct errors or improve the quality of my study materials.

Acceptance Criteria:
- Clicking "Edit" button on flashcard opens edit form
- Edit form displays front and back fields pre-filled with current text
- Form includes "Save" button
- Form includes "Cancel" button
- User can modify both front and back text
- Clicking "Save" validates both fields are non-empty
- System displays validation error if front or back are empty
- Upon valid submission, system updates flashcard in database
- System displays success message after save
- System returns to My Flashcards view after save
- Clicking "Cancel" discards changes and returns to Browse view without updating
- Original flashcard remains unchanged if user cancels

### US-012: Delete Flashcard with Confirmation
Title: Delete Unwanted Flashcard

Description: As a student, I want to delete flashcards I no longer need so that I can maintain a clean and relevant collection.

Acceptance Criteria:
- Clicking "Delete" button on flashcard triggers confirmation dialog
- Confirmation dialog displays message: "Delete this flashcard? This cannot be undone."
- Dialog includes "Delete" button
- Dialog includes "Cancel" button
- Clicking "Delete" in dialog immediately removes flashcard from database
- Deleted flashcard disappears from Browse list
- Clicking "Cancel" in dialog closes dialog without deleting
- Flashcard remains in collection if user cancels
- No undo functionality available after deletion
- Deleted flashcards are permanently removed

### US-013: Study Session With Spaced Repetition
Title: Study Session With Spaced Repetition

Description: As a logged-in student, I want the created flashcards to be available in the "Study Session" view based on an external algorithm, so that I can practice and retain information using spaced repetition.

Acceptance Criteria:
- Navigation bar includes "Study Session" button
- In the "Study Session" view the algorithm prepares a study session with flashcards
- Initially the front is displayed, interaction from user shows the back
- User provides feedback on whether she internalised the flashcard
- Then the algorithm shows the next flashcard from the session

### US-019: User Logout
Title: Log Out of Account

Description: As a logged-in user, I want to log out of my account so that I can secure my session when using shared devices.

Acceptance Criteria:
- Navigation menu includes "Logout" link or button
- Clicking logout terminates user session
- System redirects to login page after logout
- User must log in again to access flashcards
- Session data is cleared securely
- User cannot access protected pages without logging in again

### US-021: View Account Security
Title: Secure User Session Management

Description: As a user of the application, I want my account and data to be secure so that only I can access my flashcards.

Acceptance Criteria:
- All authenticated routes require valid user session
- Unauthenticated users redirect to login page when accessing protected routes
- User can only view and modify their own flashcards

## 6. Success Metrics

### Primary Success Metrics

The MVP will be considered successful based on these two critical metrics:

1. AI Acceptance Rate: 75% or more of AI-generated flashcards are accepted by users during the review process
   - Measurement: Track accept vs. reject button clicks during AI generation review
   - Target: At least 75 out of every 100 AI-generated flashcards are accepted
   - Rationale: High acceptance rate validates AI generation quality and reduces user friction

2. AI Usage Rate: 75% or more of total flashcards in the system are created via AI generation (versus manual creation)
   - Measurement: Track creation method (AI vs. manual) in database for all flashcards
   - Target: At least 75 out of every 100 flashcards created using AI generation
   - Rationale: High AI usage validates that the core value proposition (reducing manual effort) resonates with users

### Measurement Implementation

The following mechanisms will be implemented to measure success metrics:

1. Database Tracking:
   - Record creation method (AI-generated vs. manual) for each flashcard
   - Store accept/reject decisions during AI generation review process
   - Track timestamps for all flashcard creation events

2. Reporting Capability:
   - Calculate AI acceptance rate: (Accepted cards / Total generated cards) × 100
   - Calculate AI usage rate: (AI-generated cards / Total cards) × 100
