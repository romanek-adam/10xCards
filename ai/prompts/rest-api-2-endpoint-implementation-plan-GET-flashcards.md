You are an experienced software architect whose task is to create a detailed implementation plan for a REST API endpoint. Your plan will guide the development team in effectively and correctly implementing this endpoint.

Before we begin, review the following information:

1. Route API specification:
<route_api_specification>
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
</route_api_specification>

2. Related Django models:
<related_django_models>
@flashcards/core/models.py
</related_django_models>

3. Tech stack:
<tech_stack>
@ai/tech-stack.md
</tech_stack>

Your task is to create a comprehensive implementation plan for the REST API endpoint. Before delivering the final plan, use <analysis> tags to analyze the information and outline your approach. In this analysis, ensure that:

1. Summarize key points of the API specification.
2. List required and optional parameters from the API specification.
3. List necessary Models.
4. Consider how to extract logic to a service (existing or new, if it doesn't exist).
5. Plan input validation according to the API endpoint specification and Django model validations.
6. Determine how to log errors in the error table (if applicable).
7. Identify potential security threats based on the API specification and tech stack.
8. Outline potential error scenarios and corresponding status codes.

After conducting the analysis, create a detailed implementation plan in Markdown format. The plan should contain the following sections:

1. Endpoint Overview
2. Request Details
3. Response Details
4. Data Flow
5. Security Considerations
6. Error Handling
7. Performance
8. Implementation Steps

Throughout the plan, ensure that you:
- Use correct API status codes:
  - 200 for successful read
  - 201 for successful creation
  - 400 for invalid input
  - 401 for unauthorized access
  - 404 for not found resources
  - 500 for server-side errors
- Adapt to the provided tech stack

The final output should be a well-organized implementation plan in Markdown format. Here's an example of what the output should look like:

``markdown
# API Endpoint Implementation Plan: [Endpoint Name]

## 1. Endpoint Overview
[Brief description of endpoint purpose and functionality]

## 2. Request Details
- HTTP Method: [GET/POST/PUT/DELETE]
- URL Structure: [URL pattern]
- Parameters:
  - Required: [List of required parameters]
  - Optional: [List of optional parameters]
- Request Body: [Request body structure, if applicable]

## 3. Used Types
[DTOs and Command Models necessary for implementation]

## 3. Response Details
[Expected response structure and status codes]

## 4. Data Flow
[Description of data flow, including ORM calls and/or interactions with external services]

## 5. Security Considerations
[Authentication, authorization, and data validation details]

## 6. Error Handling
[List of potential errors and how to handle them]

## 7. Performance Considerations
[Potential bottlenecks and optimization strategies]

## 8. Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]
...
```

The final output should consist solely of the implementation plan in markdown format and should not duplicate or repeat any work done in the analysis section.

Remember to save your implementation plan as ai/rest-api-endpoint-implementation-plan.md. Ensure the plan is detailed, clear, and provides comprehensive guidance for the development team.
