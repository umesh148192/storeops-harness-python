# Skill: Coding Conventions

Generator-specific. Conventions already established in `src/storeops/` — follow them exactly,
don't introduce a new pattern for a new sprint.

## Layer pattern (per module)

Every module is `routes.py` / `service.py` / `repository.py` / `types.py`, plus `__init__.py`
re-exporting `router`. Copy the shape of an existing module (`activities/` is the most complete
example) rather than inventing structure.

- **Routes are `async def`.** Depend on `storeops.shared.deps.get_current_user`/`get_current_store`
  via `Depends()` only when the endpoint needs identity/store context — not by default.
- **Service and repository methods are synchronous** — they're in-memory dict operations with
  nothing to `await`. Don't make them `async def`; that would be a fake-async idiom.
- **Repository and service are module-level singletons**: `repository = XRepository()` at the
  bottom of `repository.py`, `service = XService(repository)` at the bottom of `service.py`.
  Routes import and call the singleton, they don't construct instances.
- **Repository has a `reset()` method** (clears its in-memory store) — required for test isolation
  via `tests/storeops/conftest.py`'s autouse fixture. Every new repository needs one.

## Types

- Enums are `str`-mixed: `class TaskStatus(str, Enum)` — clean JSON serialization, matches the
  spec's string vocabulary exactly (`"TODO"`, not `"TaskStatus.TODO"`).
- Pydantic v2 `BaseModel` for both the domain type (`Task`) and its request/response schemas
  (`TaskCreate`, `TaskUpdate`) — conflated in one `types.py` per module, not split into separate
  `schemas.py`/`models.py` files.

## Errors

Raise `AppError` subclasses from `storeops.shared.errors`, never a bare exception (Rule 3 in
`architecture-principles.md`). Add a new subclass only if none of the existing five
(`NotFoundError`, `ValidationError`, `ForbiddenError`, `ConflictError`, `UnauthorizedError`) fit —
check first.

## Cross-module calls

Import another module's `service` singleton directly for reads (`from storeops.programmes.service
import service as programmes_service`). For side effects that should be decoupled, import
`storeops.shared.events.event_bus` and `emit()` — never import another module's `service` to
trigger a side effect (Rule 2).

## Tooling

- Dependency management: `uv` — add deps via `pyproject.toml`, not `pip install`.
- `mypy` config is "balanced strict" (`disallow_untyped_defs`, `warn_return_any`, not full
  `strict = true`) — annotate everything, but don't fight `Depends()` typing edge cases.
- `pylint` is configured to disable docstring-related checks — don't add docstrings just to
  satisfy a linter that isn't asking for them; do keep lines ≤100 chars.
