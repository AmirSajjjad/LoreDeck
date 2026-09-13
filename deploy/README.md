# Container deployment

The root `docker-compose.yml` provides a provider-neutral production deployment for the Game API,
Vue frontend, and PostgreSQL. Redis is not included because no current LoreDeck service uses it.

## Configure

From a clean checkout, create the Compose environment file:

```bash
cp .env.sample .env
```

Replace `POSTGRES_PASSWORD` and `JWT_SECRET`. Set `FRONTEND_ORIGIN` to the exact browser-visible
frontend origin, including its scheme and non-default port. The default is
`http://localhost:8080`. Set the bind addresses and ports for the host or reverse proxy without
putting provider-specific domains or secrets in either image.

The frontend image builds with the environment-neutral `/api` base path. Its Nginx server proxies
that path to `BACKEND_UPSTREAM`, which Compose sets to the private `backend:8000` service. The
backend independently receives `FRONTEND_ORIGIN` through `LOREDECK_CORS_ALLOWED_ORIGINS`.

## Build

Build both independently deployable images:

```bash
docker compose build backend frontend
```

The backend image runs FastAPI with Uvicorn as a non-root user. The frontend image builds Vue with
Node.js, then serves the static output with unprivileged Nginx; it does not contain the Node.js
build toolchain.

## Migrate

Compose applies migrations once through the `migrate` service before starting any API replicas:

```bash
docker compose up -d --build
```

The backend image never runs migrations during application startup. Compose also models migration
as a one-shot service and starts backend replicas only after it exits successfully, preventing
every replica from attempting the same migration. Run only one deployment operation against a
given database at a time; coordination between separate hosts belongs to the deployment platform.

To apply migrations without starting the application services, start PostgreSQL and run the same
one-shot migration command directly:

```bash
docker compose up -d --wait postgres
docker compose run --rm migrate
```

Inspect the migration state when needed:

```bash
docker compose run --rm migrate /app/.venv/bin/alembic -c /app/alembic.ini current
```

## Start and verify

Start the complete stack after configuration. This also runs the gated migration described above:

```bash
docker compose up -d --build
docker compose ps
```

Verify the frontend, its API proxy, and the directly published backend:

```bash
curl --fail http://localhost:8080/healthz
curl --fail http://localhost:8080/api/decks
curl --fail http://localhost:8000/decks
```

Container health checks validate PostgreSQL readiness, a database-backed Game API request, and the
Nginx frontend. `docker compose ps` should report `postgres`, `backend`, and `frontend` as healthy;
the `migrate` service should show a successful exit.

## Operate

Follow service logs:

```bash
docker compose logs --follow backend frontend postgres migrate
```

Restart application services without removing PostgreSQL data:

```bash
docker compose restart backend frontend
```

Stop containers while retaining the named PostgreSQL volume:

```bash
docker compose down
```

Remove the persistent database only when data loss is intentional:

```bash
docker compose down --volumes
```

For multiple backend replicas, leave migrations as the single deployment step and scale only the
backend service. Provider-specific TLS termination, domains, registry names, rollout locks, and
secret injection remain inputs for the selected hosting platform.
