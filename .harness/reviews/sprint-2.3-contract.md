# Sprint 2.3 Contract

## Sprint ID
sprint-2.3

## Goal
Update `alerts` to notify the resolved Department Lead on `SLA_BREACH` and the resolved Store Manager on the new escalation event, resolving recipients read-only via `programmes.service` (sprint-2.1's lookups), with a documented fallback when no programme or no member in that role exists.

## Modules / layers touched
- `src/storeops/alerts/service.py` — update `_on_sla_breach` recipient resolution; add `_on_sla_escalation` handler; register it in `register_event_handlers`
- `tests/storeops/alerts/test_service.py` — coverage for both handlers, including the fallback paths

## Acceptance criteria
### AC1: SLA_BREACH notifies the programme's Department Lead when resolvable
GIVEN an `SLA_BREACH` event payload with a `programme_id` that has at least one `DEPARTMENT_LEAD` member
WHEN the handler processes the event
THEN it creates a `Notification` (via `AlertService`/`AlertRepository`) with `alert_type=SLA_BREACH` addressed to that Department Lead's `user_id`, not the task's assignee.

### AC2: SLA_BREACH falls back to the assignee when no Department Lead is resolvable
GIVEN an `SLA_BREACH` event payload where `programme_id` is missing, or the programme has no `DEPARTMENT_LEAD` member
WHEN the handler processes the event
THEN it creates the notification addressed to the payload's `assignee_id` instead (preserving today's behavior), and does nothing if neither is available.

### AC3: escalation notifies the programme's Store Manager when resolvable
GIVEN the new escalation event payload with a `programme_id` that has at least one `STORE_MANAGER` member
WHEN `_on_sla_escalation` processes the event
THEN it creates a `Notification` with `alert_type=ESCALATION` addressed to that Store Manager's `user_id`.

### AC4: escalation is a no-op when no Store Manager is resolvable
GIVEN the escalation event payload where `programme_id` is missing, or the programme has no `STORE_MANAGER` member
WHEN the handler processes the event
THEN no notification is created and no exception propagates out of the event handler.

## Explicit non-goals
- No new alerts route or response shape change to `GET /api/alerts` — recipients still read their notifications through the existing endpoint.
- No retry/delivery-guarantee logic for the event bus itself (it remains synchronous, in-process, best-effort, as today).
- No change to `programmes/service.py` beyond what sprint-2.1 already added.

## Architecture principles that are load-bearing
- Rule 1: Module boundary — recipient resolution calls `programmes.service` (already how `programmes/service.py` itself reads from `staff.service`), never `programmes.repository` directly.
- Rule 2: Event bus only — this sub-sprint only adds subscribers; `alerts` must not import `activities.service` to trigger anything.
- Rule 5 is not applicable (not `reports/`), but the same discipline applies: every call into `programmes.service` here must be read-only (`list_department_leads`/`list_store_managers`), never a write method.

## Implementation notes for the Generator
- Both handlers should catch `NotFoundError` from `programmes.service` (e.g. a payload referencing a deleted programme) and fall back to no-op/assignee rather than letting the exception escape the event handler — an event handler raising would break the emitting caller's request per `EventBus.emit`'s synchronous dispatch.
- Pick the first matching member deterministically (e.g. list order) if a programme has more than one Department Lead or Store Manager; document that choice in `generator-summary.md` rather than leaving it implicit.
