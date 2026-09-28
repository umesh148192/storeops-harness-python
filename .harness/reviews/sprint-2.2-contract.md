# Sprint 2.2 Contract

## Sprint ID
sprint-2.2

## Goal
Add a `due_date` to activities and an idempotent SLA evaluation that detects HIGH/CRITICAL tasks past due and not `DONE`, emitting one `SLA_BREACH` event the first time a task is found overdue, and a separate escalation event once a configurable grace period has elapsed with the task still unresolved — without re-emitting either event on repeated evaluation runs.

## Modules / layers touched
- `src/storeops/activities/types.py` — `due_date` field on `Task`/`TaskCreate`/`TaskUpdate`; SLA check response schema
- `src/storeops/activities/repository.py` — per-task SLA notification state (has-breached / has-escalated flags) so re-running the check doesn't duplicate events
- `src/storeops/activities/service.py` — the evaluation method and event emission
- `src/storeops/activities/routes.py` — an endpoint to trigger the evaluation (intended for an external scheduler to call periodically; this codebase has no in-process scheduler — see `app-context.md`)
- `src/storeops/shared/events.py` — add an `EventName` member for the escalation event
- `tests/storeops/activities/` — service/route/repository coverage

## Acceptance criteria
### AC1: overdue HIGH/CRITICAL task fires SLA_BREACH exactly once
GIVEN a task with priority `HIGH` or `CRITICAL`, a `due_date` in the past, and status not `DONE`
WHEN the SLA evaluation runs
THEN it emits `EventName.SLA_BREACH` via `event_bus.emit(...)` with the task id, assignee id, and programme id in the payload, and running the evaluation again for the same still-unresolved task does not emit a second `SLA_BREACH` for it.

### AC2: tasks not past due, already DONE, or below HIGH priority are ignored
GIVEN a task that is not yet past its `due_date`, or is `DONE`, or has priority `LOW`/`MEDIUM`
WHEN the SLA evaluation runs
THEN no event is emitted for that task.

### AC3: unresolved breach past the grace period escalates exactly once
GIVEN a task already past its `due_date` by more than the configured grace period (default value defined in code, overridable per evaluation call) and still not `DONE`
WHEN the SLA evaluation runs
THEN it emits the new escalation `EventName` with the task id, assignee id, and programme id, and running the evaluation again for the same still-unresolved task does not emit a second escalation for it.

### AC4: resolving the task stops further alerts
GIVEN a task that previously triggered `SLA_BREACH` (or escalation)
WHEN the task's status is subsequently updated to `DONE` (via the existing `update_activity`/`bulk_update_status` paths) and the SLA evaluation is run again
THEN no further `SLA_BREACH` or escalation event is emitted for that task.

## Explicit non-goals
- No in-process scheduler, cron, or background thread is added; the evaluation is exposed as an explicit, callable operation only.
- No change to how `programmes`/`alerts` resolve notification recipients — this sub-sprint only emits events with enough payload data (task id, assignee id, programme id, priority, due date) for subscribers to do that resolution (that resolution logic is sprint-2.1's lookups, consumed by sprint-2.3).
- No change to the existing per-task `TaskUpdate`-driven `BLOCKED`+`CRITICAL` SLA_BREACH emission already in `update_activity` — that behavior is left as-is; this sub-sprint adds the separate due-date-driven path.
- No UI/reporting surface for viewing SLA state — that would be a `reports`-side sprint, out of scope here.

## Architecture principles that are load-bearing
- Rule 2: Event bus only — both the breach and escalation signals must go through `event_bus.emit(...)`; `activities` must not import `alerts.service` directly.
- Rule 3: Error contract — an unknown/invalid grace period value or malformed input raises an `AppError` subclass, never a raw exception.
- Rule 4: Layer separation — the scan/evaluation logic lives in `service.py`; `routes.py` only accepts the request and calls the service; `repository.py` only stores tasks and per-task notification flags, no business rules.

## Implementation notes for the Generator
- Store the "already breached" / "already escalated" flags per task id in the repository (mirrors the audit-entry-map pattern already used for the bulk-status feature) and clear them when a task's status moves to `DONE`, or simply gate emission on `status != DONE` at evaluation time in addition to the flags — whichever keeps the logic simplest to test.
- A reasonable shape: `POST /api/activities/sla-check?grace_period_hours=24` (query param optional, defaulting to a module-level constant), returning a small summary of which task ids breached vs. escalated in that run.
- `due_date` should be an optional field (`datetime | None`) so existing tasks/tests without a due date are unaffected.
