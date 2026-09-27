# Generator Summary — sprint-2.3

## Sprint
sprint-2.3 — `alerts`: notify Department Lead on `SLA_BREACH` (assignee fallback) and Store Manager on `SLA_ESCALATION` (no-op fallback), resolved read-only via `programmes.service`.

## AC self-check

| AC | Description | Test | Result |
|----|---|---|---|
| AC1 | `SLA_BREACH` notifies the resolved Department Lead when resolvable | `test_sla_breach_notifies_department_lead_when_resolvable` | PASS |
| AC2 | `SLA_BREACH` falls back to the assignee when no Department Lead is resolvable | `test_sla_breach_falls_back_to_assignee_when_no_department_lead_resolvable` (plus pre-existing `test_sla_breach_event_creates_notification_for_assignee`, `test_sla_breach_event_without_assignee_is_ignored`) | PASS |
| AC3 | `SLA_ESCALATION` notifies the resolved Store Manager when resolvable | `test_sla_escalation_notifies_store_manager_when_resolvable` | PASS |
| AC4 | `SLA_ESCALATION` is a no-op (no exception propagates) when no Store Manager is resolvable | `test_sla_escalation_is_noop_when_no_store_manager_resolvable`, `test_sla_escalation_is_noop_when_programme_missing` | PASS |

## Files changed

- **Service**: `src/storeops/alerts/service.py` — `_on_sla_breach` now resolves the recipient via `programmes_service.list_department_leads(programme_id)` (first match, deterministic), falling back to `payload["assignee_id"]` when unresolvable (missing `programme_id`, `NotFoundError`, or empty list); added `_on_sla_escalation` handler resolving via `programmes_service.list_store_managers(programme_id)` with a silent no-op fallback (uses the existing `AlertType.ESCALATION` enum member — no new type needed); both `_resolve_department_lead`/`_resolve_store_manager` helpers catch `NotFoundError` explicitly (Rule 3); registered `EventName.SLA_ESCALATION` in `register_event_handlers`. Reads `programmes.service` directly (a same-process read, not a repository import — Rule 1/Rule 2 compliant).
- **Tests**: `tests/storeops/alerts/test_service.py` — added 6 new tests covering AC1-AC4 (department-lead resolution, assignee fallback, store-manager resolution, no-op on missing member and on missing programme); 3 pre-existing tests kept unchanged and still pass.

## Known gaps

None. All 4 ACs are covered by citable tests. No new `alerts` route or event-bus retry logic was added (contract non-goals). `AlertType.ESCALATION` already existed in `alerts/types.py` prior to this sprint, so no type change was required there — used as-is for escalation notifications.

## Local check results (run before handoff)

- `uv run mypy src` — Success, no issues found in 32 source files.
- `uv run pylint src` — 10.00/10.
- `uv run lint-imports` — 7 contracts kept, 0 broken.
- `uv run pytest` — 77 passed.
- `uv run python scripts/check_coverage.py` — service 94.6% (≥80%), routes 100% (≥70%), shared 97.1% (≥60%), overall 97.6% (≥70%); `alerts/service.py` itself at 91%.
