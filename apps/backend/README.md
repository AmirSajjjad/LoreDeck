# LoreDeck backend

The backend workspace contains the player-facing FastAPI Game API, shared PostgreSQL models and
database infrastructure, the repository's single Alembic migration history, deterministic card
seed data, and backend tests. The `admin`, `ai`, and `telegram_bot` namespaces exist as service
boundaries but do not currently expose runnable applications.

## Architecture

Game features follow the existing request flow:

```text
FastAPI router -> use case -> optional service -> repository -> async SQLAlchemy session
```

- Routers own HTTP contracts, dependencies, status codes, and error mapping.
- Use cases coordinate application behavior and transaction boundaries.
- Repositories contain SQLAlchemy queries and do not commit independently.
- Password hashing and JWT handling live in user services.
- Shared settings, metadata, engine, sessions, and ORM models live under `loredeck.shared`.

## Layout

```text
alembic/                       Shared migration environment and revisions
data/seeds/                    Validated seed input
scripts/seed_major_arcana.py   Idempotent major-arcana seed runner
src/loredeck/game/decks/       Public deck API and persistence
src/loredeck/game/readings/    Reading creation and authenticated history
src/loredeck/game/user/        Authentication and profile management
src/loredeck/shared/           Settings, database infrastructure, and ORM models
static/                        Card artwork exposed at /static
tests/integration/             HTTP, repository, database, and migration-boundary tests
tests/unit/                    Isolated configuration and use-case tests
```

## Setup

Requirements are Python `>=3.13,<3.14`, uv, and PostgreSQL. Run backend commands from
`apps/backend`:

```bash
cp .env.sample .env
uv sync --dev
```

Edit `.env` for the local database and generate a non-placeholder JWT secret. The application reads:

- `LOREDECK_DATABASE_HOST`, `LOREDECK_DATABASE_PORT`, `LOREDECK_DATABASE_NAME`
- `LOREDECK_DATABASE_USER`, `LOREDECK_DATABASE_PASSWORD`
- `LOREDECK_DATABASE_DRIVER`, `LOREDECK_DATABASE_ECHO`
- `LOREDECK_DEBUG`
- `LOREDECK_CORS_ALLOWED_ORIGINS`, `LOREDECK_CORS_ALLOWED_METHODS`,
  `LOREDECK_CORS_ALLOWED_HEADERS`
- `LOREDECK_JWT_SECRET`, `LOREDECK_JWT_ALGORITHM`,
  `LOREDECK_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`

Comma-separate multiple CORS values. Do not use wildcard origins when credentials are enabled.
Redis is not configured or required by the current backend.

## Database and seed data

Apply the current migrations and load the major-arcana deck:

```bash
uv run alembic -c alembic.ini upgrade head
uv run python scripts/seed_major_arcana.py
```

The seed command is transactional and rerunnable. Useful Alembic inspection and rollback commands:

```bash
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini history
uv run alembic -c alembic.ini downgrade -1
```

Review migration downgrade behavior and data impact before running it. Deployment uses the same
Alembic history through the one-shot Compose `migrate` service; API replicas do not migrate on
startup.

## Run the Game API

Start the development server on port 8000:

```bash
uv run uvicorn loredeck.game.main:app --reload --host 127.0.0.1 --port 8000
```

Implemented route groups include:

- `GET /decks`
- `POST /readings`
- `GET /readings/history` and `GET /readings/history/{history_id}`
- `POST /users/signup` and `POST /users/signin`
- `GET /users/profile` and `PATCH /users/profile`
- `/static/*` for card artwork

Reading history and profile routes require a bearer token. Reading creation accepts guests and
persists history only for authenticated users.

## API documentation and health checks

Set `LOREDECK_DEBUG=true` to enable:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

These URLs intentionally return 404 when debug mode is disabled. There is no dedicated backend
`/health` route. The production image health check calls `GET http://127.0.0.1:8000/decks`, which
checks both the FastAPI process and database access. The container frontend exposes `/healthz`.

## Checks

Run the backend verification suite from `apps/backend`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Run one test file or node first while iterating, for example:

```bash
uv run pytest tests/integration/test_game_decks_api.py
```

Install or run repository hooks from the repository root:

```bash
uv run --project apps/backend pre-commit install
uv run --project apps/backend pre-commit run --all-files
```

## Container deployment

`Dockerfile` builds the backend independently and runs Uvicorn as a non-root user without reload
mode. The root Compose stack supplies PostgreSQL settings, gates startup on the one-shot migration,
and persists database data in a named volume. See the [deployment guide](../../deploy/README.md).
