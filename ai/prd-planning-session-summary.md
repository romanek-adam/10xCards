# PRD Planning Summary - 10xCards MVP

## Conversation Summary

### Decisions

#### Target Users and Scope
1. Primary target users: primary and secondary school students
2. This is a toy project that will not be used by real users
3. Privacy regulations (COPPA, GDPR) can be ignored
4. No teacher or parent account functionality - students only
5. No content moderation for inappropriate content

#### AI Flashcard Generation
6. AI provider: OpenRouter (experimental approach)
7. Cost considerations: completely ignored for MVP
8. Input text limit: 10,000 words maximum
9. Input format: plain text only
10. Number of cards generated: 5-10 flashcards per text input
11. Priority subjects: language learning, biology, chemistry, history
12. No user guidance options (e.g., "focus on vocabulary") - single text input only
13. No character counter or input validation displayed to users
14. Error handling: display user-friendly message and preserve input text on failure

#### Flashcard Data Structure
15. Flashcard fields: question and answer only (no tags, metadata, or additional fields)
16. Data model definition: handled separately, not part of PRD
17. No metadata displayed to users (keep interface completely clean)

#### Quality Measurement
18. Primary metric: 75% of AI-generated flashcards accepted by users
19. Secondary metric: 75% of flashcards created using AI
20. Feedback mechanism: thumbs up/down rating with specific feedback capability
21. Additional engagement metrics: ignored for MVP

#### Review and Acceptance Flow
22. Generated cards displayed: all on single page in a list format
23. Each card shows: question and answer with "Accept" and "Reject" buttons
24. Accept button: immediately saves flashcard to database
25. Reject button: does nothing, card is simply discarded
26. No edit option during review - cards can only be accepted or rejected

#### Spaced Repetition System
27. Algorithm: leverage existing open-source library (specific library TBD, not part of PRD)
28. Study session length: 10-15 cards OR 5-10 minutes
29. Session progress: not persistent - users start over if they exit
30. Self-rating system: 2-button approach ("Got it" and "Needs review")
31. Study flow: question displayed first, "Show Answer" button reveals answer, then rating buttons appear
32. After session completion: show completion message with "Study More" and "Done" options
33. When no cards due: display "You're all caught up! Next review in X hours" with no additional functionality

#### User Interface and Navigation
34. Core views: Browse All Flashcards, Generate Flashcards, Create Flashcard (manual)
35. Navigation: simple top menu bar with links to 3 core views + due card count + "Start Session" button
36. No dashboard view - replaced by Browse view with integrated navigation
37. First-time user experience: redirect to Browse All Flashcards page (empty), no special onboarding
38. No tutorial, no tooltips, no onboarding - bare minimum MVP

#### Browse and Organization
39. Organization: flat list of all flashcards, no folders, tags, or categories
40. Session card selection: randomly chosen from all available flashcards
41. Display format: question text truncated to ~100 characters with "Edit" and "Delete" buttons
42. No search or filter functionality
43. Simple pagination: 25-50 cards per page, sorted by creation date (newest first)

#### Editing and Deletion
44. Edit mode: explicit "Save" and "Cancel" buttons required
45. After saving: return to Browse view with success message
46. Delete action: show confirmation dialog ("Delete this flashcard? This cannot be undone")
47. Confirmation options: "Delete" and "Cancel" buttons

#### Manual Flashcard Creation
48. Required fields: both question and answer (cannot be empty or whitespace only)
49. No minimum character length requirements
50. Validation errors: simple messages like "Question is required"

#### Authentication and User Management
51. Authentication method: email/password only
52. Required features: basic password reset and email verification
53. Deferred features: 2FA, SSO, OAuth options

#### Monetization and Pricing
54. Completely ignored in MVP - no pricing model, no paid features, no freemium

#### Usage Limits
55. No limits on flashcard creation or AI generations in MVP

#### Technical Stack
56. Backend: Python/Django
57. Frontend: HTMX, Bootstrap, limited JavaScript (if at all)
58. Database: PostgreSQL
59. CI/CD: GitHub
60. Cloud hosting: TBD (ignored for MVP planning)

