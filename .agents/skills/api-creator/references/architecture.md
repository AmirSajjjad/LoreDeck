# Game API architecture

## Evidence and intended flow

`apps/backend/src/loredeck/game` currently contains no API implementation beyond `__init__.py`. The stable repository infrastructure is `loredeck.shared.config`, `loredeck.shared.database`, and `loredeck.shared.models`; tests live under `apps/backend/tests`. The required Game dependency flow is:

```text
API/router → use case → service (only when necessary) → repository
```

This flow defines responsibilities but does not establish folder names, interface abstractions, or a complete Clean Architecture implementation. Inspect new neighboring code as the application grows.

## Responsibilities

### API/router

Register routes and define the HTTP method, path, dependencies, authentication/authorization checks, request parsing, status code, response model, and established application-error mapping. Keep SQLAlchemy queries, transaction workflows, reusable business rules, and endpoint-specific session manipulation out of routers. A router may receive the established session or application dependency only to pass it onward.

### Use case

Represent one application action. Coordinate application rules, repositories, and any justified domain/integration service; own the transaction boundary when consistent with nearby code; and return framework-independent application results. A use case must not depend on `APIRouter`, `Request`, `Response`, `HTTPException`, or FastAPI response objects.

### Service

Services are optional. Add one only for a meaningful operation reused by multiple use cases, substantial domain behavior, or orchestration of an external capability. Do not add a service that only forwards arguments to a repository.

### Repository

Keep SQLAlchemy queries, model loading/saving, query composition, persistence filtering/sorting/pagination, and locking here. Repositories return the result types established by nearby Game code and do not contain FastAPI dependencies, HTTP exceptions, response schemas, or presentation logic. They do not commit; the request or use-case workflow owns transactions.

The repository currently has no repository protocols or separate SQLAlchemy implementations. Introduce that distinction only when an actual boundary or existing Game convention requires it.

### Schemas

The Game package has no established schema layout yet. Use explicit Pydantic request and response schemas and place them beside the feature or in the nearest convention that exists when editing. Put transport validation in schemas and application/business rules in the use case or domain logic. Query-parameter models, ORM serialization settings, naming, and file subdivision remain undecided; derive them from nearby code or ask when the choice affects the contract. Never expose a SQLAlchemy model accidentally as the public contract.

## Dependency rules

Allowed dependencies point from the router toward the application and persistence path. Prevent these reverse or cross-boundary dependencies:

```text
repository → use case
repository → API
use case → API
shared → game-specific business logic
```

Use shared models, configuration, and `get_db_session` without moving Game rules into `loredeck.shared`.
