# Generator Summary — sprint-3.3

## Sprint
sprint-3.3 — `reports` route: `GET /api/reports/region/{region_id}` calling sprint-3.2's `generate_regional_rollup`, and wiring the `reports` router into `main.py` for the first time.

## AC self-check

| AC | Description | Test | Result |
|----|---|---|---|
| AC1 | `GET /api/reports/region/{region_id}` returns 200 with the `Report` shape for a region with stores/tasks | `test_get_regional_rollup_returns_200_with_report_shape` | PASS |
| AC2 | Region with no seeded stores returns the `AppError`-mapped 404 JSON, not an unhandled 500 | `test_get_regional_rollup_missing_region_returns_404_app_error_json` | PASS |
| AC3 | The `reports` router's routes are registered in the app after wiring | `test_reports_router_is_wired_into_app` | PASS |

## Files changed

- **Routes**: `src/storeops/reports/routes.py` — added `GET /region/{region_id}` calling `service.generate_regional_rollup(region_id)` directly, no business logic in the route (Rule 4); removed the stale "not wired in" comment since this sprint explicitly wires it in.
- **Main**: `src/storeops/main.py` — imported `router as reports_router` from `storeops.reports` (same pattern as the other three routers) and added `app.include_router(reports_router)`; left the pre-existing `reports_service.register_event_handlers(event_bus)` call untouched (it already ran regardless of router wiring).
- **Tests**: `tests/storeops/reports/test_routes.py` (new file — none existed before, since the router had no routes) — 3 tests covering AC1-AC3, using the existing `client` fixture from `conftest.py`.

## Known gaps

None functionally — all 3 ACs are covered by citable tests. One self-caught test-authoring issue: the initial AC3 smoke test read `route.path` off every entry in `app.routes`, which raised `AttributeError` because this FastAPI/Starlette version wraps included routers in an object without a `.path` attribute; fixed by asserting against `app.openapi()["paths"]` instead, which is the stable, documented way to confirm a path is registered.

## Local check results (run before handoff)

- `uv run mypy src` — Success, no issues found in 33 source files.
- `uv run pylint src` — 10.00/10.
- `uv run lint-imports` — 7 contracts kept, 0 broken.
- `uv run pytest` — 90 passed.
- `uv run python scripts/check_coverage.py` — service 95.1% (≥80%), routes 100% (≥70%, `reports/routes.py` itself at 100%), shared 97.3% (≥60%), overall 97.8% (≥70%).