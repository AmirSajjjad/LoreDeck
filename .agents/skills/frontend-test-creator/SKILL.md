---
name: frontend-test-creator
description: Create, update, review, run, diagnose, or fix LoreDeck frontend tests under apps/frontend. Use for Vitest unit tests, Vue Test Utils component tests, composables, Pinia stores, Zod schemas, API and router integration, Playwright journeys, and frontend test failures; exclude backend tests and installing or designing test infrastructure unless explicitly requested.
---

# LoreDeck Frontend Test Creator

Read root and frontend `AGENTS.md` plus `.agents/skills/frontend-development/SKILL.md`. Read `vue-component-creator` or `frontend-api-creator` only when the test touches those boundaries. This skill selects and implements frontend tests; it does not redefine application architecture.

## Select the test level

- Use Vitest unit tests for isolated Zod schemas, composables, stores, transformations, and route-policy logic.
- Use Vue Test Utils component tests for rendered behavior, accessibility, validation, and user interaction.
- Use integration tests when meaningful behavior depends on collaboration among components, VeeValidate forms, Pinia, Vue Router, and mocked API boundaries.
- Use Playwright only for critical supported journeys: signup; signin and defined signout behavior; profile read/update; reading creation/result; and reading history after the backend supports it.
- Do not test framework internals, trivial implementation details, or every layer for the same rule. Use snapshots sparingly and never as the only assertion for interactive behavior.

## Workflow

1. Inspect code under test, neighboring tests, shared setup, runner configuration, `package.json`, and established naming and placement. Follow repository conventions; if none exist, do not introduce a conflicting layout and surface the missing convention when it affects scope.
2. Define the observable contract and smallest suitable test level. For a confirmed regression, reproduce it with a failing test when practical, then apply the smallest relevant fix and verify the regression.
3. Use deterministic fixtures and explicit state. Restore mocks, timers, DOM changes, Pinia instances, router instances, and other shared state between tests.
4. Run the smallest relevant declared test script or supported filter during development, then all required declared checks before completion.

## Vitest and component tests

- Interact as a user would and assert visible output, emitted public events, navigation, or meaningful state. Prefer accessible roles, labels, names, and visible Persian text over CSS classes, implementation IDs, or DOM structure.
- Use clear arrange, act, and assert sections when they improve readability. Avoid arbitrary timeouts; await deterministic UI, promise, router, or network completion.
- Test relevant default, disabled, loading, empty, error, and success states. Include keyboard behavior and focus when interaction depends on them.
- For forms, cover required and representative invalid values, Persian messages that are user-visible contracts, submission success/failure, and disabled/loading behavior. Test detailed Zod rules at schema level instead of duplicating every case through components.
- For Pinia, create an isolated active store instance per test and reset state. Test public actions, getters, and observable transitions rather than internal mutations.
- For Vue Router, use an isolated memory history in unit/integration tests. Cover public, guest-only, and authenticated navigation or guards when defined; do not depend on real browser history.

## API tests

- Mock at the network boundary. Do not mock the internal implementation being tested and never call production, shared development, or other live external services.
- Verify request construction, response mapping, and relevant success, `401`, `403`, FastAPI `422`, and network-failure outcomes.
- Verify safe conversion of FastAPI validation locations into VeeValidate field errors plus the general fallback for unmapped failures when applicable.
- Keep test credentials and tokens synthetic and non-sensitive. Do not assert or print real authorization values.

## Playwright safety

- Run against an isolated test environment with repeatable setup and cleanup. Never use production credentials or data.
- Keep journeys independent and deterministic. Prefer web-first assertions and deterministic event or response waiting over sleeps.
- Capture traces, screenshots, video, or other failure artifacts only when current Playwright configuration enables them; avoid committing incidental artifacts.

## Verification

- Use only scripts present in current `package.json` and the selected package manager. Never invent command names or install missing dependencies as part of a test task without authorization.
- Run the narrowest relevant test first, then configured full unit/integration or end-to-end suites as warranted. Before completion, run applicable lint, type-check, test, build, and pre-commit checks.
- Distinguish failures caused by the change from pre-existing failures. Report exact commands, results, skipped checks, environment blockers, and remaining risk; commit only completed task-owned changes unless the task forbids it.
