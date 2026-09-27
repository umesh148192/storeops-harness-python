# Sprint 3.1 — Regional rollup foundations: store directory + Report schema + event name

## Goal

Add the minimal prerequisites the regional rollup feature needs that don't exist yet: a way to
list `Store` records by region, and the `Report`/`EventName` additions the aggregation sprint
(3.2) will use. No business logic, no new route — purely additive types/data.

## Modules / layers touched

- `src/storeops/shared/stores.py` (**new file**) — a seeded, in-memory store directory.
- `src/storeops/reports/types.py` — extend `Report`.
- `src/storeops/shared/events.py` — extend `EventName`.
- Tests: `tests/storeops/shared/test_stores.py` (new), `tests/storeops/reports/test_types.py`
  (new, if one doesn't already exist — check first), `tests/storeops/shared/test_events.py`
  (extend existing).

This is 3 non-test files — at the sizing limit per `sprint-decomposition.md`; do not add anything
beyond what's listed above in this sprint.

## Design

- `shared/stores.py`: a module-level seeded list of `Store` (imported from `shared.entities`),
  e.g. `store-1`/"Downtown"/"North", `store-2`/"Uptown"/"North", `store-3`/"Southside"/"South" —
  keep `store-1`'s id/name/region identical to `shared/deps.py`'s existing `_FAKE_STORE` so the two
  don't disagree. Expose `list_stores_by_region(region: str) -> list[Store]` returning stores
  whose `.region` matches exactly (case-sensitive), `[]` if none match. Do not modify
  `shared/deps.py`.
- `reports/types.py`: change `Report.store_id: str` to `store_id: str | None = None`; add
  `region: str | None = None`; add `blocked_tasks: list[Task] = []` (import `Task` from
  `storeops.activities.types` — a type-only import of another module's `types.py`, consistent with
  `reports/service.py` already importing `activities.types.TaskStatus`).
- `shared/events.py`: add `REGIONAL_ROLLUP_GENERATED = "REGIONAL_ROLLUP_GENERATED"` to `EventName`.

## Acceptance criteria

- **AC1**: GIVEN the seeded store directory, WHEN `list_stores_by_region("North")` is called,
  THEN it returns exactly the seeded stores whose region is `"North"` (and none from other
  regions).
- **AC2**: GIVEN an unseeded region name, WHEN `list_stores_by_region("Nonexistent")` is called,
  THEN it returns `[]` (not an error — this is a plain lookup helper, not a service method; the
  caller in sprint-3.2 decides what an empty result means).
- **AC3**: GIVEN no arguments, WHEN a `Report` is constructed with only `id`, `report_type`, THEN
  `store_id` defaults to `None`, `region` defaults to `None`, and `blocked_tasks` defaults to `[]`
  (backward compatible with existing `STORE_SUMMARY` construction, which still explicitly passes
  `store_id=...`).
- **AC4**: `EventName.REGIONAL_ROLLUP_GENERATED` exists and equals `"REGIONAL_ROLLUP_GENERATED"`.

## Non-goals

- No change to `shared/deps.py`, `get_current_store`, or `get_current_user`.
- No new `reports` route, no `reports/service.py` change (that's sprint-3.2).
- No `stores` domain module (no routes/repository/service for stores) — this is a plain lookup
  helper, not a new bounded module, and is intentionally not subject to `lint-imports`' per-module
  repository contracts.
- No change to `generate_store_summary`'s existing behavior or its existing test expectations.

## Load-bearing architecture-principles.md rules

- Rule 1 (module boundary) is N/A for `shared/stores.py` itself (not one of the 5 domain modules),
  but `reports/types.py` importing `activities.types.Task` must stay a `types.py`-to-`types.py`
  import, never a `repository.py` import — confirm `lint-imports` still shows 7/7 kept after this
  change.
