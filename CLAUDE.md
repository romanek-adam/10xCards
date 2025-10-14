# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

10xCards is a Django-based educational flashcard application that uses AI to generate flashcards from student input text, combined with spaced repetition algorithms. Built with django-cookiecutter template.

**Tech Stack:**
- Backend: Django 5.2 with Python 3.13
- Frontend: HTMX + Bootstrap (minimal JavaScript)
- Database: PostgreSQL 17
- AI: OpenRouter API for LLM-powered flashcard generation
- Package Management: uv
- Containerization: Podman/Docker

## Development Commands

### Environment Setup
```bash
# Ensure DJANGO_READ_DOT_ENV_FILE=True is set (via .envrc or manually)
# The project uses direnv to auto-load .env file
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage html
uv run open htmlcov/index.html
```

### Type Checking
```bash
# Run mypy type checks on the flashcards app
uv run mypy flashcards
```

### Database Management
```bash
# Create superuser
uv run python manage.py createsuperuser

# Run migrations
uv run python manage.py migrate

# Create migrations
uv run python manage.py makemigrations
```

### Docker/Podman Development (using justfile)
```bash
# List available commands
just

# Build containers
just build

# Start containers
just up

# Stop containers
just down

# View logs
just logs

# Execute manage.py commands
just manage <command>

# Example: Create migrations
just manage makemigrations
```

### Code Quality
```bash
# Run ruff linter (configured in pyproject.toml)
uv run ruff check flashcards

# Run djLint for template linting
uv run djlint flashcards/templates
```

## Architecture

### Project Structure
- `flashcards/` - Main Django app directory
  - `users/` - Custom user app with django-allauth integration
  - `contrib/` - Contributed apps (e.g., custom sites migrations)
  - `static/` - Static files (CSS, JS)
  - `templates/` - Django templates
- `config/` - Django configuration
  - `settings/` - Split settings: base.py, local.py, test.py, production.py
  - `urls.py` - URL configuration
  - `wsgi.py` - WSGI configuration

### Settings Configuration
The project uses django-environ with split settings:
- `base.py` - Common settings for all environments
- `local.py` - Development settings
- `test.py` - Test settings (used by pytest via `--ds=config.settings.test`)
- `production.py` - Production settings

Environment variables are loaded from `.env` file when `DJANGO_READ_DOT_ENV_FILE=True`.

### Authentication
- Custom user model: `flashcards.users.User` (username-less, email-based)
- django-allauth configured with email-only login (no username field)
- Mandatory email verification (`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`)
- Custom adapters: `AccountAdapter` and `SocialAccountAdapter` in `flashcards.users.adapters`
- Custom forms: `UserSignupForm` in `flashcards.users.forms`
- Login redirect: `users:redirect` view
- Argon2 password hashing (primary hasher)

### Database
- PostgreSQL with psycopg3 driver
- Default database name: `flashcards`
- Database URL configured via `DATABASE_URL` environment variable
- Atomic requests enabled by default

### Key PRD Requirements
The MVP focuses on three core views:
1. **My Flashcards** - Flat list of user's flashcards with edit/delete
2. **Generate Flashcards** - AI-powered generation from text input (5-10 cards)
3. **Create Flashcard** - Manual flashcard creation

**Success Metrics:**
- 75% AI-generated flashcard acceptance rate
- 75% of total flashcards created via AI

**Out of Scope for MVP:**
- Folders, tags, categories
- Search/filter functionality
- Rich text or images in flashcards
- Mobile apps
- Content moderation
- Teacher/parent accounts
- Export functionality

### Testing Configuration
- pytest configured with `--ds=config.settings.test --reuse-db --import-mode=importlib`
- Coverage includes `flashcards/**`, excludes migrations and tests
- Django coverage plugin enabled
- Test files: `test_*.py` or `tests.py`

### Code Style
- Ruff linter with extensive rule set (see pyproject.toml)
- Force single-line imports (isort config)
- Migrations and staticfiles excluded from linting
- djLint for template formatting (Django profile, Bootstrap 5)
- mypy type checking with django-stubs plugin


## CODING_PRACTICES

### General

- When running in agent mode, execute up to 3 actions at a time and ask for approval or course correction afterwards.
- Write code with clear variable names and include explanatory comments for non-obvious logic. Avoid shorthand syntax and complex patterns.
- Provide full implementations rather than partial snippets. Include import statements, required dependencies, and initialization code.
- Add defensive coding patterns and clear error handling.
- Include validation for user inputs and explicit type checking.
- Suggest simpler solutions first, then offer more optimized versions with explanations of the trade-offs.
- Briefly explain why certain approaches are used and link to relevant documentation or learning resources.
- When suggesting fixes for errors, explain the root cause and how the solution addresses it to build understanding. Ask for confirmation before proceeding.
- Offer introducing basic test cases that demonstrate how the code works and common edge cases to consider.


### Documentation

- Update relevant documentation in /docs when modifying features
- Keep README.md in sync with new capabilities
- Maintain a log of what, why and how you did what you did in CHANGELOG.md


### Git

- Use conventional commits to create meaningful commit messages
- Use feature branches with descriptive names
- Write meaningful commit messages that primarily explain why changes were made, not just what
- Keep commits focused on single logical changes to facilitate code review and bisection

### Django

- Use class-based views instead of function-based views for more maintainable and reusable code components
- Leverage Django REST Framework for building APIs with serializers that enforce data validation
- Use Django ORM query expressions and annotations for complex database queries involving
- Leverage Django signals sparingly and document their usage to avoid hidden side effects in the application flow
- Implement custom model managers for encapsulating complex query logic rather than repeating queries across views
- Use Django forms or serializers for all user input to ensure proper validation and prevent security vulnerabilities

### Docker

- Use multi-stage builds to create smaller production images
- Implement layer caching strategies to speed up builds
- Use non-root users in containers for better security

## TESTING

### Guidelines for UNIT

#### PYTEST

- Use fixtures for test setup and dependency injection
- Implement parameterized tests for testing multiple inputs
- Use `pytest-mock`'s `mocker` fixture for mocking dependencies
- Use `pytest-responses` for mocking HTTP responses


### Guidelines for E2E

#### PLAYWRIGHT

- Initialize configuration only with Chromium/Desktop Chrome browser
- Use browser contexts for isolating test environments
- Implement the Page Object Model for maintainable tests
- Use locators for resilient element selection
- Leverage API testing for backend validation
- Implement visual comparison with expect(page).toHaveScreenshot()
- Use the codegen tool for test recording
- Leverage trace viewer for debugging test failures
- Implement test hooks for setup and teardown
- Use expect assertions with specific matchers
- Leverage parallel execution for faster test runs
