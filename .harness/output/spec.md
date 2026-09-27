STATUS: AWAITING APPROVAL

Feature: **"Add regional rollup report"** — `GET /api/reports/region/{region_id}` aggregating task
completion counts, overdue counts by `TaskCategory`, and blocked-task lists across every store in
a region, with report generation announced on the event bus. Three sprints, ordered by dependency
(a module other sprints read from is built first, per Rule 1):

**sprint-3.1** — foundations: add a minimal in-memory store directory (`shared/stores.py`) that
can list `Store` records by region — this does not exist anywhere in the codebase today, only a
single hardcoded store — plus the `Report` schema/event additions the later sprints need
(`blocked_tasks` field, `store_id` loosened + new `region` field so a report can describe a region
instead of one store, and a new `REGIONAL_ROLLUP_GENERATED` event name).

**sprint-3.2** — `reports` service: add `generate_regional_rollup(region)`, a read-only aggregation
across every store in the region (via `shared.stores`, `programmes.service`, `activities.service`)
that builds completion/overdue-by-category counts and the blocked-task list, persists the `Report`,
and emits `REGIONAL_ROLLUP_GENERATED` on the event bus.

**sprint-3.3** — `reports` route: add `GET /api/reports/region/{region_id}` and wire the `reports`
router into `main.py` for the first time (see note below).

## Decisions flagged for review before approval

1. **New store directory required.** `Store` (in `shared/entities.py`) has a `region` field, but
   the only `Store` instance anywhere in the app is the single hardcoded one in
   `shared/deps.py::get_current_store`. There is no way today to answer "which stores are in
   region X." Sprint-3.1 adds a small seeded lookup (`shared/stores.py`, same
   hardcoded-seed-data pattern already used for `staff`'s one seeded user and
   `shared/deps.py`'s one fake store) rather than inventing a full `stores` domain module with its
   own routes/repository — this is scoped strictly to what the rollup needs. `shared/deps.py`
   itself is left untouched.
2. **`Report.store_id` becomes optional, plus a new `region` field.** `Report.store_id: str` is
   currently required and models "this report is about one store" — true for `STORE_SUMMARY` but
   not for `REGIONAL_ROLLUP`. Sprint-3.1 changes it to `store_id: str | None = None` and adds
   `region: str | None = None`; existing `STORE_SUMMARY` generation is unaffected (still always
   passes `store_id`).
3. **Task lists, not just counts.** The request asks for "completion rates," "overdue counts by
   category" (both expressed as raw counts in `Report.data: dict[str, int]`, consistent with
   `generate_store_summary`'s existing convention of counts over pre-computed percentages — a rate
   is `completed_tasks / total_tasks`), and "blocked task lists" — that last one needs an actual
   list, so `Report` gets a new `blocked_tasks: list[Task]` field (full task records, not just IDs)
   rather than trying to force it into the existing `dict[str, int]` shape.
4. **"Overdue" uses `due_date`, not the `BLOCKED` status.** `generate_store_summary`'s existing
   `overdue_tasks` metric is actually `status == BLOCKED` as a stand-in, predating the `due_date`
   field added in the SLA-alerting feature. The new rollup instead uses the real definition
   (`due_date` in the past and `status != DONE`), matching `activities.service.evaluate_sla`'s
   logic — a small intentional inconsistency with the older `STORE_SUMMARY` metric, called out
   here rather than silently diverging.
5. **Wiring the `reports` router into `main.py`.** `app-context.md` currently states the `reports`
   router is deliberately not included ("a deferred demonstration feature... don't fix this by
   wiring them in unless a sprint contract explicitly asks for it"). This request explicitly asks
   for a live `reports` endpoint, so sprint-3.3 does wire it in — flagged here since it changes a
   documented piece of current state, not because it's being done quietly.
6. **What "triggers ... via the event bus" means.** No sprint asks `alerts` (or any other module)
   to subscribe to the new event — only that generating a regional rollup report emits
   `REGIONAL_ROLLUP_GENERATED` (payload: `region`, `report_id`) as an extensibility hook, mirroring
   how `evaluate_sla` emits its events after computing results. Adding a subscriber would be new
   scope not requested here.
