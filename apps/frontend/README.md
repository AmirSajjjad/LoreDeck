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
npm run build
npm run preview
```

`npm run format` writes Prettier changes. Run commands from `apps/frontend`.