#### Timeline
61. Development duration: 3-4 months
62. Month 1: Core flashcard CRUD and user accounts
63. Month 2: AI integration and testing
64. Month 3: Spaced repetition integration
65. Month 4: Beta testing and refinement
66. Buffer time included for unexpected challenges

---

### Matched Recommendations

Based on the conversation decisions, the following recommendations were accepted and should be incorporated into the PRD:

1. **AI Generation Volume**: Generate 5-10 flashcards per text input as a default, with the exact number depending on content richness.

2. **Quality Feedback Mechanism**: Implement a feedback mechanism where users can rate flashcards (thumbs up/down) and provide specific feedback.

3. **Spaced Repetition Algorithm**: Leverage an existing algorithm from an open-source library (specific library to be evaluated during development).

4. **Input Constraints**: Limit input to 10,000 words, plain text only.

5. **Authentication**: Implement email/password authentication with basic password reset functionality and email verification. Defer advanced features like 2FA and SSO to post-MVP phases.

6. **Development Timeline**: 3-4 month MVP development cycle with milestones: Month 1 - Core flashcard CRUD and user accounts, Month 2 - AI integration and testing, Month 3 - Spaced repetition integration, Month 4 - Beta testing and refinement.

7. **Subject Focus**: Focus initially on core subjects with clear factual content: language learning, biology, chemistry, and history where flashcards are most effective.

8. **Study Sessions**: Design short, focused study sessions (10-15 cards or 5-10 minutes) suitable for student attention spans.

9. **Rating System**: Use a simple 2-button system: "Got it" and "Needs review". This feeds into the spaced repetition algorithm without overwhelming users with complexity.

10. **Post-Session Flow**: After completing a session, show a simple completion message with two options: "Study More" (start another session) and "Done" (return to main view).

11. **No Cards Due**: If no cards are due, display a message like "You're all caught up! Next review in X hours."

12. **Core Views**: Three core views: 1) Browse All Flashcards (flat list with edit/delete actions), 2) Generate Flashcards (paste text interface), 3) Create Flashcard (manual entry form). Keep navigation minimal with a simple top menu bar.

13. **Clean Interface**: Hide all metadata in the main study flow to reduce cognitive load.

14. **Single Input Mode**: For MVP, use a single text input without additional options. The AI prompt can be designed to create a balanced mix of question types.

15. **First-Time Users**: After registration/login, redirect to the Browse All Flashcards page which will be empty initially.

16. **Review Presentation**: Display all generated flashcards on a single page in a list format, each showing question/answer with "Accept" and "Reject" buttons.

17. **Edit Flow**: Use explicit "Save" and "Cancel" buttons when editing. This prevents accidental changes and gives users clear control.

18. **Browse Display**: For MVP, display a simple paginated list (25-50 cards per page) sorted by creation date (newest first).

19. **Study Flow**: Show the question first with a "Show Answer" button. After clicking, reveal the answer and present the "Got it" / "Needs review" buttons.

20. **Delete Confirmation**: Show a simple confirmation dialog: "Delete this flashcard? This cannot be undone." with "Delete" and "Cancel" buttons.

21. **Form Validation**: Make both question and answer fields required (cannot be empty or only whitespace). No minimum length requirements beyond that.

22. **Error Handling**: Display a user-friendly error message: "Couldn't generate flashcards right now. Please try again." Keep the input text in the form so users don't lose their work.

23. **No Usage Limits**: For the toy MVP, don't impose any limits on flashcard creation or AI generations.

24. **Browse List Items**: Display just the question text (truncated to ~100 characters if long) with "Edit" and "Delete" action buttons beside each item.

---

### PRD Planning Summary

#### Product Overview

10xCards is an educational flashcard application designed to solve the problem of time-consuming manual flashcard creation, which discourages students from using spaced repetition as an effective learning method. The MVP targets primary and secondary school students and focuses on AI-powered flashcard generation combined with a proven spaced repetition algorithm.

This is a toy project for learning purposes and will not handle real user data or comply with privacy regulations.

#### Main Functional Requirements

**1. User Authentication and Account Management**
- Email/password registration and login
- Email verification process
- Password reset functionality
- Individual student accounts only (no teacher/parent oversight)

