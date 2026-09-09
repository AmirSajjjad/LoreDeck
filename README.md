# LoreDeck

LoreDeck is a monorepo for a card-reading product. The repository is currently establishing its shared backend foundation; the service and frontend packages exist, but application features are not yet implemented.

## Repository structure

- `apps/backend`: Python workspace for the Game API, Admin API, Telegram bot, AI integration, and shared infrastructure.
- `apps/frontend`: independent frontend placeholder; no framework or package manager has been selected.
- `apps/backend/src/loredeck/shared`: implemented database settings, async SQLAlchemy sessions, and shared models.
- `apps/backend/alembic`: the single migration environment and history for all backend services.
- `.agents/skills`: repository-specific Codex workflows.

The planned `loredeck.game` and `loredeck.admin` packages will host separate FastAPI applications. `loredeck.telegram_bot` and `loredeck.ai` are also placeholders pending implementation choices. The frontend will consume backend APIs and remains independent from Python ORM models.

## Confirmed technologies

The backend configuration currently uses Python 3.13, uv, FastAPI, Pydantic Settings, SQLAlchemy 2 with asyncpg, PostgreSQL, Alembic, Ruff, Pyright, Pytest, pytest-asyncio, pytest-cov, and pre-commit. No frontend toolchain is configured yet.

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL when running migrations or database-backed code
- Git for pre-commit hooks

## Environment setup

From the repository root, create a local backend environment file:

```bash
cp .env.sample apps/backend/.env
```

Edit the safe placeholder values for your local PostgreSQL instance. LoreDeck reads the `LOREDECK_DATABASE_HOST`, `LOREDECK_DATABASE_PORT`, `LOREDECK_DATABASE_NAME`, `LOREDECK_DATABASE_USER`, `LOREDECK_DATABASE_PASSWORD`, `LOREDECK_DATABASE_DRIVER`, and `LOREDECK_DATABASE_ECHO` variables. Never commit `apps/backend/.env`.

## Backend development

Run backend commands from `apps/backend`:

```bash
uv sync --dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Apply the shared migration history after configuring PostgreSQL:

```bash
uv run alembic -c alembic.ini upgrade head
```

Create a new revision after updating shared models and verifying the next sequential identifier:

```bash
uv run alembic -c alembic.ini revision --autogenerate --rev-id 002 -m "describe_change"
```

Alembic writes revisions as `{number}-{YYYYMMDD}-{lowercase_snake_case_description}.py`. Review every generated upgrade and downgrade before applying it.

## Repository hooks

After installing backend development dependencies, run from the repository root:

```bash
uv run --project apps/backend pre-commit install
uv run --project apps/backend pre-commit run --all-files
```

The hooks perform repository hygiene checks and run backend Ruff lint and format checks without synchronizing dependencies. Frontend-specific hooks will be added after `apps/frontend` has a committed package manifest, lockfile, and tool configuration.

## Important paths

- Backend configuration: `apps/backend/src/loredeck/shared/config.py`
- Database engine and sessions: `apps/backend/src/loredeck/shared/database.py`
- Shared models: `apps/backend/src/loredeck/shared/models/`
- Alembic configuration: `apps/backend/alembic.ini`
- Alembic revisions: `apps/backend/alembic/versions/`
- Backend tests: `apps/backend/tests/`
