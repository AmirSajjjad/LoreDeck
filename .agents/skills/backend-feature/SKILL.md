---
name: backend-feature
description: Implement or modify a LoreDeck FastAPI backend feature, including its API, application behavior, domain rules, persistence, and tests. Use for backend feature requests under apps/api; do not use for frontend-only work or standalone database migrations.
---

# Backend Feature

Implement the smallest complete vertical slice that satisfies the requested
backend behavior.

## Inspect

Before editing:

1. Read the root `AGENTS.md`.
2. Read the nearest applicable `AGENTS.md`.
3. Inspect the target module and neighboring implementations.
4. Identify the current domain rule, application boundary, API contract, and
   persistence impact.
5. Reuse established patterns when they fit the requested behavior.

Do not invent fields, endpoints, relationships, states, or provider behavior
that cannot be derived from the request or existing repository.

## Implement

Change only the layers required by the feature:

- domain for business concepts and invariant rules
- application for use cases and ports
- infrastructure for persistence or provider implementations
- presentation for HTTP schemas, routes, and error mapping

Keep route handlers thin and keep framework dependencies out of the domain.

When the feature changes the database schema:

1. update the SQLAlchemy mappings
2. create an Alembic migration
3. inspect upgrade and downgrade operations
4. test the resulting schema behavior

Do not commit inside repositories. Let the application or request boundary own
the transaction.

## Test

Add tests at the lowest useful level:

- domain tests for invariant rules
- application tests for use-case behavior
- integration tests for persistence
- API tests for HTTP contracts

Do not call live AI services or third-party APIs in tests. Use deterministic
fakes.

## Verify

Run the checks relevant to the changed files:

```bash
uv run --project apps/api ruff check apps/api
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api pyright
uv run --project apps/api pytest apps/api/tests
````

Fix failures caused by the change. Do not modify unrelated code only to silence
an unrelated failure.

## Report

Summarize:

* implemented behavior
* important design decisions
* migrations created
* verification commands and results
* remaining limitations
