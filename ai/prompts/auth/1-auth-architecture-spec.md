You are an experienced full-stack web developer specializing in documenting user registration, login, and password recovery modules. Develop a detailed architecture for this functionality based on requirements from @ai/prd.md (US-001 to US-005) and the stack from @ai/tech-stack.md.

Ensure compatibility with remaining requirements - you cannot break existing application behavior described in the documentation.

The specification should include the following elements:

1. USER INTERFACE ARCHITECTURE
- Detailed description of the frontend layer (pages, components, and layouts in auth and non-auth mode)
- Precise separation of responsibilities between frontend and backend, taking into account their integration with navigation, and user actions
- Description of validation cases and error messages
- Handling of the most important scenarios

2. BACKEND LOGIC
- Structure of API endpoints and data models consistent with new interface elements
- Input data validation mechanism
- Exception handling
- Server-side rendering method for selected pages

3. AUTHENTICATION SYSTEM
- Details of the implementation of authentication for registration, login, logout, and account recovery functionality

Present key findings in the form of a descriptive technical specification - without implementation details (no references to source file or specific code parts), but with indication of individual components, modules, services, and contracts. After completing the task, create a file ai/auth-spec.md and add the entire specification there.
