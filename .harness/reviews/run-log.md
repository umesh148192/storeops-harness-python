# Run Log

One entry per sprint, appended in completion order. Never overwritten.

---

## sprint-1 — bulk shift-handover status update

- **Goal**: Bulk `PATCH /api/activities/bulk-status` endpoint accepting multiple task status updates in one request, with partial-failure handling, ownership enforcement, and per-task audit records.
- **Final verdict**: PASS
- **Iterations used**: not tracked at the time (run-log.md did not yet exist for this sprint) — backfilled from the final verified state: `mypy`, `pylint` (10.00/10), `lint-imports` (7/7 kept), `pytest` (58 passed at the time), and `check_coverage.py` (98.2% overall) all green with no open gaps.
- **Escalation**: No.
- **Estimated token cost**: not tracked (pre-dates run-log.md).
- **Quality-trend notes**: One recurring implementation snag worth flagging for skill-file review — a repository method literally named `list` (`ActivityRepository.list`) caused a `mypy` self-shadowing error on its own return-type annotation; fixed by annotating with `typing.List` instead of the lowercase builtin. Not yet recurred in ≥3 sprints, so no skill-file change triggered by this entry alone.

---

## sprint-2.1 — programmes: Department Lead / Store Manager lookups

- **Goal**: Add read-only `list_department_leads(project_id)` / `list_store_managers(project_id)` service methods so downstream SLA alerting (sprint-2.2, sprint-2.3) can resolve notification recipients without any module reading another module's repository directly.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: small — single-file service change (~16 lines) + one test file addition (~55 lines); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean first-pass PASS, 100% weighted score, no AMBIGUOUS items. No repeated issue pattern to flag.

---

## sprint-2.2 — activities: due_date field + SLA breach/escalation evaluation

- **Goal**: Add a `due_date` field to tasks and an idempotent SLA evaluation (`evaluate_sla`) that detects overdue HIGH/CRITICAL tasks, emits `SLA_BREACH` once, and emits a new `SLA_ESCALATION` event once a configurable grace period elapses with the task still unresolved.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: medium — 5 source files touched (~80 lines net) + 3 test files (~140 lines); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean first-pass PASS, 100% weighted score, no AMBIGUOUS items. Generator proactively added a `ValidationError` for negative `grace_period_hours` beyond the literal AC list, disclosed honestly in `generator-summary.md`'s "known gaps" as an implied-not-numbered requirement — good example of the "disclosed gap ≠ automatic failure" principle in `grading-criteria.md` working as intended.

---

## sprint-2.3 — alerts: notify Department Lead / Store Manager on SLA breach and escalation

- **Goal**: Update `alerts` to notify the resolved Department Lead on `SLA_BREACH` (falling back to the assignee) and the resolved Store Manager on `SLA_ESCALATION` (no-op fallback), resolving recipients read-only via `programmes.service`'s sprint-2.1 lookups.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: small-medium — single service file change (~47 lines net) + one test file (~79 lines); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean first-pass PASS, 100% weighted score, no AMBIGUOUS items. `AlertType.ESCALATION` already existed in `alerts/types.py` from an earlier phase, so no type change was needed — Generator correctly reused it instead of adding a duplicate. This completes all three sub-sprints of the SLA breach alerting feature (2.1 → 2.2 → 2.3), each passing on the first iteration.

---

## sprint-3.1 — regional rollup foundations: store directory + Report schema + event name

- **Goal**: Add a seeded store→region directory (`shared/stores.py`), extend `Report` with `region`/`blocked_tasks`/optional `store_id`, and add `EventName.REGIONAL_ROLLUP_GENERATED` — the prerequisites the regional rollup aggregation (sprint-3.2) and route (sprint-3.3) need.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: small — 1 new file (~13 lines) + 2 small edits (~7 lines net) + 3 test files (~2 new, 1 extended, ~35 lines total); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean first-pass PASS, 100% weighted score, no AMBIGUOUS items. First sprint of a new feature ("Add regional rollup report") — Planner flagged 6 scope decisions up front in `spec.md` (new store directory, optional `Report.store_id`, new `blocked_tasks` list field, `due_date`-based overdue definition diverging intentionally from the older `STORE_SUMMARY` metric, wiring the previously-excluded `reports` router into `main.py`, and the event-bus trigger being emit-only with no new subscriber) before the developer approved — worth noting as a good pattern for future multi-decision features.

---

## sprint-3.2 — reports service: generate_regional_rollup aggregation

- **Goal**: Add `ReportService.generate_regional_rollup(region)` — a read-only aggregation across every store in a region (completion/overdue-by-category counts, blocked-task list), persisting a `Report` and emitting `EventName.REGIONAL_ROLLUP_GENERATED`.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: medium — single service method (~35 lines net) + one test file with 5 new tests (~90 lines); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean PASS on the single Generator-facing iteration, 100% weighted score, no AMBIGUOUS items — though the Generator self-caught and fixed two issues before requesting Evaluator review: a missing `event_bus` import (mypy/pylint failure) and a test that subscribed on a disconnected local `EventBus()` instance instead of the shared singleton the service actually emits on. Neither counted against the score since both were fixed pre-handoff and the final local check run was fully green, but worth flagging as a repeat-risk pattern: **when a service emits via the shared `storeops.shared.events.event_bus` singleton (not a bus passed into `register_event_handlers`), tests verifying emission must subscribe directly on that same imported `event_bus`, not a freshly constructed `EventBus()`** — this is the second time this exact singleton-vs-local-instance distinction has come up (see also `activities`/`alerts` tests already using the correct pattern); if it recurs in sprint-3.3 or later, consider adding a line to `architecture-principles.md` or `grading-criteria.md` calling this out explicitly.

---

## sprint-3.3 — reports route: GET /api/reports/region/{region_id} + main.py wiring

- **Goal**: Expose `generate_regional_rollup` as `GET /api/reports/region/{region_id}` and wire the previously-excluded `reports` router into `main.py` for the first time, completing the "Add regional rollup report" feature.
- **Final verdict**: PASS
- **Iterations used**: 1 (of 3)
- **Escalation**: No.
- **Estimated token cost**: small — 2 small edits (~6 lines net across `routes.py` and `main.py`) + one new test file with 3 tests (~40 lines); estimate based on diff size, not exact token count.
- **Quality-trend notes**: Clean PASS on the single Generator-facing iteration, 100% weighted score, no AMBIGUOUS items. One self-caught-and-fixed test-authoring issue: the first draft of the router-wiring smoke test iterated `app.routes` and read `.path` off each entry, which raised `AttributeError` because this FastAPI/Starlette version wraps included routers in an object without a `.path` attribute; fixed by asserting against the more stable `app.openapi()["paths"]` instead. This is a new, distinct pattern from sprint-3.2's singleton-vs-local-`EventBus()` issue — no recurrence of that one this sprint, so no skill-file update triggered. **This completes all three sprints of the "Add regional rollup report" feature (3.1 → 3.2 → 3.3), each passing on the first iteration.**
