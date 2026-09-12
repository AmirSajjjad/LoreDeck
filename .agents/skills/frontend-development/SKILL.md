---
name: frontend-development
description: Create, update, refactor, review, or verify LoreDeck Vue frontend code under apps/frontend. Use for frontend implementation and code-review tasks; keep detailed component generation, API-client generation, and dedicated testing workflows in their own future skills.
---

# LoreDeck Frontend Development

Read root `AGENTS.md` and `apps/frontend/AGENTS.md` before acting. Those files define the authoritative frontend conventions; do not duplicate or override them here.

Use the approved stack: Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios, Tailwind CSS, VeeValidate, Zod, Vitest, and Playwright. `shadcn-vue` remains deferred; add it only when a later task explicitly approves it after evaluating real component needs.

## Workflow

1. Inspect the requested feature, neighboring frontend code, current `package.json`, and established patterns before proposing or editing code.
2. When API behavior is involved, inspect implemented FastAPI routes and schemas or the generated OpenAPI schema. Treat implemented contracts as authoritative; never invent endpoints, fields, enums, authentication rules, or response shapes.
3. Keep changes inside the requested feature and the smallest necessary shared boundaries. Preserve unrelated changes and avoid speculative infrastructure.
4. Implement relevant loading, empty, error, and success states. Build Persian-first, RTL, mobile-first responsive UI with semantic HTML, accessible names, keyboard interaction, visible focus, and correctly associated errors.
5. Add or update focused tests for changed behavior. Mock network traffic at the API/service boundary, not component internals.
6. Run only scripts declared by the current `package.json`, using the repository-selected package manager. Run relevant format, lint, type-check, test, end-to-end, and build scripts; report a missing required script instead of inventing a command. Run pre-commit on changed files when configured without installing or synchronizing dependencies unless authorized.
7. Review the final diff, then commit completed task-owned changes with a concise Conventional Commits message unless the task forbids committing. Report files, checks, commit, and unresolved blockers.

## Boundaries

- Organize business behavior by owning feature, including `auth`, `profile`, and `readings`.
- Keep shared HTTP and cross-feature infrastructure in shared frontend directories such as `api`; keep reusable presentation components in `components`.
- Keep feature-specific components, composables, schemas, API functions, and types inside the owning feature.
- Route Vue components through feature services and centralized Axios configuration. Do not call Axios directly from page or presentation components.
- Use global Pinia state only for state shared across routes or features; prefer local or composable state otherwise.
- Do not import backend Python modules or ORM models. Prefer generated contract types when configured.
- Avoid `any`; contain and document unavoidable boundary uses. Use Composition API, `<script setup lang="ts">`, and typed props and emits.

## Forms

- Use VeeValidate for form state and Zod for user input and necessary boundary validation.
- Keep schemas with their owning feature and infer TypeScript types when this removes safe duplication.
- Match verified backend constraints and map FastAPI `422` field errors consistently to form fields, with Persian messages and a safe form-level fallback.
- Do not validate every internal object or duplicate generated API types without a concrete boundary need.

Detailed recipes for generating components, generating API clients, or building test infrastructure are outside this skill and belong to dedicated future skills.
