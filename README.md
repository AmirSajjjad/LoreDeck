# LoreDeck

LoreDeck is an open-source learning project for card-based fortune-telling and storytelling.
It models decks and cards with their own attributes, then uses an LLM to interpret drawn cards
and an optional question into a personalized story. It is an entertainment and software-learning
project; readings are imaginative interpretations, not reliable predictions or professional advice.

## Current capabilities

- Discover active decks and draw one-card or three-card spreads using secure random selection.
- Generate per-card stories and a combined summary through the implemented OpenAI provider.
- Read as a guest, or create an account and sign in with JWT bearer authentication.
- Manage a profile and retrieve saved readings for authenticated users.
- Use a Persian-first, responsive RTL web interface with card artwork and explicit UI states.

The data model supports different decks; the bundled seed supplies Major Arcana cards.
Admin and Telegram namespaces are placeholders, not runnable services. Additional AI providers
are not implemented.

## Repository structure

```text
.agents/
deploy/
apps/
  backend/
  frontend/
```

- [.agents](.agents/README.md): agent workflows, skills, prompt examples, and developer tools.
- [deploy](deploy/README.md): Compose setup, initialization, URLs, and operations.
- [apps/backend](apps/backend/README.md): Game API, AI integration, persistence, migrations, and tests.
- [apps/frontend](apps/frontend/README.md): Vue client, browser integration, and frontend checks.

## Technology stack

- Backend: Python 3.13, FastAPI, Pydantic Settings, SQLAlchemy 2 with asyncpg, PostgreSQL,
  Alembic, OpenAI SDK, Argon2 through pwdlib, and PyJWT. Development uses uv, Ruff, Pyright,
  and Pytest.
- Frontend: Node.js `>=24.15.0 <25`, npm, Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios,
  Tailwind CSS, VeeValidate, and Zod; tests use Vitest, Vue Test Utils, and Playwright.
- Containers: Docker Compose, PostgreSQL 17, multi-stage Python/Node builds, and unprivileged Nginx.

## Running with Docker Compose

Install Docker Engine with the Compose plugin, or Docker Desktop, and Git.
Run from the repository root; the only checked-in Compose file is `docker-compose.yml`,
with no profiles. Prepare the environment files without overwriting existing local settings:

```bash
cp .env.sample .env
cp apps/backend/.env.sample apps/backend/.env
```

Replace the root PostgreSQL password and JWT secret, and supply the backend AI provider,
API key, and model. **The checked-in Compose setup is incomplete:** it does not pass AI settings,
which are required even for migrations, and does not seed cards. Follow the
[complete deployment workflow](deploy/README.md) to create a temporary override and initialize it.
After preparing that override, these commands start and inspect the stack:

```bash
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml up -d --build
docker compose --env-file .env -f docker-compose.yml -f /tmp/loredeck-compose.local.yml ps --all
```

Default URLs are `http://localhost:8080` for the frontend and `http://localhost:8000/decks`
for the API. API documentation is disabled in Compose. The deployment guide includes the seed
step, logs, shutdown, rebuilding, and configuration limitations.

## Working with Codex

Read [AGENTS.md](AGENTS.md) and the nearest component instructions before changing files.
Nested instructions refine repository-wide guidance. Discover task-specific workflows in
[.agents/skills](.agents/README.md#skills) and read the relevant `SKILL.md`.
Give Codex a concrete goal, references, target scope, tasks, constraints, and acceptance criteria.
The [agent guide](.agents/README.md) provides a practical English prompt using
`Goal / Refs / Target / Tasks / Rules / Acceptance`, context-management guidance, verified tool
installation examples, and the distinction between repository requirements and optional tools.

Keep changes focused, preserve unrelated work, run applicable checks, and review the diff before
committing. Repository hooks are configured in [.pre-commit-config.yaml](.pre-commit-config.yaml).

## License

A license has not yet been specified: this repository contains no LICENSE file or license declaration
in its application manifests. Its open-source intent does not establish a reuse license.
