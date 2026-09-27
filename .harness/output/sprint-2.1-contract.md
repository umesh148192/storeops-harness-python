# Sprint 2.1 Contract

## Sprint ID
sprint-2.1

## Goal
Add read-only `programmes` service lookups that resolve which staff hold the Department Lead and Store Manager roles on a given programme, so the SLA breach/escalation alerting sub-sprints (sprint-2.2, sprint-2.3) have a single, testable way to find the right notification recipient without any module reading another module's repository directly.

## Modules / layers touched
- `src/storeops/programmes/service.py` — new read-only lookup methods
- `tests/storeops/programmes/test_service.py` — coverage for the new lookups, including the "no member with that role" case

## Acceptance criteria
### AC1: resolve Department Lead members for a programme
GIVEN a programme with one or more members added via `add_member`, including at least one with role `DEPARTMENT_LEAD`
WHEN `service.list_department_leads(project_id)` is called
THEN it returns exactly the `ProjectMember` records whose role is `DEPARTMENT_LEAD` for that programme, and an empty list when none exist.

### AC2: resolve Store Manager members for a programme
GIVEN a programme with one or more members, including at least one with role `STORE_MANAGER`
WHEN `service.list_store_managers(project_id)` is called
THEN it returns exactly the `ProjectMember` records whose role is `STORE_MANAGER` for that programme, and an empty list when none exist.

### AC3: unknown programme raises NotFoundError
GIVEN a `project_id` that does not exist
WHEN either lookup method is called
THEN it raises `NotFoundError` (consistent with `get_programme`'s existing behavior) rather than returning an empty list silently.

## Explicit non-goals
- No new route is added; these are internal service methods for other modules to call, not a new public endpoint.
- No change to `add_member`, `ProjectMember`, or `ProjectRole` — this sub-sprint only reads existing membership data.
- No resolution mechanism for staff outside programme membership (e.g. a store-wide "the" store manager independent of any programme) — that gap is called out as a known limitation for sprint-2.3 to inherit, not solved here.

## Architecture principles that are load-bearing
- Rule 1: Module boundary — the new methods live in `programmes/service.py` so other modules (`activities`, `alerts`) can call them as a legitimate cross-module read, never importing `programmes.repository` directly.
- Rule 4: Layer separation — filtering by role is business logic and belongs in `service.py`; `repository.list_members` is not changed.
- Rule 5 is not applicable here (this sub-sprint is not `reports/`), but the same "read-only" spirit applies: these methods must not create, update, or delete anything.

## Implementation notes for the Generator
- Reuse `self._repo.list_members(project_id)` (already exists) and filter by `ProjectRole.DEPARTMENT_LEAD` / `ProjectRole.STORE_MANAGER` in the service layer.
- Call `self.get_programme(project_id)` first (existing method) to get the `NotFoundError` behavior for free rather than duplicating the not-found check.
