---
name: frontend-api-creator
description: Create, update, review, or test LoreDeck frontend integrations with its FastAPI backend under apps/frontend. Use for Axios clients and interceptors, typed requests and responses, JWT attachment, API error normalization, FastAPI validation errors, and runtime validation; exclude backend endpoint implementation, Vue presentation work, and generated-client setup unless separately approved.
---

# LoreDeck Frontend API Creator

Read root and frontend `AGENTS.md`, backend `AGENTS.md`, and `.agents/skills/frontend-development/SKILL.md`. Use `.agents/skills/vue-component-creator/SKILL.md` only when the task also changes component behavior. This skill owns transport integration, not presentation or backend behavior.

## Contract-first workflow

1. Inspect the implemented FastAPI route, Pydantic request and response schemas, authentication dependency, and relevant tests. Inspect generated OpenAPI when available; do not assume it captures undocumented errors or optional authentication correctly.
2. Confirm path, method, parameters or body, success response and status, error statuses, authentication, nullability, constraints, and enums. Report missing or conflicting contracts before implementation when they affect client behavior.
3. Inspect existing frontend API infrastructure, feature services, types, tests, `package.json`, and environment conventions. Preserve established patterns unless the task explicitly changes them.
4. Implement the smallest typed transport change. Never invent endpoints, fields, enums, refresh behavior, retries, caching, persistence, or response semantics; never copy Python or ORM models into frontend code.
5. Cover relevant loading, success, empty, and error transitions without silently swallowing failures or allowing overlapping requests to apply stale results.
6. Add focused tests, run only applicable scripts declared by current `package.json`, and run pre-commit on changed files when configured. Commit completed task-owned changes unless the task forbids it.

## API architecture

- Centralize Axios creation, API base URL, shared headers, token attachment, timeout policy, and cross-feature error normalization in shared `api` infrastructure.
- Keep endpoint functions and feature-specific mapping inside the owning feature. Return typed domain or contract data rather than raw untyped Axios responses.
- Keep transport concerns out of Vue presentation components. Components call feature services or composables, never Axios directly.
- Avoid generic repositories, wrappers, interceptors, or abstraction layers without a demonstrated cross-feature need.
- Read the API base URL through one project-declared Vite environment variable at the central configuration boundary. Access it through typed configuration, not scattered `import.meta.env` reads.
- Document required public variables with empty or safe placeholder values in `.env.sample`. Never commit populated environment files, credentials, tokens, or secrets.

## JWT and failures

- Follow the implemented token response, scheme, expiration, and protected-route behavior. Centralize authorization attachment and never log tokens or authorization headers.
- Normalize network and HTTP failures into one discriminated frontend error shape that retains status and safe actionable detail without exposing sensitive backend data.
- Handle `401` and `403` consistently. Coordinate authentication-state changes and navigation at one boundary; guard against repeated interceptor retries or redirect loops.
- Do not add refresh-token behavior when the backend has none. If persistent browser token storage is not already specified, stop for an explicit security decision and document exposure and user-experience trade-offs.
- Convert FastAPI `422` locations to owning VeeValidate field paths when mapping is safe. Preserve unmapped issues in a general Persian fallback instead of dropping them.
- Provide Persian user-facing messages while retaining safe diagnostic context for programmatic handling.

## Validation, lifecycle, and tests

- Keep backend/OpenAPI contracts authoritative. Use Zod for form input and runtime parsing only at risky external boundaries where malformed data would cause meaningful harm; do not parse every internal value.
- Keep Zod schemas with the owning feature and infer TypeScript types when this safely removes duplication. Do not duplicate generated or verified contract types without need.
- Prevent stale state when requests overlap through lifecycle ownership or response ordering. Use cancellation only for a real lifecycle or concurrency problem, and distinguish cancellation from user-facing failure.
- Test request construction, authentication attachment, response mapping, and normalized outcomes. At the network boundary, cover relevant success, `401`, `403`, `422`, and network-failure cases.
- Do not require end-to-end coverage for every helper; reserve it for critical integrated journeys.

Generated OpenAPI client adoption, generator selection, generated-file policy, and regeneration commands require a separate explicit repository decision. Do not introduce them through this skill.
