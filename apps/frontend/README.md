# LoreDeck frontend

Minimal Vue 3 client for LoreDeck. Use Node.js 24 and npm.

## Setup

```bash
cp .env.sample .env.local
npm ci
```

Set `VITE_API_BASE_URL` in `.env.local` to the Game API origin. Do not commit populated environment files.

Shared environment validation and the Axios instance live in `src/api`. Feature API modules must
import `apiClient` from `@/api/client`; Vue components and views must call feature services instead
of Axios directly.

## Authentication

The Game API returns a bearer access token from `/users/signin` and `/users/signup`; it does not
provide refresh or logout endpoints. The frontend stores only that token in `sessionStorage`, so the
session survives reloads in the current browser tab and ends when the tab closes or the user logs
out. Session startup verifies the token through `/users/profile`. Do not move the token to
`localStorage`, log it, or infer authorization by decoding it on the client.

## Commands

```bash
npm run dev
npm run type-check
npm run lint
npm run format:check
npm run test
npm run test:e2e
npm run check
npm run build
npm run preview
```

`npm run format` writes Prettier changes. Run commands from `apps/frontend`.

## Tests

Unit and component tests live in `tests/unit`; browser journeys live in `tests/e2e`. Vitest uses a
shared jsdom setup and mocks the shared Axios boundary, so it cannot contact a live backend.
Playwright routes API calls to deterministic in-test fixtures and targets Chromium only.

Install the Chromium binary once after `npm ci`:

```bash
npx playwright install chromium
```

Use `npm run test` for a non-interactive unit run, `npm run test:watch` while developing, and
`npm run test:e2e` for browser journeys. Failure screenshots, video, and traces are written to
ignored test-artifact directories.
