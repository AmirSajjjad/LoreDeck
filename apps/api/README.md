# My handbook

LoreDeck database migrations.

Create a migration from the repository root:

    uv run --env-file .env --project apps/api \
      alembic -c apps/api/alembic.ini revision --autogenerate -m "message"

Apply migrations:

    uv run --env-file .env --project apps/api \
      alembic -c apps/api/alembic.ini upgrade head

Revert the latest migration:

    uv run --env-file .env --project apps/api \
      alembic -c apps/api/alembic.ini downgrade -1

uv run --env-file .env --project apps/api \
  alembic -c apps/api/alembic.ini current

uv run --env-file .env --project apps/api \
  uvicorn loredeck.main:app \
  --app-dir apps/api/src \
  --reload

---


# LoreDeck API

FastAPI backend for LoreDeck.

## Requirements

- Python 3.13
- uv

## Install

From the repository root:

```bash
uv sync --project apps/api
````

## Run

```bash
uv run --project apps/api uvicorn loredeck.main:app \
  --app-dir apps/api/src \
  --reload
```

The API will be available at:

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## Verify

```bash
uv run --project apps/api ruff check apps/api
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api pyright
uv run --project apps/api pytest apps/api/tests
```