**2. AI Flashcard Generation**
- Text input interface accepting up to 10,000 words of plain text
- Integration with OpenRouter API for AI-powered generation
- Generation of 5-10 flashcards per text input
- Optimized for language learning, biology, chemistry, and history content
- Review interface showing all generated cards simultaneously
- Binary acceptance mechanism: "Accept" (save to database) or "Reject" (discard)
- User-friendly error handling with input preservation on failure

**3. Manual Flashcard Creation**
- Simple form with question and answer fields
- Required field validation (both fields must be non-empty)
- No minimum character length constraints
- Explicit save/cancel actions

**4. Flashcard Management (Browse View)**
- Flat list of all user flashcards
- Display question text truncated to 100 characters
- Edit functionality with explicit save/cancel
- Delete functionality with confirmation dialog
- Pagination (25-50 cards per page)
- Sorted by creation date (newest first)
- No search, filter, or organizational features

**5. Spaced Repetition Study System**
- Study sessions of 10-15 cards or 5-10 minutes duration
- Random card selection from entire collection
- Question-first display with "Show Answer" button
- Simple 2-button rating system: "Got it" and "Needs review"
- Non-persistent session progress (restart on exit)
- Post-session options: "Study More" or "Done"
- "All caught up" message when no cards due for review
- Due card counter in top navigation

**6. Navigation and Interface**
- Top menu bar with three core views: Browse, Generate, Create
- Due card count display in navigation
- "Start Session" button in navigation
- Minimalist interface with no metadata display
- No onboarding, tutorials, or tooltips

#### Key User Stories and Usage Paths

**User Story 1: AI-Powered Flashcard Creation**
- As a student studying biology, I want to paste my textbook notes into the app so that flashcards are automatically generated for me
- Acceptance: User pastes text (up to 10,000 words) → AI generates 5-10 flashcards → User reviews and accepts/rejects cards → Accepted cards appear in Browse view

**User Story 2: Manual Flashcard Creation**
- As a student, I want to manually create flashcards for concepts I'm struggling with so that I can customize my study materials
- Acceptance: User navigates to Create view → Fills in question and answer → Saves → Card appears in Browse view

**User Story 3: Spaced Repetition Study Session**
- As a student, I want to study due flashcards using spaced repetition so that I can efficiently retain information long-term
- Acceptance: User sees due count in navigation → Clicks "Start Session" → Reviews 10-15 cards one at a time → Rates each as "Got it" or "Needs review" → Sees completion message → Chooses to continue or finish

**User Story 4: Flashcard Management**
- As a student, I want to view, edit, and delete my flashcards so that I can maintain an accurate study collection
- Acceptance: User navigates to Browse view → Sees list of all flashcards → Clicks Edit to modify → Saves changes → Or clicks Delete with confirmation → Card removed from collection

**User Story 5: First-Time User Experience**
- As a new user, I want to quickly start using the app so that I can begin creating flashcards immediately
- Acceptance: User registers → Verifies email → Logs in → Lands on empty Browse page → Clicks "Generate Flashcards" in navigation → Pastes content → Reviews and accepts cards → Starts first study session

#### Success Criteria and Measurement

**Primary Success Metrics:**
1. **75% AI Acceptance Rate**: 75% of AI-generated flashcards are accepted by users during the review process
2. **75% AI Usage Rate**: Users create 75% of their total flashcards using AI generation (vs. manual creation)

**Measurement Approach:**
- Track flashcard creation method (AI-generated vs. manual) in database
- Record accept/reject decisions during AI generation review
- Implement thumbs up/down feedback mechanism for ongoing quality assessment
- Allow users to provide specific feedback on flashcard quality

**Additional Metrics (Deferred):**
- Daily/weekly active users
- Study session frequency and duration
- User retention rates
- Cards reviewed per session

#### Technical Constraints and Boundaries

**In Scope:**
- Python/Django backend implementation
- HTMX + Bootstrap frontend with minimal JavaScript
- PostgreSQL database
- GitHub for version control and CI/CD
- Integration with OpenRouter API for AI generation
- Integration with open-source spaced repetition library

