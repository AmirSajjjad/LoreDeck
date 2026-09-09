# LoreDeck Repository Instructions

LoreDeck is a monorepo for a card-reading product. `apps/backend` is the Python workspace for the Game API, Admin API, Telegram bot, AI integration, and shared infrastructure; `apps/frontend` is the independent client application.

## Scope and boundaries

- This file applies repository-wide. A nested `AGENTS.md` adds or overrides instructions for its subtree; follow the nearest applicable file.
- Backend services share SQLAlchemy models in `apps/backend/src/loredeck/shared/models`, database infrastructure in `apps/backend/src/loredeck/shared/database.py`, and one Alembic history in `apps/backend/alembic`.
- Keep Game, Admin, Telegram bot, and AI behavior within their respective service namespaces. Put only genuinely cross-service infrastructure and data definitions in `loredeck.shared`.
- The frontend consumes backend API contracts and does not import or mirror Python ORM models.

## Workflow

- Inspect neighboring code, tests, configuration, and the applicable instructions before editing. Preserve existing conventions and unrelated user changes.
- Keep changes within the requested scope. When behavior changes, update its tests and relevant documentation.
- Do not edit generated artifacts or existing migration history without a specific reason.
- Run commands from `apps/backend` unless a command explicitly uses repository-root paths. Confirmed backend checks are `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, and `uv run pytest`.
- Report changed files, verification performed, and any pre-existing or remaining blockers.
