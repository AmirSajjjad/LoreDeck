---
name: api-creator
description: "Create or change FastAPI endpoints, schemas, dependencies, filters, pagination, sorting, use cases, repositories, and API tests in LoreDeck's Game backend. Do not use for pure model or Alembic changes, frontend work, Telegram handlers, AI integrations, or general documentation."
---

# Game API Creator

Work only under `apps/backend/src/loredeck/game` and directly affected tests or shared interfaces. Before editing:

1. Read the root and backend `AGENTS.md` files.
2. Inspect the closest Game API implementation and its tests; if the area is still empty, do not invent structure beyond the requested change.
3. Read [architecture.md](references/architecture.md) before adding or changing the router → use case → optional service → repository path.
4. Read [fastapi.md](references/fastapi.md) when the change affects HTTP contracts, dependencies, schemas, errors, or query behavior.
5. Trace the complete dependency path and define the method, path, router, auth rules, parameters/body, success schema/status, application errors, repository operations, transaction behavior, and tests.

Ask before implementation when a missing choice materially changes public API or business behavior and nearby code does not resolve it. Otherwise follow the closest established convention.

Implement the smallest complete change, preserve the existing public contract unless a breaking change is explicit, and add tests for observable API or use-case behavior. Run the narrowest relevant test first, then from `apps/backend` run:

```bash
uv run ruff check src/loredeck/game tests
uv run ruff format --check src/loredeck/game tests
uv run pyright
uv run pytest
```

Report changed files, API contract decisions, targeted and broader verification results, and unresolved decisions.
