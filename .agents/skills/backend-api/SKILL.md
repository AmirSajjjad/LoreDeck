---
name: backend-api
description: Create or change LoreDeck Game API or Admin API endpoints under apps/backend, including their HTTP contracts, workflows, persistence, and API tests.
---

# Backend API

Before editing, read the root and backend `AGENTS.md` files, then inspect the target service under `apps/backend/src/loredeck/game` or `apps/backend/src/loredeck/admin` and its nearby routes, schemas, repositories, services, and tests under `apps/backend/tests`. Follow established local structure; add only boundaries the endpoint needs.

- Keep FastAPI request parsing, response schemas, status codes, dependencies, and error translation in API modules.
- Keep SQLAlchemy queries and persistence details in repositories. Do not commit there; the request or service workflow owns the transaction.
- Keep business decisions and multi-step workflows in services.
- Reuse models and sessions from `loredeck.shared.db`; do not move Game- or Admin-specific rules into `loredeck.shared`.
- Update API tests for success, validation, authorization when relevant, and expected error responses. Add repository or service tests only where they verify separate behavior.

From `apps/backend`, run the narrowest affected Pytest test first. Then run Ruff on changed paths and, when the current tree is ready, `uv run pyright` and the broader `uv run pytest` suite. Report pre-existing failures separately.
