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
