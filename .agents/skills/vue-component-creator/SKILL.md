---
name: vue-component-creator
description: Create, edit, refactor, review, or test LoreDeck Vue components, pages, layouts, and reusable form controls under apps/frontend. Use for component logic, templates, accessibility, RTL, responsive behavior, and visual states; exclude API-client generation and general test-infrastructure work.
---

# LoreDeck Vue Component Creator

Read root `AGENTS.md`, `apps/frontend/AGENTS.md`, and `.agents/skills/frontend-development/SKILL.md`. Use their stack and broad workflow as the baseline; this skill adds component-specific decisions only. `shadcn-vue` remains deferred and must not be installed or used without explicit approval in a later task.

## Component workflow

1. Inspect nearby components, tests, tokens, and feature conventions. Decide whether the UI is feature-owned or genuinely shared before choosing its location.
2. Define one focused responsibility, required states, inputs, outputs, slots, and accessibility semantics before implementation. Expose the smallest typed public API that supports current callers.
3. Implement with Vue 3 Composition API and `<script setup lang="ts">`. Use typed props and emits, computed values instead of duplicated mutable state, and composables for reusable stateful logic.
4. Avoid unnecessary watchers, direct DOM manipulation, and `any`. When one is technically required, contain it and document why the safer alternative does not work.
5. Verify relevant default, hover, focus, disabled, loading, empty, error, and success states across narrow and wide viewports in RTL.
6. Add focused Vitest component tests when rendering, interaction, validation, branching, or state transitions are significant. Test observable behavior rather than implementation details.
7. Run only relevant scripts declared by current `package.json` for lint, type-check, unit tests, build, and other configured checks. Run pre-commit on changed files when configured; report missing scripts instead of inventing commands.

## Boundaries

- Keep feature-specific components with their owning feature. Move UI to shared `components` only after real reuse across features or an established shared-system need.
- Keep pages and layouts focused on composition, routing context, and orchestration; move reusable rendering and stateful behavior down to components or composables.
- Do not call Axios from pages or presentation components. Use feature services and shared API infrastructure; leave API-client generation procedures to a dedicated skill.
- Keep local UI state local. Use Pinia only for cross-component, cross-route, or persistence needs that local state and composables cannot meet cleanly.
- Reuse project design tokens and shared primitives. Do not repeat hard-coded colors, spacing, or typography.

## Forms

- Use VeeValidate for form state, field state, and submission. Use the owning feature's Zod schema for user input and necessary boundary validation.
- Infer types from Zod when this avoids safe duplication and does not conflict with generated API types.
- Reusable controls must expose an accessible label, validation message, disabled state, and required native or ARIA attributes. Associate help and error text with the control.
- Map FastAPI `422` field errors through shared form-error handling; do not duplicate schema or backend validation logic inside templates.

## UI and accessibility

- Use Persian-first content, RTL layout, and mobile-first responsive behavior. Confirm direction-sensitive spacing, alignment, icon placement, and reading order.
- Prefer semantic HTML and native controls. Add ARIA only when native semantics cannot express the interaction.
- Support keyboard navigation and activation, preserve visible focus indicators, and restore or move focus deliberately after significant UI transitions when needed.
- Never communicate meaning through color alone. Ensure status and validation feedback has textual or semantic context.
- Give meaningful images concise Persian alt text. Treat decorative images accordingly and provide graceful card-image loading and failure fallbacks without losing card identity.

Detailed component-library scaffolding, API-client generation, and general testing-infrastructure procedures remain outside this skill.
