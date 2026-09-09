# LoreDeck Frontend Instructions

The frontend is an independent client of backend APIs; do not import, expose, or manually mirror Python ORM models. Reuse API contracts and generated client types once generation is available instead of maintaining duplicate definitions.

Keep feature-specific code near its feature. The frontend stack is not selected: do not assume Vue, a component library, or a state-management system, and add framework-specific commands only after corresponding configuration exists.
