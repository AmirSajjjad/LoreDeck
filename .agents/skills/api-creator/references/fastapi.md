# Game FastAPI conventions

## Established constraints

- Build modular routing with `APIRouter` and compose routers at the application boundary once that setup exists.
- Define async endpoints for async workflows. Await async repository/session calls and never perform blocking I/O in an async endpoint.
- Reuse `loredeck.shared.database.get_db_session` through FastAPI dependency injection; do not create an engine or session inside a route.
- Declare explicit request and response schemas where a structured body exists, an explicit response model where appropriate, and the correct success status code.
- Use response models to keep persistence-only fields from becoming public API by accident. Do not use SQLAlchemy models as incidental response contracts.
- Keep queries in repositories, not routers. Do not catch broad exceptions silently; map only known application failures according to the nearest established pattern.
- Preserve existing paths, fields, response shapes, and status codes unless the user explicitly requests a breaking change.
- Register static routes before conflicting dynamic routes, such as `/items/me` before `/items/{item_id}`.

## Contract checklist

Resolve these before editing: HTTP method and path, owning router, authentication requirement, authorization rule, path/query parameters, body schema, response schema, success status, application errors, repository operations, transaction behavior, and required tests.

No repository convention yet selects router prefixes/tags, API versioning, dependency aliases, authentication/authorization, error envelopes, pagination shape, filtering syntax, sort syntax, schema names/files, or OpenAPI summaries/descriptions. Inspect nearby Game code when it exists. Ask the user instead of guessing when a missing decision materially changes the contract or business behavior.

For pagination, filtering, and sorting, validate public query inputs in the API schema and pass normalized values through the use case; compose persistence-specific expressions in the repository. Document externally meaningful constraints in FastAPI metadata once their form is established.

## Tests

Follow fixtures and isolation under `apps/backend/tests`. Add the cases relevant to the change: success, request validation, not found, authentication, authorization, business-rule rejection, established repository-failure mapping, filtering, sorting, pagination, and commit/rollback behavior. Use deterministic fakes for external systems and assert observable API or use-case results rather than private call sequences.

Run the narrowest affected test node or file before broader Game and backend checks.
