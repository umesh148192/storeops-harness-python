# Skill: How to Test

Generator-specific. Testing conventions already established under `tests/storeops/` — mirror them
for any new test.

## Layout

`tests/storeops/<module>/` mirrors `src/storeops/<module>/` exactly (e.g.
`tests/storeops/activities/test_service.py`). A new module gets a new mirrored directory; a new
file in an existing module gets a test file in the same relative position.

**Why `tests/storeops/` and not `tests/`**: it deliberately mirrors the package name, which
required setting `--import-mode=importlib` in `[tool.pytest.ini_options]` (`pyproject.toml`) and
dropping `__init__.py` from the test tree — otherwise pytest's default import resolution collides
with the real installed `storeops` package. Don't add `__init__.py` files back into `tests/`.

## Fixtures (`tests/storeops/conftest.py`)

- `client` fixture: a `TestClient(app)` with `get_current_user`/`get_current_store` overridden to a
  fixed `FAKE_USER_CONTEXT`/`FAKE_STORE` — use this for route-level tests, not the raw app.
- An **autouse** fixture resets every module's repository singleton before each test (calls
  `.reset()` on all of them) — this is why every repository needs a `reset()` method
  (`coding-conventions.md`). Don't hand-roll your own reset logic per test file.

## What to test per layer, per new endpoint/feature

- **`test_repository.py`**: CRUD roundtrip against a fresh `Repository()` instance (not the
  singleton) — create/get/update/delete, plus a miss case (`get` on an unknown id returns `None`).
- **`test_service.py`**: one test per acceptance criterion in the sprint contract, using the
  `service` singleton directly (no HTTP). Cover the `AppError` paths explicitly (e.g.
  `NotFoundError` on an unknown id) — this is what `grading-criteria.md`'s Correctness dimension
  checks the AC self-check table against.
- **`test_routes.py`**: one smoke test per endpoint (happy path, 200/201) via the `client` fixture,
  plus the one or two edge cases that exercise a non-trivial `AppError` (404, 403 placeholder
  checks) — not every possible input, that's `test_service.py`'s job.

## Coverage

Run `uv run pytest` (writes `.coverage`, enforces the 70% overall `--cov-fail-under` from
`pyproject.toml`), then `uv run python scripts/check_coverage.py` for the per-layer breakdown:
service ≥80%, routes ≥70%, shared ≥60%, overall ≥70%. Both must pass before a sprint is
Generator-complete.
