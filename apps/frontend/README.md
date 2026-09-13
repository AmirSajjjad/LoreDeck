# LoreDeck frontend

The frontend is a Persian-first, RTL Vue single-page application for the LoreDeck Game API. It
supports guest readings, account signup and sign-in, profile management, authenticated reading
history, and responsive loading, empty, success, and error states.

## Architecture

- `src/api`: validated environment access, shared Axios client, authentication hooks, and normalized
  API errors.
- `src/components`: reusable common and layout components.
- `src/composables`: shared stateful UI behavior, including FastAPI validation mapping.
- `src/features/auth`: authentication API, schemas, session token storage, views, and components.
- `src/features/profile`: profile API, schemas, views, and components.
- `src/features/readings`: deck, reading, result, and history APIs and UI.
- `src/router`: lazy routes and guest/authentication navigation policy.
- `src/stores`: cross-route Pinia state.
- `src/assets/styles`: global RTL styles and design tokens.
- `tests/unit`: Vitest and Vue Test Utils coverage.
- `tests/e2e`: Playwright browser journeys with deterministic API interception.

Views and components call feature services; feature services use the centralized Axios client.
Authentication stores the bearer token in `sessionStorage`. The API has no refresh-token or logout
endpoint.

## Setup

Use Node.js `>=24.15.0 <25`, npm, and the committed `package-lock.json`. Run frontend commands from
`apps/frontend`:

```bash
cp .env.sample .env.local
npm ci
npm run dev
```

Vite serves the application at `http://localhost:5173` by default.

## Backend API URL

`VITE_API_BASE_URL` is required and read once by the centralized API configuration. It accepts an
absolute HTTP(S) URL or a safe root-relative path, without credentials, a query, or a fragment.
The development sample uses:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

The production container builds with `/api`; Nginx proxies that path to its environment-backed
`BACKEND_UPSTREAM`. Never put secrets in Vite variables because they are public browser assets.

## Development and verification

Available npm scripts:

```bash
npm run dev           # Vite development server
npm run build         # Type-check and create dist/
npm run preview       # Preview dist/ on port 4173 by default
npm run type-check    # vue-tsc
npm run lint          # ESLint
npm run format        # Write Prettier formatting
npm run format:check  # Check Prettier formatting
npm run test          # Vitest unit/component suite
npm run test:watch    # Interactive Vitest watch mode
npm run test:e2e      # Playwright browser suite
npm run check         # Format, lint, type-check, unit tests, and build
```

Install the Playwright Chromium binary once after `npm ci`:

```bash
npx playwright install chromium
npm run test:e2e
```

Playwright starts its isolated Vite server at `http://127.0.0.1:4173` and intercepts Game API
requests; it does not require a live backend. Test screenshots, videos, traces, and HTML reports are
written to ignored artifact directories.

## Production deployment

`Dockerfile` performs the Node.js build in one stage and copies only `dist/` into unprivileged Nginx.
The Nginx configuration provides SPA history fallback, `GET /healthz`, and the `/api` reverse proxy.
The container listens on port 8080 and requires `BACKEND_UPSTREAM` when the backend is not reachable
at the Compose default `http://backend:8000`.

Build the frontend image independently from this directory:

```bash
docker build -t loredeck-frontend .
```

For the complete PostgreSQL, migration, Game API, CORS, and frontend topology, follow the
[deployment guide](../../deploy/README.md).
