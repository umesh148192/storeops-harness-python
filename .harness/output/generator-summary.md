# Generator Summary — sprint-4.2

## Sprint

sprint-4.2 — `programmes`: add a fixed `PLANOGRAM` task template definition and
`POST /api/programmes/{project_id}/templates`, cloning it into the target programme's activities.
Revised design (see below): the write crosses the module boundary via
`event_bus.emit(EventName.PLANOGRAM_TEMPLATE_CLONE_REQUESTED, ...)`, handled by a new
`activities.service` subscriber; the created tasks are then fetched back via a direct, read-only
call to `activities_service.list_activities(...)` (Rule 2 explicitly permits reads via direct
service import).

## AC self-check

| AC | Description | Test | Result |
|----|---|---|---|
| AC1 | Cloning creates one `Task` per template item, each `category == PLANOGRAM`, `programme_id == project_id` | `test_clone_planogram_template_creates_one_task_per_template_item` (service) + `test_clone_template_route_returns_201_with_planogram_tasks` (route) | PASS |
| AC2 | Each created task's `department`/`priority` matches its template item exactly | `test_clone_planogram_template_applies_department_and_priority_per_item` | PASS |
| AC3 | Missing `project_id` → 404 `NotFoundError`, no tasks created as a side effect | `test_clone_planogram_template_missing_programme_raises_not_found_and_creates_nothing` (service) + `test_clone_template_route_missing_programme_returns_404` (route) | PASS |
| AC4 | Calling the endpoint twice produces two independent, non-deduplicated sets of cloned tasks | `test_clone_planogram_template_is_additive_not_deduplicated` | PASS |

## Files changed

- **Shared**: `src/storeops/shared/events.py` — added
  `EventName.PLANOGRAM_TEMPLATE_CLONE_REQUESTED`.
- **Service (activities)**: `src/storeops/activities/service.py` — added
  `register_event_handlers(bus)` and `_on_planogram_template_clone_requested(payload)`, which
  creates one `Task` per item in the event payload via the existing `create_activity`.
- **Service (programmes)**: `src/storeops/programmes/service.py` — added `_PLANOGRAM_TEMPLATE`
  (3 fixed items: Front End/HIGH, Grocery/MEDIUM, Marketing/MEDIUM) and
  `clone_planogram_template(project_id)`, which validates the programme exists, emits
  `PLANOGRAM_TEMPLATE_CLONE_REQUESTED` with the template payload, then reads back the newly
  created tasks (by diffing task ids before/after) via `activities_service.list_activities`.
- **Routes**: `src/storeops/programmes/routes.py` — added
  `POST /{project_id}/templates` → thin pass-through to `service.clone_planogram_template`.
- **Wiring**: `src/storeops/main.py` — added
  `activities_service.register_event_handlers(event_bus)` alongside the existing
  `alerts_service`/`reports_service` registrations.
- **Tests**: `tests/storeops/programmes/test_service.py` (+4 tests),
  `tests/storeops/programmes/test_routes.py` (+2 tests).

## Design revision (superseding the contract's suggested approach)

The contract's design section suggested `programmes/service.py` call
`activities_service.create_activity(...)` directly — a synchronous cross-module **write** outside
the event bus. That pattern was implemented first, but the Evaluator's review of the equivalent
prior iteration flagged it as an AMBIGUOUS Rule 2 item (a direct write call, not a read, not an
event-bus emission) rather than force-fitting it into PASS or FAIL. Revised to comply with Rule 2
as literally written, with no exception needed:

1. `programmes.service.clone_planogram_template` emits
   `EventName.PLANOGRAM_TEMPLATE_CLONE_REQUESTED` with the template payload (title/category/
   programme_id/department/priority per item) instead of calling `create_activity` directly.
2. `activities.service` subscribes to that event (via `register_event_handlers`, wired in
   `main.py` exactly like the existing `alerts`/`reports` subscriptions) and performs the actual
   `Task` creation.
3. Because the HTTP response must synchronously return the created tasks (and `event_bus.emit()`
   always returns `None`), `clone_planogram_template` reads them back afterward via
   `activities_service.list_activities(programme_id=project_id)` — a **read**, explicitly
   permitted by Rule 2 via direct service import, filtered by comparing task ids captured before
   and after the emit to isolate only the newly created batch (so pre-existing tasks in the same
   programme aren't misattributed).

This keeps `activities.service` already importing `programmes.service` at module level (unchanged,
for `create_activity`'s `programme_id` validation) as the only place a top-level cross-import
exists; `programmes.service`'s function-scoped import of `activities.service` is retained (still
needed for the read-back call) with the same `# pylint: disable-next=import-outside-toplevel,
cyclic-import` justification as before, since a top-level import in that direction would still
deadlock at startup.

## Known gaps

None. All 4 ACs pass; no file touched outside the list above.

## Local check results (run before handoff)

- `uv run mypy src` — Success, no issues found in 33 source files.
- `uv run pylint src` — 10.00/10.
- `uv run lint-imports` — 7 contracts kept, 0 broken (65 dependencies analyzed).
- `uv run pytest` — 100 passed.
- `uv run python scripts/check_coverage.py` — service 94.8% (≥80%; `programmes/service.py` itself
  at 100%, `activities/service.py` at 94% with the untested `if not payload: return` guard branch
  as the only new miss), routes 100% (≥70%), shared 97.4% (≥60%), overall 97.6% (≥70%).


