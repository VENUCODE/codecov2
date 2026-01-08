# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI Math Operations API - A REST API providing basic and advanced mathematical operations with comprehensive test coverage and CI/CD integration.

## Development Commands

### Running the API
```bash
uvicorn app.main:app --reload
```
Access interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=app
```

**Run with coverage report and minimum threshold:**
```bash
pytest --cov=app --cov-report=term --cov-fail-under=75
```

**Run tests excluding integration/slow tests (matches CI):**
```bash
pytest --cov=app --cov-report=xml --cov-report=term --cov-fail-under=75 --junitxml=junit.xml -m "not integration and not e2e and not slow"
```

**Run single test:**
```bash
pytest tests/test_main.py::TestAddEndpoint::test_add_positive_numbers -v
```

## Architecture

### Application Structure

The codebase follows a simple layered architecture:

- **app/main.py**: FastAPI application entry point with endpoint definitions. All API routes are defined here with centralized error handlers.
- **app/models.py**: Pydantic models for request/response validation (MathRequest, SingleNumberRequest, MathResponse, HealthResponse).
- **app/utils.py**: Pure utility functions for mathematical operations and validation. These are standalone functions without side effects.
- **app/errors.py**: Custom error handlers and exceptions. Includes centralized handlers for validation errors and division by zero.
- **tests/**: Test files organized by module (test_main.py, test_utils.py, test_errors.py).

### Error Handling Pattern

The app uses a layered error handling approach:
1. Pydantic validation for request models (422 errors)
2. Custom exception handlers registered in main.py via `app.add_exception_handler()`
3. HTTPException for business logic errors (400 errors)
4. Utility functions raise ValueError which are caught and converted to HTTPException

### Code Coverage Requirements

**CRITICAL**: This project enforces a **75% minimum code coverage threshold**. This is enforced at three levels:

1. **Pre-push Git hook** (`.githooks/pre-push`): Runs locally before push, blocks if coverage < 75%
2. **Test-reporting.yml workflow**: Runs on PRs with `--cov-fail-under=75`, blocks PR merge if coverage insufficient
3. **CI workflow**: Checks coverage threshold and displays results in PR comments

When adding new code or endpoints:
- Always add corresponding tests to maintain 75% coverage
- The pre-push hook will prevent pushing code that fails tests or drops coverage below 75%
- CI/CD workflows will block PR merges if coverage requirements aren't met

### CI/CD Workflows

Two GitHub Actions workflows run on PRs:

1. **ci.yml** (Codecov Coverage Workflow):
   - Uploads coverage to Codecov
   - Uploads test results to Codecov
   - Checks 75% coverage threshold
   - Displays coverage summary in PR comments

2. **test-reporting.yml** (Test quality and coverage):
   - Runs with `--cov-fail-under=75` to enforce threshold
   - Publishes test results with EnricoMi/publish-unit-test-result-action
   - Generates CTRF JSON reports for GitHub Test Reporter
   - Excludes integration/e2e/slow tests

### Git Hooks

The `.githooks/pre-push` hook:
- Automatically runs pytest with coverage check before allowing push
- Requires 75% minimum coverage
- Can be bypassed with `--no-verify` (not recommended - CI will still block merge)
- Provides colored output for test results

### Branch Protection

Per the README, branch ruleset should be configured to require:
- Passing CI checks (both workflows)
- 75% minimum code coverage
- All tests passing

This prevents merging PRs that fail tests or have insufficient coverage.
