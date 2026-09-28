# Sprint 3.3 — reports route: GET /api/reports/region/{region_id} + wire router into main.py

## Goal

Expose sprint-3.2's `generate_regional_rollup` as a live REST endpoint, and wire the `reports`
router into the app for the first time (currently deliberately excluded — see spec.md decision
#5).

## Modules / layers touched

- `src/storeops/reports/routes.py` — add the route.
- `src/storeops/main.py` — add `app.include_router(reports_router)`.
- Tests: `tests/storeops/reports/test_routes.py` (new file — none exists today since the router
  had no routes; check first in case this changed).

Depends on sprint-3.2 (`generate_regional_rollup`) — do not re-implement aggregation logic in the
route; the route is a thin HTTP wrapper only (Rule 4).

## Design

- `reports/routes.py`: import `service` from `reports.service` (already the pattern in every
  other `routes.py`) and `Report` from `reports.types`; add:
  ```python
  @router.get("/region/{region_id}", response_model=Report)
  async def get_regional_rollup(region_id: str) -> Report:
      return service.generate_regional_rollup(region_id)
  ```
  No business logic in the route — it only calls the service and returns the result (Rule 4).
- `main.py`: import `router as reports_router` from `storeops.reports` (mirroring how
  `activities_router`/`programmes_router`/`alerts_router` are already imported), and add
  `app.include_router(reports_router)` alongside the existing three `include_router` calls. Leave
  the existing `reports_service.register_event_handlers(event_bus)` call where it already is
  (unchanged — it already runs regardless of whether the router is wired in).

## Acceptance criteria

- **AC1**: GIVEN a region with seeded stores and tasks, WHEN `GET /api/reports/region/{region_id}`
  is called via the test client, THEN it returns `200` with a body matching the `Report` shape
  (including `report_type == "REGIONAL_ROLLUP"`, `region == region_id`, populated `data` and
  `blocked_tasks`).
- **AC2**: GIVEN a region with no seeded stores, WHEN the same endpoint is called, THEN it returns
  the `AppError`-mapped JSON error response for `NotFoundError` (404), via the existing
  `app_error_handler` — not an unhandled 500.
- **AC3**: GIVEN the app is constructed, WHEN `main.py` is imported, THEN the `reports` router's
  routes appear in `app.routes` (a smoke-test assertion, e.g. checking `/api/reports/region/{...}`
  is a registered path) — confirming the wiring, not just that the route function exists in
  isolation.

## Non-goals

- No other `reports` routes are added (e.g. no `GET /api/reports/{report_id}` route, even though
  `service.get_report` already exists) — stay scoped to exactly the one endpoint requested.
- No auth/permission check added to the new route (consistent with every other current endpoint —
  `shared/deps.py`'s placeholder auth is unchanged, per `app-context.md`).
- No change to `generate_regional_rollup` itself — any bug found here that lives in the service
  method belongs to a sprint-3.2 fix, not new route-layer logic.

## Load-bearing architecture-principles.md rules

- **Rule 4** (layer separation) — the route must not embed any aggregation/business logic; it is
  a direct pass-through to `service.generate_regional_rollup`.
- **Rule 3** (error contract) — verify the existing `AppError` exception handler in `main.py`
  already covers this route without any route-local `try`/`except` needed.