**Out of Scope:**
- Cloud hosting decisions (TBD)
- Specific database schema design (handled separately)
- Specific spaced repetition library selection (to be evaluated)
- Cost optimization and API expense management
- Mobile applications (web only)
- Advanced authentication (OAuth, 2FA, SSO)
- Privacy compliance (COPPA, GDPR)
- Content moderation
- Advanced metrics and analytics
- Search and filter functionality
- Organizational features (tags, folders, categories)
- Multi-format import (PDF, DOCX)
- Flashcard sharing between users
- Educational platform integrations
- Custom advanced spaced repetition algorithms

#### Design Principles

1. **Minimal Viable Product**: Focus on core functionality only, defer all non-essential features
2. **Simplicity First**: No tutorials, tooltips, or complex UI elements
3. **Student-Centric**: Interface designed for primary and secondary school students
4. **AI-First Workflow**: Encourage AI generation as primary creation method
5. **Clean Interface**: Hide technical details and metadata from users
6. **Explicit Actions**: Require explicit save/cancel/delete confirmations to prevent accidents
7. **No Feature Bloat**: Flat structure with no organizational complexity

---

### Unresolved Issues

The following items require further clarification or decision-making during the development phase:

1. **Spaced Repetition Library Selection**: Specific open-source library to be evaluated and selected (e.g., fsrs, supermemo2). Requires technical evaluation of Python libraries, licensing review, and compatibility testing.

2. **OpenRouter Configuration**: Specific model selection, API configuration, and prompt engineering approach need to be defined during implementation phase.

3. **AI Prompt Design**: Exact prompts for generating flashcards optimized for each subject area (language learning, biology, chemistry, history) need to be developed and tested.

4. **Session Termination Logic**: Clarify exact logic for ending a study session - is it 10-15 cards AND 5-10 minutes (whichever comes first), OR 10-15 cards OR 5-10 minutes? Current assumption: flexible based on card count primarily.

5. **"Study More" Behavior**: When user clicks "Study More" after completing a session, should the next session include the same cards they just reviewed (if they marked some as "Needs review"), or only cards that are algorithmically due? Current assumption: follow spaced repetition algorithm strictly.

6. **Email Service Provider**: For email verification and password reset, which email service will be used (e.g., SendGrid, AWS SES, SMTP)? Needs decision during implementation.

7. **Cloud Hosting Platform**: Final decision on cloud hosting provider deferred but will be needed before deployment (e.g., Heroku, DigitalOcean, AWS, Railway).

8. **Accept Button Batch Behavior**: When multiple cards are shown after AI generation, does each "Accept" button immediately save that individual card, or is there a final "Save All Accepted" button? Current decision indicates individual Accept buttons save immediately.

9. **Database Schema Details**: While data model is defined separately from PRD, coordination needed to ensure all functional requirements are captured in database design (user accounts, flashcards, review history, ratings).

10. **Error Recovery Strategy**: For AI generation failures, should there be retry logic, fallback models, or just display error? Current decision: display error and preserve input.

11. **Pagination Defaults**: Exact number for cards per page in Browse view - 25, 50, or user-configurable? Current guidance: 25-50, needs specific decision.

12. **Review History Retention**: How long should spaced repetition review history be retained? Is there any data retention or deletion policy needed even for toy project?

---

## Next Steps

This PRD planning summary should be used as the foundation for:

1. **Full PRD Development**: Expand this summary into a complete Product Requirements Document with detailed specifications, wireframes, and technical requirements
2. **Technical Architecture Design**: Use the technical stack decisions and constraints to design system architecture
3. **Database Schema Design**: Create detailed schema based on functional requirements and out-of-scope technical design work
4. **Development Sprint Planning**: Use the 4-month timeline and functional requirements to plan development sprints
5. **Library and Tool Evaluation**: Research and select specific spaced repetition library and finalize OpenRouter configuration
6. **UI/UX Wireframing**: Create wireframes for the three core views and study session flow
7. **API Integration Planning**: Design integration approach for OpenRouter and selected spaced repetition library

---

**Document Version**: 1.0
**Date**: 2025-10-09
**Status**: Planning Complete - Ready for Full PRD Development
