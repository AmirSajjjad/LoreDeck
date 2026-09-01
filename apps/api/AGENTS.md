# LoreDeck API Instructions

These instructions apply to files under `apps/api`.

Also follow the repository-level `AGENTS.md`.

## Stack

- Python 3.13
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- PostgreSQL
- Alembic
- uv
- Ruff
- Pyright
- Pytest

## Package Layout

Application code belongs under:

```text
apps/api/src/loredeck
````

Tests belong under:

```text
apps/api/tests
```

Use absolute imports from `loredeck`.

## API Conventions

* Place shared API routing in `loredeck/api`.
* Place module-specific routes in the module's `presentation` package.
* Prefix public API routes with `/api/v1`.
* Use Pydantic models for request and response bodies.
* Declare explicit HTTP status codes.
* Do not expose SQLAlchemy models from API responses.
* Translate domain and application errors at the presentation boundary.
* Keep route handlers thin; business behavior belongs in application use cases.

## Domain Conventions

* Keep the domain independent from FastAPI, SQLAlchemy, and provider SDKs.
* Represent business concepts explicitly when they contain behavior or
  validation.
* Do not add an abstraction unless at least one current use case requires it.
* Keep framework-specific code at the boundaries.

## Database Conventions

* Use SQLAlchemy 2 typed declarative mappings.
* Use asynchronous database sessions.
* Keep transactions at the application or request boundary.
* Do not commit inside repositories.
* Avoid lazy loading across application boundaries.
* Every schema change requires an Alembic migration.
* Review generated migrations before accepting them.
* Migrations must support upgrade and downgrade unless documented otherwise.

## Configuration

* Read configuration through Pydantic Settings.
* Environment variable names use the `LOREDECK_` prefix.
* Do not read environment variables directly inside domain or application code.
* Never hard-code secrets or environment-specific URLs.

## Testing

* Prefer unit tests for domain rules and application use cases.
* Use integration tests for database repositories and migrations.
* Use API tests for routing, validation, status codes, and error translation.
* Tests must not depend on execution order.
* Tests must not call live AI or third-party services.
* Replace external providers with deterministic fakes in tests.

## Quality

Before completing a backend change, run:

```bash
uv run --project apps/api ruff check apps/api
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api pyright
uv run --project apps/api pytest apps/api/tests
```
