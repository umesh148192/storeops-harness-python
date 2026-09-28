# Skill: Architecture Principles

Shared foundation — every agent reads this. These are the 5 non-negotiable architecture rules for
StoreOps. Each rule below names its real enforcement mechanism in this repo — not a generic
principle.

## Rule 1: Module boundary

No module imports directly from another module's `repository.py`. Cross-module reads go through
the target module's `service.py` only (e.g. `programmes/service.py` calls
`staff_service.get_user(...)`, never `staff.repository`).

**Enforced by**: `import-linter`, contracts in `pyproject.toml` under `[[tool.importlinter.contracts]]`
— one `layers` contract (`routes → service → repository` per module) plus five `forbidden`
contracts (one per module's repository, `allow_indirect_imports = "True"` so legitimate
service-to-service reads aren't flagged as violations — only *direct* repository imports are).
Run: `uv run lint-imports`.

## Rule 2: Event bus only

Side effects that cross module boundaries fire through `storeops.shared.events.event_bus.emit(...)`
— never a direct import of another module's `service` for the purpose of triggering it. Example:
`activities/service.py` emits `EventName.SLA_BREACH`; `alerts/service.py` and `reports/service.py`
subscribe to it in `register_event_handlers`, wired up once in `main.py`. Reads (validating a
`programme_id` exists, looking up a user) ARE allowed via direct service import — Rule 2 is only
about side effects, not reads (that's Rule 1's job to allow).

**Enforced by**: LLM review — grep for direct imports of `alerts.service`/`reports.service` from
`activities`/`programmes` (a `forbidden` import-linter contract also catches this specific pair
today, but the rule is broader than what one contract can express as the module graph grows).

## Rule 3: Error contract

No raw `raise Exception(...)` (or any bare stdlib exception) in `routes.py` or `service.py`. All
errors are `AppError` subclasses (`storeops/shared/errors.py`): `NotFoundError`, `ValidationError`,
`ForbiddenError`, `ConflictError`, `UnauthorizedError`, each carrying `code`, `message`,
`status_code`. `main.py` has one `@app.exception_handler(AppError)` that maps any of them to JSON —
routes/services never touch HTTP status codes directly.

**Enforced by**: `grep -rn "raise Exception" src/storeops` (zero hits expected) + LLM review for
other raw builtin exceptions (`raise ValueError`, `raise RuntimeError`, etc. — same violation,
different spelling).

## Rule 4: Layer separation

Routes → Service → Repository, no skipping. `routes.py` contains HTTP concerns and validation
only, calling `service.py` — never `repository.py` directly. `repository.py` is a leaf: in-memory
dict access only, no imports from other `storeops.*` packages, no HTTP-shaped return values.

**Enforced by**: the `layers` import-linter contract (structural half) + LLM review (the semantic
half — routes must not embed business logic like the ownership check pattern used in
`activities/service.py`'s `delete_activity`, not in `activities/routes.py`).

## Rule 5: Read-only reports

`reports/service.py` and `reports/repository.py` may call `activities.service`/`programmes.service`
for read-only aggregation (see `generate_store_summary`) but must never call a write method
(`create_*`, `update_*`, `delete_*`, `add_member`) on any other module's service.

**Enforced by**: LLM review — for any diff touching `reports/`, confirm every cross-module call is
to a method whose name and return type are read-only.
