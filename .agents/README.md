# Working with Codex and agents

[Project overview](../README.md) · [Repository instructions](../AGENTS.md)

## Instructions

Read root `AGENTS.md`, then the nearest applicable instructions:
[backend](../apps/backend/AGENTS.md) and [frontend](../apps/frontend/AGENTS.md).
Nested rules refine or override broader project guidance. Explicit task instructions apply alongside
higher-priority session requirements. Codex loads global guidance and then project instructions
from root toward its working directory; `AGENTS.override.md` wins over `AGENTS.md` at the same level.
Read component instructions explicitly when a task crosses directories. See
[official discovery rules](https://developers.openai.com/codex/guides/agents-md/).

Personal instructions such as `~/.codex/RTK.md` and codebase-memory MCP integrations may be supplied
by an agent environment. They are not tracked repository prerequisites. Follow active instructions
without assuming other contributors have the same personal configuration.

## Skills

Discover workflows with `find .agents/skills -name SKILL.md` or the Codex skills list.
Read each applicable `SKILL.md` and its referenced material before using it. Request a skill by name
(for example `$api-creator`) or describe the workflow. See the
[official skills guide](https://developers.openai.com/codex/skills/).

| Skill | Scope |
| --- | --- |
| [api-creator](skills/api-creator/SKILL.md) | Game FastAPI endpoints and contracts |
| [backend-testing](skills/backend-testing/SKILL.md) | Backend unit, database, and API tests |
| [database-change](skills/database-change/SKILL.md) | Shared models and Alembic schema changes |
| [frontend-development](skills/frontend-development/SKILL.md) | Vue implementation and review |
| [frontend-api-creator](skills/frontend-api-creator/SKILL.md) | Typed HTTP clients and errors |
| [vue-component-creator](skills/vue-component-creator/SKILL.md) | Components, accessibility, and RTL |
| [frontend-test-creator](skills/frontend-test-creator/SKILL.md) | Vitest and Playwright tests |

No documentation-specific or `caveman-compress` skill is checked in. If a personal compression skill
is available, scope it to task memory and preserve exact technical facts, code, commands, paths,
and links. Do not compress published guides into fragments or install missing skills implicitly.

## Standard prompt

Describe an observable goal, authoritative references, bounded scope, concrete tasks, constraints,
and verifiable acceptance criteria. These headings are a convention, not an enforced schema:

```text
Goal
Update the backend setup guide to match current AI configuration.

Refs
Read AGENTS.md, apps/backend/AGENTS.md, apps/backend/README.md,
apps/backend/.env.sample, apps/backend/src/loredeck/shared/config.py,
and deploy/README.md. Inspect the implementation before writing.

Target
apps/backend/README.md only.

Tasks
1. Verify required AI settings and local startup commands.
2. Document required values without credentials or invented defaults.
3. Validate relative links and run applicable documentation hooks.
4. Review the diff and report verification results.

Rules
Write clear English. Preserve unrelated changes. Do not modify code,
configuration, or dependencies. Do not install tools or commit this task.

Acceptance
Every required AI setting and working directory is documented.
Links resolve and commands match the implementation.
Report changed files, checks, and remaining blockers.
```

## Context, verification, and commits

Keep one goal per task. Reference specific paths and symbols, inspect relevant neighbors, and avoid
pasting whole directories or populated environment files. Prefer codebase-memory MCP graph tools
when supplied by the session; use targeted text searches for configuration/literals or insufficient
graph results. Current implementation remains authoritative.

Keep short task memory recording verified facts, decisions, constraints, changed files, exact
commands, pending checks, and blockers. Preserve this before compaction or handoff. Read additional
material only to resolve uncertainty. Separate implemented behavior from future plans.

Inspect `git status` before editing. Keep changes focused and preserve user work. Run applicable
checks from the [backend](../apps/backend/README.md#checks) and
[frontend](../apps/frontend/README.md#development-and-verification) guides; report failures honestly.
Review the diff, stage explicit task-owned paths, inspect `git diff --cached`, and commit only when
requested. Use descriptive Conventional Commits, such as `docs: clarify backend AI setup`.
There is no configured Markdown link checker; verify documentation links when changing guides.

## Developer tools

Installation examples below are contributor setup instructions, not permission for an agent to
install tools. Toolchains are needed only for their selected development workflow. Codex and RTK
are optional; neither is an application dependency. Do not assume any tool is installed.

### Docker Compose

Compose orchestrates PostgreSQL, migrations, API, and Nginx. Install Docker Desktop or Docker Engine
with the Compose plugin using [official platform instructions](https://docs.docker.com/compose/install/).
Verify with `docker compose version`; follow [deployment setup](../deploy/README.md) before running
`docker compose -f docker-compose.yml ps` from the repository root.

### uv

uv manages backend dependencies and executes project tools. An official Linux/macOS installation
option is `curl -LsSf https://astral.sh/uv/install.sh | sh`; review the installer first. See
[official installation alternatives](https://docs.astral.sh/uv/getting-started/installation/).
From `apps/backend`, `uv sync --dev` prepares dependencies and `uv run ruff check .` runs lint.
Use Python `>=3.13,<3.14` and the committed lockfile.

### Node.js and npm

Install Node.js `>=24.15.0 <25` with npm using the
[official download instructions](https://nodejs.org/en/download).
From `apps/frontend`, `npm ci` installs locked dependencies and `npm run dev` starts Vite.
No alternative package manager or generated API-client setup is configured.

### pre-commit

pre-commit executes the [repository hooks](../.pre-commit-config.yaml): whitespace, syntax,
merge-conflict, file-size, Ruff, ESLint, and Prettier checks. It is declared in backend dev dependencies.
After `uv sync --dev`, run from the repository root:

```bash
uv run --project apps/backend pre-commit install
uv run --project apps/backend pre-commit run --all-files
```

See [official usage](https://pre-commit.com/). Frontend hooks also require `npm ci`; Python hooks
use the prepared backend environment with `--no-sync`. Hook installation is a contributor setup step.

### Codex (optional)

Install with `npm install -g @openai/codex`, run `codex` from the repository root, and follow sign-in.
Paste a scoped prompt like the example above. Codex helps inspect, edit, and verify code; it is not
needed to run LoreDeck. See the [official CLI guide](https://developers.openai.com/codex/cli/).

### RTK (optional unless active personal instructions require it)

RTK filters shell output to reduce agent context consumption. Upstream offers binaries and installers;
a source-install option requires Rust/Cargo:

```bash
cargo install --git https://github.com/rtk-ai/rtk
rtk --version
rtk git status
rtk gain
```

Use `rtk proxy <command>` for unfiltered output. Manual prefixes need no hook.
Optional `rtk init -g --codex` integration changes personal configuration; review it before using it.
See [official installation and usage](https://github.com/rtk-ai/rtk).
An active personal rule requiring RTK prefixes is a session requirement, not a LoreDeck runtime need.
