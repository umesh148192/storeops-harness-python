# Sprint 4.1 — activities: add `department` field to Task

## Goal

Add a `department: str | None = None` field to `Task`, `TaskCreate`, and `TaskUpdate` so a task
can carry a department assignment. This is the prerequisite sprint-4.2 (planogram template
cloning) needs to stamp a department onto each cloned task.

## Modules / layers touched

- `src/storeops/activities/types.py` — add the field to `Task`, `TaskCreate`, `TaskUpdate`.
- No change expected to `routes.py`, `service.py`, or `repository.py`: `create_activity` already
  does `Task(id=..., **data.model_dump())`, `update_activity` already does
  `self._repo.update(task_id, **data.model_dump(exclude_unset=True))`, and
  `ActivityRepository.update` already accepts arbitrary `**fields` — all three are generic over
  `Task`'s field set today and need no logic changes for a new field to flow through. Verify this
  holds after adding the field; if it doesn't, that's a signal the field was modeled wrong, not a
  reason to add bespoke plumbing.
- Tests: extend `tests/storeops/activities/test_routes.py` (and/or `test_service.py`) — check
  current file contents first, add cases rather than restructuring existing ones.

## Acceptance criteria

- **AC1**: GIVEN a `TaskCreate` payload including `"department": "Grocery"`, WHEN
  `POST /api/activities` is called, THEN the response `Task` has `department == "Grocery"`.
- **AC2**: GIVEN a `TaskCreate` payload that omits `department`, WHEN `POST /api/activities` is
  called, THEN the response `Task` has `department is None` (existing callers remain unaffected —
  the field is additive, not required).
- **AC3**: GIVEN an existing task, WHEN `PATCH /api/activities/{task_id}` is called with
  `{"department": "Electronics"}`, THEN the returned `Task`'s `department` is updated to
  `"Electronics"` and no other field on the task changes.
- **AC4**: GIVEN an existing task with `department` set, WHEN `GET /api/activities/{task_id}` is
  called, THEN `department` is present with the correct value in the JSON response body.

## Non-goals

- No `department` query filter added to `GET /api/activities` — the existing filters
  (`programme_id`, `status`) are untouched; adding a third filter is not requested here.
- No enum or validation constraining allowed department values. `department` is a free-form
  `str | None`, matching the codebase's current lack of any `Department` entity.
- No change to `evaluate_sla`, `bulk_update_status`, or any event payload — `department` is not
  added to `SLA_BREACH`/`SLA_ESCALATION` payloads in this sprint.
- No new `Department` module, repository, or route of any kind.

## Load-bearing architecture-principles.md rules

- **Rule 4** (layer separation) — this is a pure schema/type change; no business logic is added to
  `routes.py` or `service.py`. If any of those files needs more than a mechanical pass-through to
  accommodate the new field, stop and flag it rather than improvising new logic.
