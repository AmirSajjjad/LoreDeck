---
name: database-change
description: Change LoreDeck shared SQLAlchemy models or PostgreSQL schema and create or review the corresponding revision in the single backend Alembic history.
---

# Database Change

Before editing, read the root and backend `AGENTS.md` files. Inspect affected models in `apps/backend/src/loredeck/shared/models`, metadata and sessions in `apps/backend/src/loredeck/shared/database.py`, model registration in `apps/backend/src/loredeck/shared/models/__init__.py`, `apps/backend/alembic/env.py`, current heads, and neighboring revisions in `apps/backend/alembic/versions`.

- Update the shared SQLAlchemy mapping first and ensure Alembic metadata imports every affected model.
- Create exactly one new revision in the shared `apps/backend/alembic/versions` history for one coherent schema change. Never create per-service Alembic trees.
- Use an explicit sequential three-digit `--rev-id`; `alembic.ini` formats the filename as `{revision}-{YYYYMMDD}-{lowercase_snake_case_slug}.py`.
- Do not edit, renumber, or reuse an already-applied revision unless the user explicitly requests it.
- Review generated operations manually: types, nullability, defaults, indexes, constraints, foreign-key actions, operation order, and data safety. Do not assume existing tables are empty.
- Make upgrade and downgrade safe and symmetric where feasible; document any intentional irreversible data operation.
- Update affected integration tests and `apps/backend/data/seeds` or `apps/backend/scripts` logic when the schema changes their behavior.

From `apps/backend`, run targeted model/integration tests and Ruff first. When database access is available, verify upgrade to head and downgrade/re-upgrade against a disposable database; then run Pyright and the broader relevant Pytest suite. Never target an unverified shared or production database.
