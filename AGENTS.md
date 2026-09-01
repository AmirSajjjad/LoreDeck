# LoreDeck Repository Instructions

## Project

LoreDeck is a browser-based card reading platform.

The repository is a monorepo containing:

- `apps/api`: FastAPI backend
- `apps/web`: Vue frontend, planned for a later phase
- `docs`: architecture and product documentation
- `.agents/skills`: repository-specific Codex skills

The current development focus is the backend MVP.

## Architecture

The backend is a modular monolith with clean boundaries.

Each business module may contain:

- `domain`: business entities, value objects, rules, and errors
- `application`: use cases and ports
- `infrastructure`: database and external-provider implementations
- `presentation`: HTTP routes and schemas

Dependencies must point inward:

- presentation depends on application
- infrastructure implements application ports
- application depends on domain
- domain must not depend on FastAPI, SQLAlchemy, or external services

Do not create layers, abstractions, repositories, or interfaces without a
concrete use case.

## Repository Rules

- Keep backend code under `apps/api`.
- Keep frontend code under `apps/web`.
- Do not commit secrets or `.env`.
- Commit `uv.lock`.
- Do not commit virtual environments, caches, coverage output, or generated
  build artifacts.
- Preserve existing user changes.
- Keep changes scoped to the requested task.
- Do not add speculative functionality.
- Update documentation when an architectural or operational decision changes.

## Backend Commands

Run backend commands from the repository root:

```bash
uv sync --project apps/api
uv run --project apps/api ruff check apps/api
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api pyright
uv run --project apps/api pytest apps/api/tests
````

Run the API locally:

```bash
uv run --project apps/api uvicorn loredeck.main:app \
  --app-dir apps/api/src \
  --reload
```

## Verification

A backend change is complete when all relevant checks pass:

```bash
uv run --project apps/api ruff check apps/api
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api pyright
uv run --project apps/api pytest apps/api/tests
```

Report:

* files changed
* behavior implemented
* commands executed
* test results
* any remaining limitation or follow-up

## Skills

Use repository skills when their descriptions match the task.

Skills provide task workflows. This file remains the source of repository-wide
rules.
