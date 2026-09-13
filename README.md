# LoreDeck

LoreDeck is a monorepo for a Persian-first card-reading product. Its Game API and Vue frontend support authentication, profile management, guest or authenticated one-card and three-card readings, results, and authenticated reading history.

## Repository structure

- `apps/backend`: Python workspace for the Game API, Admin API, Telegram bot, AI integration, and shared infrastructure.
- `apps/frontend`: Vue 3, TypeScript, and Vite client managed with npm and Node.js 24.
- `apps/backend/src/loredeck/shared`: implemented database settings, async SQLAlchemy sessions, and shared models.
- `apps/backend/alembic`: the single migration environment and history for all backend services.
- `.agents/skills`: repository-specific Codex workflows.

`loredeck.game` exposes the public and authenticated contracts consumed by the frontend. The planned `loredeck.admin`, `loredeck.telegram_bot`, and `loredeck.ai` packages remain separate service boundaries. The frontend consumes HTTP contracts and remains independent from Python ORM models.

## Confirmed technologies

The backend uses Python 3.13, uv, FastAPI, Pydantic Settings, SQLAlchemy 2 with asyncpg, PostgreSQL, Alembic, Ruff, Pyright, Pytest, pytest-asyncio, pytest-cov, and pre-commit. The frontend uses Vue 3, TypeScript, Vite, npm, Pinia, Vue Router, Axios, Tailwind CSS, VeeValidate, Zod, Vitest, Vue Test Utils, and Playwright.

## Prerequisites

- Python 3.13
- Node.js `>=24.15.0 <25` and npm
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

Start the Game API from `apps/backend`:

```bash
uv run uvicorn loredeck.game.main:app --reload
```

The public `POST /readings` endpoint accepts a deck ID and either `one_card` or `three_card`. Authenticated readings are persisted by the backend; guest readings are not.

## Frontend development

Run frontend commands from `apps/frontend`:

```bash
cp .env.sample .env.local
npm ci
npm run dev
npm run check
npx playwright install chromium
npm run test:e2e
```

See `apps/frontend/README.md` for environment, architecture, authentication-session, testing, build, and preview details.

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

The hooks perform repository hygiene checks, backend Ruff lint and formatting checks, and frontend ESLint and Prettier checks without synchronizing dependencies.

## Important paths

- Backend configuration: `apps/backend/src/loredeck/shared/config.py`
- Database engine and sessions: `apps/backend/src/loredeck/shared/database.py`
- Shared models: `apps/backend/src/loredeck/shared/models/`
- Alembic configuration: `apps/backend/alembic.ini`
- Alembic revisions: `apps/backend/alembic/versions/`
- Backend tests: `apps/backend/tests/`
