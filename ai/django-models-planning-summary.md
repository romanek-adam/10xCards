# Django Models Planning Summary for 10xCards MVP

## Overview

The database schema supports three core MVP features: AI flashcard generation, manual flashcard creation, and flashcard management. The design prioritizes tracking success metrics (75% AI acceptance rate and 75% AI usage rate) while maintaining simplicity and security.

## Decisions Made

1. **Flashcard Creation Method Tracking**: Add `creation_method` field to `Flashcard` model with three choices: AI_FULL (accepted without edits), AI_EDITED (modified before accepting), and MANUAL (manually created). Include nullable `ai_session` foreign key to `AIGenerationSession`.

2. **AI Generation Session Tracking**: Create `AIGenerationSession` model to track AI generation attempts and accept/reject decisions for success metrics calculation.

3. **Store Rejected Flashcards**: Create `GeneratedFlashcard` model to store all generated flashcards (both accepted and rejected) for calculating AI acceptance rate metric.

4. **Flashcard Field Constraints**: Use CharField with max_length=200 for `front` and max_length=500 for `back`. Apply restrictions using Django Field validators (not database-level CHECK constraints).

5. **Spaced Repetition (Deferred)**: Do not implement spaced repetition algorithm fields or study session tracking in this phase - will be covered in future development.

6. **Study Session Tracking (Deferred)**: No `StudyResponse` model needed at this time - deferred with spaced repetition implementation.

7. **Indexing Strategy**: Add composite index on (`user_id`, `-created_at`) to `Flashcard` model for efficient browsing and pagination.

8. **Deletion Strategy**: Implement hard delete (permanent removal) for flashcards without soft delete or grace period.

9. **Row-Level Security**: Use Django ORM filters (`flashcard.objects.filter(user=request.user)`) and custom model manager (`FlashcardManager`) for automatic user filtering. Do NOT implement database-level PostgreSQL RLS policies.

10. **AI Input Text Storage**: Store input text in `AIGenerationSession` using TextField. Do NOT add `character_count` field.

11. **Automatic Timestamps**: Add `created_at` (auto_now_add=True) and `updated_at` (auto_now=True) to `Flashcard` model for sorting and audit trails (not displayed to users).

12. **User Deletion Cascade**: Set `on_delete=models.CASCADE` for `user` ForeignKey in `Flashcard` model to automatically delete all flashcards when user account is deleted.

13. **Session Deletion Cascade**: Use `on_delete=models.CASCADE` for `session` ForeignKey in `GeneratedFlashcard` model. Keep sessions indefinitely for analytics.

14. **LLM Model Tracking**: Do NOT track which specific LLM model or provider was used for generation.

15. **Error Information Storage**: Add `error_message` (TextField, nullable), `error_code` (CharField, nullable), and `api_response_time_ms` (IntegerField, nullable) to `AIGenerationSession` for debugging and monitoring.

16. **Edit History Tracking**: Store both original and edited versions in `GeneratedFlashcard`: `original_front`, `original_back`, `edited_front` (nullable), `edited_back` (nullable) to distinguish AI_FULL vs AI_EDITED creation methods.

17. **Session Model Indexes**: Add composite index on (`user_id`, `-created_at`) and single index on `status` to `AIGenerationSession` for analytics queries.

18. **Input Text Validation**: No database character limit on `input_text` field.

19. **Session-Flashcard Relationship**: Add `ai_session` (ForeignKey to AIGenerationSession, nullable, on_delete=models.SET_NULL, related_name='accepted_flashcards') to `Flashcard` model.

20. **User Model Extension**: Use existing custom `flashcards.users.User` model without additional fields. Keep simple for MVP.

## Core Models

### 1. Flashcard Model

The central model storing user flashcards with support for both AI-generated and manually-created cards.

**Fields:**
- `user` (ForeignKey to User, on_delete=CASCADE)
- `front` (CharField, max_length=200)
- `back` (CharField, max_length=500)
- `creation_method` (CharField with choices: 'ai_full', 'ai_edited', 'manual')
- `ai_session` (ForeignKey to AIGenerationSession, nullable, on_delete=SET_NULL, related_name='accepted_flashcards')
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Features:**
- Custom manager: `FlashcardManager` for automatic user filtering (row-level security)
- Composite index on (`user`, `-created_at`) for efficient browse/pagination queries
- Hard delete implementation (permanent removal)
- Character limits enforced via Django validators (not database CHECK constraints)
- Automatic timestamp tracking for sorting and audit trails

### 2. AIGenerationSession Model

Tracks each AI generation attempt for analytics and debugging.

**Fields:**
- `user` (ForeignKey to User, on_delete=CASCADE)
- `input_text` (TextField, max_length=10,000)
- `status` (CharField with choices: 'pending', 'completed', 'failed')
- `error_message` (TextField, nullable)
- `error_code` (CharField, max_length=50, nullable)
- `api_response_time_ms` (IntegerField, nullable)
- `created_at` (DateTimeField, auto_now_add=True)

