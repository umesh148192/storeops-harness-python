# Sprint 3.2 — reports service: generate_regional_rollup aggregation

## Goal

Add `ReportService.generate_regional_rollup(region: str) -> Report`: a read-only aggregation
across every store in a region that computes task completion/overdue-by-category counts and the
blocked-task list, persists the `Report`, and emits `REGIONAL_ROLLUP_GENERATED` on the event bus.

## Modules / layers touched

- `src/storeops/reports/service.py` (service layer only — no route yet, that's sprint-3.3).
- Tests: `tests/storeops/reports/test_service.py`.

Depends on sprint-3.1 (`shared/stores.py`, the extended `Report` type, the new `EventName` member)
— do not re-implement or duplicate any of sprint-3.1's additions here.

## Design

`generate_regional_rollup(self, region: str) -> Report`:

1. `stores = list_stores_by_region(region)` (from `shared.stores`). If `stores` is empty, raise
   `NotFoundError(f"No stores found in region {region}")` (Rule 3 — an `AppError` subclass, same
   pattern as `get_report`).
2. For each store, `programmes_service.list_programmes(store.id)`; for each resulting programme,
   `activities_service.list_activities(programme_id=programme.id)` — collect every task across
   every store in the region into one flat list. (Read-only calls only — Rule 5.)
3. From that flat task list, compute:
   - `completed_tasks`: count where `status == TaskStatus.DONE`.
   - `total_tasks`: total count.
   - For each `TaskCategory` member, `overdue_<CATEGORY>`: count where `due_date is not None`,
     `due_date < now(UTC)`, and `status != TaskStatus.DONE` — all 5 categories always present as
     keys in `data`, even if `0`, so the shape is predictable. This is the `due_date`-based
     "overdue" definition (see spec.md decision #4) — deliberately not reusing
     `generate_store_summary`'s older `status == BLOCKED` approximation.
   - `blocked_tasks`: the list of full `Task` records where `status == TaskStatus.BLOCKED` (not
     just IDs).
4. Build and persist: `Report(id=str(uuid4()), report_type=ReportType.REGIONAL_ROLLUP,
   status=ReportStatus.READY, region=region, data={"completed_tasks": ..., "total_tasks": ...,
   "overdue_RESTOCKING": ..., ...}, blocked_tasks=[...])` via `self._repo.create(report)`.
   `store_id` is left `None` (this report describes a region, not one store — per spec.md decision
   #2).
5. After creating the report, `event_bus.emit(EventName.REGIONAL_ROLLUP_GENERATED, {"region":
   region, "report_id": report.id})`.
6. Return the created `Report`.

## Acceptance criteria

- **AC1**: GIVEN a region with 2 stores each having a programme with tasks, WHEN
  `generate_regional_rollup(region)` is called, THEN the returned `Report.data["completed_tasks"]`
  and `["total_tasks"]` reflect the combined count across both stores (not just one).
- **AC2**: GIVEN tasks in different `TaskCategory` values with past `due_date` and `status !=
  DONE`, WHEN the method runs, THEN `Report.data[f"overdue_{category.value}"]` is correct per
  category, and a category with zero overdue tasks is still present in `data` with value `0`.
- **AC3**: GIVEN a task with `status == BLOCKED`, WHEN the method runs, THEN that task's full
  record appears in `Report.blocked_tasks`, and a non-blocked task does not.
- **AC4**: GIVEN a region name with no seeded stores, WHEN `generate_regional_rollup` is called,
  THEN it raises `NotFoundError` (no `Report` is persisted).
- **AC5**: GIVEN a successful call, WHEN it completes, THEN exactly one
  `EventName.REGIONAL_ROLLUP_GENERATED` event was emitted with `payload["region"] == region` and
  `payload["report_id"] == report.id` (assert via a bus subscriber in the test, same technique as
  existing `alerts`/`activities` event tests).

## Non-goals

- No new `reports` route (sprint-3.3).
- No change to `generate_store_summary` or its `overdue_tasks` (`BLOCKED`-based) metric — the two
  metrics are intentionally allowed to disagree, per spec.md decision #4.
- No subscriber added anywhere for `REGIONAL_ROLLUP_GENERATED` — emitting it is the full scope.
- No write calls to `programmes.service`/`activities.service` (e.g. no task creation/update).

## Load-bearing architecture-principles.md rules

- **Rule 2** (event bus only) — `REGIONAL_ROLLUP_GENERATED` must be emitted via
  `event_bus.emit(...)`, never a direct call into another module's service to "notify" it.
- **Rule 3** (error contract) — the empty-region case must raise `NotFoundError`, not a bare
  `ValueError`/`Exception`.
- **Rule 5** (read-only reports) — every call this method makes into `programmes.service`/
  `activities.service`/`shared.stores` must be read-only; the Evaluator will check this explicitly.
