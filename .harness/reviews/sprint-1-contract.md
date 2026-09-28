# Sprint 1 Contract

## Sprint ID
sprint-1

## Goal
Add the bulk status update flow for operational tasks so an outgoing shift can mark multiple activities as DONE or BLOCKED in a single PATCH request, while handling partial failures without aborting the whole batch and writing an audit record for every task that actually changes.

## Modules / layers touched
- `src/storeops/activities/routes.py` — HTTP route layer
- `src/storeops/activities/service.py` — orchestration and ownership / validation logic
- `src/storeops/activities/repository.py` — bulk update + audit persistence
- `src/storeops/activities/types.py` — request/response models and audit entry schema
- `tests/storeops/activities/` — route/service coverage for success and partial-failure paths

## Acceptance criteria
### AC1: single-request bulk update accepts valid status transitions
GIVEN a valid list of task updates each containing a task id and a status of `DONE` or `BLOCKED`
WHEN the caller sends `PATCH /api/activities/bulk-status` with the payload
THEN the endpoint updates each eligible task in one operation and returns a combined result that includes the successfully updated tasks and any failed items without requiring a retry for the successful subset.

### AC2: partial failures do not break successful updates
GIVEN a payload containing a mix of valid tasks and invalid tasks (for example, missing ids, forbidden ownership, or unsupported status values)
WHEN the bulk patch is processed
THEN the service still applies the valid updates, records audit entries only for tasks that changed, and returns a `failed` list describing the rejected entries with their task ids and reasons.

### AC3: each changed task gets an audit record
GIVEN a task is successfully updated through the bulk endpoint
WHEN the patch completes
THEN the repository stores a per-task audit entry containing the task id, actor id, original status, new status, update timestamp, and optional note or reason, so the shift handover trail is attributable and reviewable.

### AC4: task ownership is enforced per item
GIVEN a caller attempts to update tasks they do not own and a manager-level override is not in effect for that task
WHEN the bulk request includes those tasks
THEN the endpoint rejects only those items with a `FORBIDDEN` response and continues processing the remaining valid tasks instead of failing the entire batch.

## Explicit non-goals
- No redesign of the authentication system; the feature uses the existing placeholder `UserContext`/`Depends(get_current_user)` behavior without adding a login flow.
- No database migration or persistence outside the in-memory repository model used by StoreOps today.
- No bulk create/delete flows for activities; this sprint only covers bulk status updates.
- No new module such as `audit` or `handover` is introduced unless needed for the repository's in-memory audit trail; the change stays within the activities domain.
- No changes to `staff`/`reports` routers or deferred demo-only endpoints.

## Architecture principles that are load-bearing
- Rule 1: Module boundary — `routes.py` must call `service.py` only; bulk update logic belongs in the service/repository layers.
- Rule 2: Event bus only — if a task becomes `BLOCKED` and the task is `CRITICAL`, the existing SLA breach event behaviour should still run through `event_bus.emit(...)` rather than direct cross-module side effects.
- Rule 3: Error contract — all validation and forbidden cases must raise `AppError` subclasses (`ValidationError`, `ForbiddenError`, `NotFoundError`) and never raw exceptions.
- Rule 4: Layer separation — business rules for ownership and partial-batch handling stay in `service.py`, not in the route handler.

## Implementation notes for the Generator
- Prefer a request model shaped like `{ "updates": [{ "task_id": "...", "status": "DONE", "note": "..." }] }` and a response shaped like `{ "updated": [...], "failed": [...] }` to keep the API explicit and testable.
- Keep the repository update atomic per item; the overall endpoint is a batch, but each task update is still an independent write so partial failures are isolated.
- The audit trail should be stored as a list on the repository or as a separate in-memory map keyed by task id so the same task can accumulate multiple handover records without losing chronology.