**Features:**
- Indexes: composite on (`user`, `-created_at`), single on `status`, single on `created_at`
- Sessions retained indefinitely for success metrics calculation
- Error information for debugging API issues
- Performance tracking via response time field

### 3. GeneratedFlashcard Model

Stores ALL flashcards generated by AI (both accepted and rejected) for metrics.

**Fields:**
- `session` (ForeignKey to AIGenerationSession, on_delete=CASCADE)
- `original_front` (CharField, max_length=200)
- `original_back` (CharField, max_length=500)
- `edited_front` (CharField, max_length=200, nullable)
- `edited_back` (CharField, max_length=500, nullable)
- `was_accepted` (BooleanField)
- `reviewed_at` (DateTimeField, nullable)

**Features:**
- Preserves original AI-generated text
- Tracks user modifications for distinguishing AI_FULL vs AI_EDITED
- Records accept/reject decision
- Enables calculation of AI acceptance rate metric
- Cascades delete with parent session

## Model Relationships

```
User (existing custom model)
  ├─→ Flashcard (CASCADE delete, many flashcards per user)
  │    └─→ AIGenerationSession (SET_NULL, optional link for AI-generated cards)
  │
  └─→ AIGenerationSession (CASCADE delete, many sessions per user)
       └─→ GeneratedFlashcard (CASCADE delete, 5-10 generated cards per session)
```

## Key Design Decisions

### Field Validation Strategy
Use Django field validators for max_length constraint rather than database CHECK constraint. This provides better error messages and flexibility.

### Deletion Strategy
- Hard delete for flashcards (permanent removal per PRD)
- Cascade deletes when users are removed
- SET_NULL for flashcard→session relationship to preserve flashcards if sessions are cleaned up

### Security Approach
- Application-level security via Django ORM filters and custom model manager
- All queries automatically filtered by user
- No database-level PostgreSQL RLS policies

### Indexing Strategy
- Composite indexes on (user, -created_at) for main browse queries
- Additional indexes on AIGenerationSession.status and created_at for analytics
- Optimized for pagination and sorting by newest first

### Edit Tracking
Store both original AI-generated content and user edits to distinguish between AI_FULL and AI_EDITED creation methods.

### Error Handling
Comprehensive error tracking in AIGenerationSession (message, code, response time) for debugging while displaying user-friendly messages in UI.

## Success Metrics Implementation

The schema directly supports the two critical MVP success metrics:

### 1. AI Acceptance Rate (75% target)
- **Calculated from:** GeneratedFlashcard records
- **Formula:** (COUNT where was_accepted=True) / (COUNT total) × 100
- **Tracking:** Per session and aggregate across all sessions

### 2. AI Usage Rate (75% target)
- **Calculated from:** Flashcard.creation_method distribution
- **Formula:** (COUNT where creation_method IN ['ai_full', 'ai_edited']) / (COUNT total) × 100
- **Purpose:** Tracks whether AI is actually reducing manual effort

## Deferred Features

The following features are intentionally excluded from this phase and will be addressed in future development:

- Spaced repetition algorithm fields (next_review_date, interval_days, ease_factor, repetitions)
- StudyResponse model for tracking study session interactions
- LLM model and provider tracking
- Character count field on input_text
- Soft delete functionality
- PostgreSQL Row Level Security policies
- User model extensions

## Security Considerations

### Application-Level Security
- Custom `FlashcardManager` that automatically filters by user
- Django ORM filters in all views: `flashcard.objects.filter(user=request.user)`
- Foreign key constraints for data integrity
- No direct SQL queries that bypass Django ORM

### Data Integrity
- Cascade deletes prevent orphaned records
- SET_NULL relationships preserve important data
- Non-nullable fields enforce required data
- Foreign key constraints maintain referential integrity

## Scalability Considerations

### Indexing
- Composite indexes optimize primary query patterns
- Single-column indexes support analytics queries
- All index fields match common WHERE and ORDER BY clauses

### Performance
- Text fields in PostgreSQL handle variable-length content efficiently
- No denormalization needed for MVP scale
- Indexes support pagination without performance degradation

### Storage
- Historical session data retention has minimal storage impact
- Hard deletes prevent table bloat from deleted records

## Unresolved Issues

No critical unresolved issues. All core model requirements have been addressed based on the PRD and user decisions.

### Minor Considerations for Implementation Phase

1. **Exact wording for CharField choices** (e.g., 'ai_full' vs 'AI_FULL' - recommend lowercase with display names)

2. **Related_name conventions** for reverse relationships (recommend consistent naming pattern)

3. **__str__ methods** for admin interface (recommended for debugging)

4. **Admin interface configuration** for viewing/debugging sessions and generated cards (recommended but not specified)

## Next Steps

1. Implement the three core models in `flashcards/models.py`
2. Create custom `FlashcardManager` for user filtering
3. Generate and review Django migrations
4. Configure Django admin for debugging
5. Write model tests to verify relationships and constraints
6. Implement views and forms that use these models

## References

- Product Requirements Document: `ai/prd.md`
- Tech Stack: `ai/tech-stack.md`
- Django Models Planning Conversation: This document summarizes all decisions
