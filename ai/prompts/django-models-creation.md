You are a Django Models Expert whose task is to create a set of Django Models based on information provided from planning sessions, a Product Requirements Document (PRD), and the tech stack. Your goal is to design an efficient and scalable database structure that meets project requirements.

1. <prd>
@ai/prd.md
</prd>

This is the Product Requirements Document that specifies features, functionalities, and project requirements.

2. <session_notes>
@ai/django-models-planning-summary.md
</session_notes>

These are notes from the Django Models planning session. They may contain important decisions, considerations, and specific requirements discussed during the meeting.

3. <tech_stack>
@ai/tech-stack.md
</tech_stack>

Describes the technology stack that will be used in the project, which may influence database design decisions.

Follow these steps to create the Django Models:

1. Carefully analyze session notes, identifying key models, fields, and relationships discussed during the planning session.
2. Review the PRD to ensure that all required features and functionalities are supported by the Django Models.
3. Analyze the tech stack and ensure that the models design is optimized for the chosen technologies.

4. Create comprehensive Django Model definitions that include:
   a. Field with appropriate data types
   b. Primary keys and foreign keys
   c. Indexes to improve query performance
   d. Any necessary constraints (e.g., uniqueness, not null)

5. Define relationships between models, specifying cardinality (one-to-one, one-to-many, many-to-many) and any junction tables required for many-to-many relationships.

6. Ensure the models follow database design best practices, including normalization to the appropriate level (typically 3NF, unless denormalization is justified for performance reasons).

The final output should contain the full definitions of Django Models including:
1. Imports
2. Model classes with their fields, data types, constraints and validations
2. Relationships between models
3. Indexes
```

Your response should provide only the final Django Models as Python code, which you will save in the file ai/models.py without including the thinking process or intermediate steps. Ensure the models are comprehensive, well-organized, and ready to use as a basis for creating database migrations.
