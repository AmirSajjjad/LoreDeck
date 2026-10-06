# Container deployment

[Project overview](../README.md) · [Backend](../apps/backend/README.md) ·
[Frontend](../apps/frontend/README.md)

## Topology and prerequisites

Install Docker Engine and its Compose plugin, or Docker Desktop (which includes Compose), following
[official installation instructions](https://docs.docker.com/compose/install/). Verify with
`docker compose version`. Git is needed to obtain the checkout. Image builds need network access;
AI readings need an API key, model access, and connectivity to the configured OpenAI endpoint.
Host Python and Node.js are not needed for this container workflow.

All commands below run from the repository root. The checked-in file is
[../docker-compose.yml](../docker-compose.yml); it defines no profiles:

- `postgres`: PostgreSQL 17 with a persistent `postgres_data` volume and readiness check.
- `migrate`: one-shot Alembic upgrade, gated on healthy PostgreSQL.
- `backend`: Game API, gated on successful migrations; image health check requests `/decks`.
- `frontend`: unprivileged Nginx serving the Vue build, gated on a healthy backend.

Redis, Admin, and Telegram services are not included. Images run as non-root users.
API startup does not migrate or seed the database independently.

## Prepare environment files

For a fresh checkout only; retain existing local files:

```bash
cp .env.sample .env
cp apps/backend/.env.sample apps/backend/.env
```

In root `.env`, replace `POSTGRES_PASSWORD` and `JWT_SECRET` with strong private values.
Set `FRONTEND_ORIGIN` to the browser-visible scheme, host, and port. Defaults use
`http://localhost:8080`. Root settings also control project/image names, host binds and ports,
CORS methods/headers, and `BACKEND_UPSTREAM` (default `http://backend:8000`).

In `apps/backend/.env`, set `LOREDECK_AI_PROVIDER=openai` and provide actual values for
`LOREDECK_OPENAI_API_KEY` and `LOREDECK_OPENAI_MODEL`. The sample also documents optional base URL,
timeout, retries, and response-length limits. No model or credentials are bundled.

**Current gap:** Compose does not forward any AI settings or load the backend environment file.
Settings validation requires a provider and, for OpenAI, a nonblank key and model. Consequently,
the unmodified stack fails during migration settings loading. Adding AI variables only to root
`.env` does not inject them into containers. The backend image also excludes seed scripts/data.

For a local run without editing checked-in configuration, create this temporary override:

```bash
cat > /tmp/loredeck-compose.local.yml <<YAML
services:
  migrate:
    env_file:
      - ./apps/backend/.env
  backend:
    env_file:
      - ./apps/backend/.env
    volumes:
      - ./apps/backend/scripts:/app/scripts:ro
      - ./apps/backend/data:/app/data:ro
YAML
```

Compose resolves relative paths against the first Compose file, at the repository root.
Its explicit `environment` entries override `env_file`, so the root database/JWT values still
control both containers and the database host remains `postgres`. The override supplies AI settings
and read-only seed inputs; it is a local workaround, not a checked-in deployment configuration.
For hosted deployments, equivalent secret injection and an explicit seed job remain prerequisites.

## Build, migrate, and seed

Validate configuration without printing interpolated secrets, then start:

```bash
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml config --quiet
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml up -d --build
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml ps --all
```

Compose runs `alembic -c /app/alembic.ini upgrade head` through `migrate` before backend startup.
Run one deployment operation per database at a time. Migrations create schema, not the card catalog.
After the backend is running, load the bundled deck explicitly:

```bash
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml exec backend /app/.venv/bin/python /app/scripts/seed_major_arcana.py
```

The seed runner validates `data/seeds/major_arcana.json` and transactionally upserts decks by title
and cards by deck/number. It can be rerun but updates matching records to the bundled seed values.
Without seeds, `/decks` may return an empty catalog even while health checks pass.

To run migrations separately and inspect the revision:

```bash
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml up -d --wait postgres
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml run --rm migrate
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml run --rm migrate /app/.venv/bin/alembic -c /app/alembic.ini current
```

## Services and URLs

These are defaults; adjust URLs when changing root ports/origin:

| Service | Address or behavior |
| --- | --- |
| Frontend | `http://localhost:8080` |
| Nginx health | `http://localhost:8080/healthz` |
| Proxied deck API | `http://localhost:8080/api/decks` |
| Direct Game API | `http://localhost:8000/decks`, bound to host loopback |
| PostgreSQL | Private Compose network, `postgres:5432`; no published host port |
| Migrations | One-shot process; no HTTP service |

Nginx strips `/api/` before proxying to the backend, and provides SPA history fallback.
The frontend build uses `/api`; `BACKEND_UPSTREAM` is a runtime Nginx setting.
Compose forces `LOREDECK_DEBUG=false`, disabling `/docs`, `/redoc`, and `/openapi.json`.
There is no backend `/health` endpoint. Verify with:

```bash
curl --fail http://localhost:8080/healthz
curl --fail http://localhost:8080/api/decks
curl --fail http://localhost:8000/decks
```

Frontend and backend must become healthy; `migrate` should exit with status 0. A successful seed
and configured AI account are required to exercise readings. TLS, public domains, backups, registry
publishing, and cross-host rollout coordination are not configured by this repository.

## Operations

Use the same files and environment for every operation:

```bash
# Follow logs; stop following with Ctrl+C.
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml logs --follow backend frontend postgres migrate
# Rebuild and recreate after changes.
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml up -d --build
# Restart existing application containers.
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml restart backend frontend
# Stop/remove containers and network, retaining the database volume.
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml down
```

Changing PostgreSQL credentials in `.env` does not update an already initialized database volume.
Plan database credential changes separately. Do not remove the volume to fix configuration unless
its data is intentionally disposable.
