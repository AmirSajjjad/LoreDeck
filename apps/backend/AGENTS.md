# LoreDeck Backend Instructions

These instructions apply under `apps/backend` in addition to the repository-level `AGENTS.md`.

## Layout and ownership

- Python sources use the `src` layout and the `loredeck` namespace. Use absolute imports such as `from loredeck.shared.db...`; do not import through `src.loredeck`.
- `loredeck.game` owns the player-facing FastAPI service; `loredeck.admin` owns the administrative FastAPI service; `loredeck.telegram_bot` owns Telegram integration; `loredeck.ai` owns the eventual AI integration; `loredeck.shared` contains only cross-service infrastructure and data definitions.
- Shared SQLAlchemy models live in `src/loredeck/shared/db/models`; shared metadata, engine, session factory, and session dependencies live in `src/loredeck/shared/db`.
- All services use the single Alembic environment in `alembic` with configuration in `alembic.ini`. Never create a service-specific migration history.

## Backend conventions

- Follow the existing SQLAlchemy 2 typed mappings and async engine/session patterns. Await database work, keep transaction ownership at the request or workflow boundary, and do not commit inside repositories.
- For FastAPI code, keep request/response/status handling in routes and schemas, persistence queries in repositories, and multi-step business workflows in services. Add only the boundaries needed by current code; do not impose unused layers.
- Reuse shared models, sessions, and metadata, but keep service-specific business rules out of `shared`.
- Read configuration through the established settings boundary. Use `LOREDECK_` environment variables, keep environment-specific values in local environment files, and never embed secrets or real credentials in code, tests, examples, or migrations.
- Keep maintained static assets under `static`; reference them by repository-relative or configured paths rather than machine-specific absolute paths.
- Keep seed inputs under `data/seeds` and seed runners under `scripts`. Seed operations should validate input, be deterministic and rerunnable, and participate in an explicit transaction.

## Tests and verification

- Put tests under `tests`; use unit tests for isolated rules and integration tests for database, migration, or HTTP boundaries. Follow nearby fixtures and database isolation, avoid order dependence and live third-party calls, and test observable behavior rather than implementation details.
- Run the narrowest relevant Pytest selection first, then broader checks when the code is runnable: `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, and `uv run pytest`.

## Migrations

- Inspect model registration, current heads, and neighboring revisions before changing schema. Update the shared model, generate exactly one revision in `alembic/versions`, and manually review upgrade and downgrade operations, constraint names, defaults, and existing-data safety.
- Do not modify an already-applied revision unless explicitly requested. Update affected integration tests and seed logic with schema changes.
