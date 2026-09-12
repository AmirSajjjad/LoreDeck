# LoreDeck Frontend Instructions

These instructions apply under `apps/frontend` in addition to repository-level `AGENTS.md`.

## Stack and boundaries

- Use Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios, Tailwind CSS, VeeValidate, Zod, Vitest, and Playwright.
- Keep frontend independent from backend Python code. Never import, expose, or manually mirror ORM models.
- Treat FastAPI OpenAPI and implemented backend routes and schemas as authoritative. Prefer generated API types when generation is configured; never invent endpoints, fields, enums, relationships, or response shapes.
- Do not add `shadcn-vue` unless a later task explicitly approves it after evaluating actual component needs.
- Keep secrets and populated environment values out of source, logs, examples, tests, and commits.

## Architecture

- Organize product code by feature: `features/auth`, `features/profile`, and `features/readings`.
- Keep feature-owned schemas, services, composables, components, and types inside their feature. Avoid generic layers that only serve one feature.
- Put reusable presentation components in `components` and shared HTTP/client infrastructure in `api`.
- Keep route-level views thin. Page and presentation components must not call Axios directly; call feature services backed by centralized shared Axios configuration.
- Use Pinia only for state shared across routes or features. Prefer local component or composable state otherwise.
- Extract reusable stateful logic into focused composables.

## Vue and TypeScript

- Use Composition API and `<script setup lang="ts">`.
- Type props, emits, service boundaries, store state, and public composable returns.
- Avoid `any`. If technically unavoidable, contain it at a boundary and document why a safer type cannot be used.
- Keep components focused and reasonably small. Split components when responsibilities, state, or rendering branches become difficult to understand or test.
- Use semantic HTML before custom interaction patterns.

## API integration

- Verify contracts against current backend source and generated OpenAPI before implementing or changing integration code.
- Centralize base URL, headers, timeout, authentication attachment, and response normalization in shared API infrastructure.
- Keep feature-specific requests and response handling in feature services.
- Represent loading, empty, success, and error states explicitly in user-facing flows.
- Handle `401`, `403`, network failures, and FastAPI `422` validation responses consistently. Map field-level `422` errors to owning form fields and show a safe form-level fallback for unmatched errors.
- Never log access tokens, authorization headers, passwords, or sensitive response data.

## Forms and validation

- Use VeeValidate with Zod for user-facing forms.
- Keep Zod schemas near their owning feature and infer TypeScript types from them when that removes duplication without conflicting with generated API types.
- Match backend constraints and normalization rules; do not strengthen, weaken, or extend API validation by assumption.
- Provide Persian user-facing validation and submission messages.
- Validate external input and meaningful domain boundaries. Do not add schemas for every internal object.

## UI and accessibility

- Build a Persian-first, RTL interface with mobile-first responsive layouts.
- Set document language and direction correctly and test layout behavior at narrow and wide viewports.
- Give controls accessible names and visible focus states. Support keyboard operation, logical focus order, error association, and status announcements where appropriate.
- Use semantic landmarks, headings, buttons, links, labels, and form elements. Do not rely on color alone to communicate state.
- Reuse design tokens and shared components instead of duplicating colors, spacing, typography, or interaction styles.

## Authentication

- Centralize authentication state and transitions; do not scatter token handling across components or feature services.
- Follow backend token contracts exactly. Do not invent refresh, logout, persistence, or token-storage behavior.
- When storage is not specified, stop and document security and user-experience trade-offs before selecting an approach.
- Clear or transition authentication state consistently after rejected credentials or protected requests, without exposing token contents.

## Testing

- Unit-test important Zod schemas, Pinia stores, composables, and components with Vitest.
- Mock network traffic at the API/service boundary; avoid mocking component internals or making tests depend on live services.
- Add Playwright coverage for critical user journeys once Playwright configuration and scripts exist, including authentication, profile, and reading flows supported by current backend contracts.
- Test observable behavior, Persian/RTL states, validation failures, keyboard interaction, and important loading/error paths.

## Verification and Git

- Inspect `package.json` before running checks. Use only the selected package manager and scripts declared there; never guess script names or substitute ad hoc tool commands.
- Before completion, run every relevant declared script for formatting checks, lint, type-checking, unit tests, end-to-end tests, and production build. If a required category has no script, report it as a blocker instead of inventing a command.
- Run repository pre-commit checks on changed files when pre-commit is available. Do not install or synchronize dependencies unless the task authorizes it.
- Run the narrowest relevant checks first, then all applicable declared frontend checks. Report exact commands, results, skipped checks, and blockers.
- Preserve unrelated working-tree changes. Stage and commit only files owned by the task, using a concise Conventional Commits message; do not create empty commits or rewrite history unless explicitly requested.
