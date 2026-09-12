# LoreDeck frontend

Minimal Vue 3 client for LoreDeck. Use Node.js 24 and npm.

## Setup

```bash
cp .env.sample .env.local
npm ci
```

Set `VITE_API_BASE_URL` in `.env.local` to the Game API origin. Do not commit populated environment files.

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
