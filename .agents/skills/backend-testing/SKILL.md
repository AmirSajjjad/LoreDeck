---
name: backend-testing
description: Add, update, or diagnose tests for LoreDeck Python services under apps/backend, from isolated unit tests through database and FastAPI integration tests.
---

# Backend Testing

Read the root and backend `AGENTS.md` files, the code under test, neighboring tests in `apps/backend/tests`, and their fixtures before changing tests or production code.

- Choose unit tests for isolated rules and service workflows; choose integration tests for SQLAlchemy repositories, migrations, session behavior, or FastAPI boundaries.
- Reuse established fixtures and database isolation. Keep state local to each test, clean up reliably, and do not depend on test order.
- Make time, randomness, environment, and external providers deterministic. Do not call live Telegram, AI, or other third-party services.
- Assert observable contracts and outcomes, not private call sequences or a line-for-line mirror of the implementation.
- When diagnosing a failure, reproduce it with the smallest relevant node or file before broadening scope.

From `apps/backend`, run the narrowest relevant `uv run pytest ...` selection first. After it passes, run the affected test group, then `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, and the broader `uv run pytest` suite when the current tree supports them. Separate failures caused by the change from pre-existing failures.
