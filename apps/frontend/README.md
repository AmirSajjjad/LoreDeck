# LoreDeck frontend

Vue 3 client for the LoreDeck Game API. Use Node.js `>=24.15.0 <25` and npm;
`package-lock.json` is the only supported lockfile.

## Setup and environment

```bash
cp .env.sample .env.local
npm ci
npm run dev
```

`VITE_API_BASE_URL` is the required, public Game API origin. The sample value expects the backend
at `http://localhost:8000`; the API has no global `/api` prefix. Never commit `.env.local` or other
populated environment files.

Shared environment validation and the Axios instance live in `src/api`. Feature API modules import
`apiClient` from `@/api/client`; Vue components and views call feature services instead of Axios.

## Authentication

The Game API returns a bearer access token from `/users/signin` and `/users/signup`; it has no
refresh or logout endpoint. The frontend stores only that token in `sessionStorage`, so the session
survives reloads in the current tab and ends when the tab closes or the user logs out. Startup
verifies a stored token through `/users/profile`.

Do not move tokens to `localStorage`, log them, or infer authorization by decoding them. Route
guards improve navigation but are not an authorization boundary; the backend protects user data.

## Structure

- `src/api`: environment, shared HTTP client, authentication hooks, and normalized errors.
- `src/components`: reusable visual, form, state, and layout components.
- `src/features`: feature-owned auth, profile, and reading APIs, schemas, types, and UI.
- `src/router`: named routes, lazy page loading, and navigation policy.
- `src/stores`: cross-route Pinia state; currently the authenticated session.
- `src/assets/styles`: global RTL styles and design tokens.
- `tests/unit`: Vitest unit, component, and integration tests.
- `tests/e2e`: isolated Playwright journeys with deterministic mocked API responses.

## Verification and builds

```bash
npm run type-check
npm run lint
npm run format:check
npm run test
npm run test:e2e
npm run check
npm run build
npm run preview
```

`npm run check` runs formatting, linting, type-checking, unit tests, and the production build.
`npm run format` writes Prettier changes. Run all commands from `apps/frontend`.

Install the Chromium binary once after `npm ci`:

```bash
npx playwright install chromium
```

Use `npm run test:watch` only during development. Unit tests block unexpected live HTTP traffic;
Playwright intercepts API calls with deterministic fixtures. Failure screenshots, videos, and
traces are written to ignored artifact directories. Build with `npm run build`, then inspect the
output locally with `npm run preview`.
