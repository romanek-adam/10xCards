As a senior frontend developer, your task is to create a detailed implementation plan for a new view in a web application. This plan should be comprehensive and clear enough for another frontend developer to implement the view correctly and efficiently.

First, review the following information:

1. Product Requirements Document (PRD):
<prd>
@ai/prd.md
</prd>

2. View Description:
<view_description>
### 2.7 My Flashcards Page

**Path:** `/flashcards/` (default authenticated landing page)
**Main Purpose:** Display paginated list of all user's flashcards with management actions.
**Key Information:** Flashcard list (front text truncated to ~100 chars), edit/delete buttons per card, pagination controls, total count.
**Key Components:** Bootstrap list-group for cards, CTA button group (Generate/Create), pagination component, delete confirmation modal, success/error alerts.
**UX:** Empty state with friendly message and prominent CTAs, newest-first sorting, visual feedback on delete, loading states for HTMX requests.
**Accessibility:** Semantic list structure, button labels, keyboard navigation, modal focus trap.
**Security:** User-isolated queryset, CSRF protection on delete, 404 for unauthorized access.
</view_description>

3. User Stories:
<user_stories>
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
</user_stories>

4. Endpoint Description:
<endpoint_description>
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

</endpoint_description>

5. Endpoint Implementation:
<endpoint_implementation>
@flashcards/api/views/flashcards.py
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

After conducting the analysis, provide an implementation plan in Markdown format with the following sections:

1. Overview: Brief summary of the view and its purpose.
2. View Routing: Specify the path where the view should be accessible.
3. Component Structure: Outline of main components and their hierarchy.
4. Component Details: For each component, describe:
 - Component description, its purpose and what it consists of
 - Main HTML elements and child components that build the component
 - Handled events
 - Validation conditions (detailed conditions, according to API)
 - Types (DTO and ViewModel) required by the component
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

## 7. API Integration
[Explanation of integration with provided endpoint, indication of request and response types]

## 8. User Interactions
[Detailed description of user interactions]

## 9. Conditions and Validation
[Detailed description of conditions and their validation]

## 10. Error Handling
[Description of handling potential errors]

## 11. Implementation Steps
1. [Step 1]
2. [Step 2]
3. [...]
```

Begin analysis and planning now. Your final output should consist solely of the implementation plan in English in markdown format, which you will save in the `ai/ui/{view-name}-view-implementation-plan.md` file and should not duplicate or repeat any work done in the implementation breakdown.
