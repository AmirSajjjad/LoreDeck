# LoreDeck

LoreDeck is a Persian-first card-reading application. The repository contains the FastAPI Game API,
the Vue single-page application, shared database models and migrations, card seed data, automated
tests, and a provider-neutral container deployment.

## Features

- Public deck discovery and one-card or three-card readings.
- Optional questions and guest reading flows.
- Account signup and sign-in with bearer-token authentication.
- Authenticated profile management and persisted reading history.
- Persian, RTL, responsive frontend with explicit loading, empty, and error states.
- Static card artwork served by the Game API.

## Technology

- Backend: Python 3.13, FastAPI, Pydantic Settings, SQLAlchemy 2, asyncpg, PostgreSQL,
  Alembic, uv, Ruff, Pyright, and Pytest.
- Frontend: Node.js 24, Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios, Tailwind CSS,
  VeeValidate, Zod, Vitest, Vue Test Utils, and Playwright.
- Deployment: multi-stage Docker images, unprivileged Nginx, Docker Compose, and PostgreSQL 17.

Redis is not a current application dependency.

## Repository layout

```text
apps/backend/      Game API, shared persistence, migrations, seed data, and backend tests
apps/frontend/     Vue application, unit tests, browser tests, and Nginx configuration
deploy/            Container deployment guide
docker-compose.yml Production-oriented local/container stack
.agents/skills/    Repository-specific development workflows
```

See the [backend guide](apps/backend/README.md), [frontend guide](apps/frontend/README.md), and
[deployment guide](deploy/README.md) for detailed commands and configuration.

## Prerequisites

For local development:

- Python `>=3.13,<3.14`
- [uv](https://docs.astral.sh/uv/)
- Node.js `>=24.15.0 <25` and npm
- PostgreSQL
- Git

Docker Engine with Docker Compose is sufficient for the container workflow.

## Quick start with Docker

From the repository root:

```bash
cp .env.sample .env
```

Replace the placeholder `POSTGRES_PASSWORD` and `JWT_SECRET`, then start the stack:

```bash
docker compose up -d --build
docker compose ps
```

Compose starts PostgreSQL, applies Alembic migrations once, starts the Game API, and serves the
frontend through Nginx. Open `http://localhost:8080`. The API is also published locally at
`http://localhost:8000`; `http://localhost:8080/healthz` is the frontend health endpoint.

Stop the stack without deleting PostgreSQL data:

```bash
docker compose down
```

## Local development

Run the backend and frontend in separate terminals. First provision PostgreSQL, then follow the
[backend setup](apps/backend/README.md#setup) to install dependencies, migrate and seed the database,
and start FastAPI on `http://localhost:8000`.

Follow the [frontend setup](apps/frontend/README.md#setup) to start Vite on
`http://localhost:5173`. The frontend sample environment already points to the local Game API.

## Repository checks

After installing both applications, run all configured pre-commit hooks from the repository root:

```bash
uv run --project apps/backend pre-commit install
uv run --project apps/backend pre-commit run --all-files
```

Application-specific test, lint, type-check, build, and browser-test commands are documented in the
backend and frontend guides.
