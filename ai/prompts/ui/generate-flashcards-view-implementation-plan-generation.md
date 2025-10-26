As a senior frontend developer, your task is to create a detailed implementation plan for a new view in a web application. This plan should be comprehensive and clear enough for another frontend developer to implement the view correctly and efficiently.

First, review the following information:

1. Product Requirements Document (PRD):
<prd>
@ai/prd.md
</prd>

2. View Description:
<view_description>
### 2.10 Generate Flashcards Page

**Path:** `/flashcards/generate/`
**Main Purpose:** Accept text input for AI-powered flashcard generation.
**Key Information:** Large textarea for input text (max 10,000 chars), generate button.
**Key Components:** Bootstrap form with large textarea (15+ rows), loading spinner overlay, error alert with input preservation.
**UX:** No character counter (server-side validation only), loading message "Generating flashcards... This may take up to 30 seconds", disabled button during processing, input preserved on failure.
**Accessibility:** Textarea label, loading state announced, error messages.
**Security:** Server-side text length validation, rate limiting on API calls, CSRF protection.

### 2.11 Generate Flashcards (Review) Page

**Path:** `/flashcards/generate/`
**Main Purpose:** Review AI-generated flashcards and accept/reject each one.
**Key Information:** Stack of 5-10 generated flashcards with editable front/back, accept/reject buttons per card.
**Key Components:** Vertical stack of Bootstrap cards, each with textarea/contenteditable front/back, button group (Accept: success, Reject: danger), visual feedback on actions.
**UX:** All cards displayed simultaneously, inline editing capability, accept saves to database (with creation_method: ai_full or ai_edited based on edits), reject removes from DOM, return to My Flashcards via navbar after review.
**Accessibility:** Card structure semantic, edit fields labeled, button actions clear.
**Security:** Session ownership validation, CSRF on accept POST, XSS prevention via Django template escaping.
</view_description>

3. User Stories:
<user_stories>
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

</user_stories>

4. Service Description:
<endpoint_description>
class FlashcardGenerationService:
    """Service for generating flashcards from user input text using AI.

    This service creates AIGenerationSession records for analytics tracking
    and returns generated flashcard proposals without persisting them to the
    Flashcard model (users accept/reject proposals in a separate flow).
</endpoint_description>

5. Endpoint Implementation:
<endpoint_implementation>
@flashcards/core/services/flashcard_generation.py
</endpoint_implementation>

6. Model Definitions:
<model_definitions>
@flashcards/core/models.py
</model_definitions>

7. Tech Stack:
<tech_stack>
@ai/tech-stack.md
</tech_stack>

Before creating the final implementation plan, conduct analysis and planning inside <implementation_breakdown> tags in your thinking block. This section can be quite long, as it's important to be thorough.

In your implementation breakdown, execute the following steps:
1. For each input section (PRD, User Stories, Endpoint Description, Endpoint Implementation, Type Definitions, Tech Stack):
  - Summarize key points
 - List any requirements or constraints
 - Note any potential challenges or important issues
2. Extract and list key requirements from the PRD
3. List all needed main components, along with a brief description of their purpose, needed types, handled events, and validation conditions
4. Create a high-level component tree diagram
5. Identify required DTOs and custom ViewModel types for each view component. Explain these new types in detail, breaking down their fields and associated types.
6. Identify potential state variables and custom hooks, explaining their purpose and how they'll be used
7. List required API calls and corresponding frontend actions
8. Map each user story to specific implementation details, components, or functions
9. List user interactions and their expected outcomes
10. List conditions required by the API and how to verify them at the component level
11. Identify potential error scenarios and suggest how to handle them
12. List potential challenges related to implementing this view and suggest possible solutions

After conducting the analysis, provide an high-level implementation plan in Markdown format with the following sections:

1. Overview: Brief summary of the view and its purpose.
2. View Routing: Specify the path where the view should be accessible.
3. Component Structure: Outline of main components and their hierarchy.
4. Component Details: For each component, describe:
 - Component description, its purpose and what it consists of
 - Main HTML elements and child components that build the component
 - Handled events
 - Validation conditions (detailed conditions, according to API)
 - Types (DTO and/or ViewModel) required by the component
 - Props that the component accepts from parent (component interface)
5. Types: Detailed description of types required for view implementation, including exact breakdown of any new types or view models by fields and types.
6. State Management: Detailed description of how state is managed in the view, specifying whether a custom hook is required.
7. API Integration: Explanation of how to integrate with the provided endpoint. Precisely indicate request and response types.
8. User Interactions: Detailed description of user interactions and how to handle them.
9. Conditions and Validation: Describe what conditions are verified by the interface, which components they concern, and how they affect the interface state
10. Error Handling: Description of how to handle potential errors or edge cases.
11. Implementation Steps: Step-by-step guide for implementing the view.

Ensure your plan is consistent with the PRD, user stories, and includes the provided tech stack.

The final output should be in English and saved in a file named .ai/{view-name}-view-implementation-plan.md. Do not include any analysis and planning in the final output.

Here's an example of what the output file should look like (content is to be replaced):

```markdown
# View Implementation Plan [View Name]

## 1. Overview
[Brief description of the view and its purpose]

## 2. View Routing
[Path where the view should be accessible]

## 3. Component Structure
[Outline of main components and their hierarchy]

## 4. Component Details
### [Component Name 1]
- Component description [description]
- Main elements: [description]
- Handled interactions: [list]
- Handled validation: [list, detailed]
- Types: [list]
- Props: [list]

### [Component Name 2]
[...]

## 5. Types
[Detailed description of required types]

## 6. State Management
[Description of state management in the view]

## 7. User Interactions
[Detailed description of user interactions]

## 8. Conditions and Validation
[Detailed description of conditions and their validation]

## 9. Error Handling
[Description of handling potential errors]

## 10. Implementation Steps
1. [Step 1]
2. [Step 2]
3. [...]
```

Begin analysis and planning now. Your final output should consist solely of the implementation plan in English in Markdown format, which you will save in the `ai/ui/{view-name}-view-implementation-plan.md` file and should not duplicate or repeat any work done in the implementation breakdown.

The output should contain no more than 200 lines.
