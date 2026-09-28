# Sprint 4.2 — programmes: POST /api/programmes/{project_id}/templates (planogram task template)

## Goal

Add a fixed "standard set" of `PLANOGRAM` task definitions and a
`POST /api/programmes/{project_id}/templates` endpoint that clones them into the target
programme's activities, applying each template item's department and default priority.

Depends on sprint-4.1 (`Task.department`) — do not attempt this sprint until sprint-4.1 has landed.

## Modules / layers touched

- `src/storeops/programmes/service.py` — add a module-level constant defining the standard
  `PLANOGRAM` task set (title, department, priority per item — at least 2 items, e.g. a "Front End"
  item and a "Grocery" item, with different priorities, so tests can assert per-item mapping, not
  just count) and a new `clone_planogram_template(project_id: str) -> list[Task]` method.
- `src/storeops/programmes/routes.py` — add the route; thin pass-through only (Rule 4).
- Tests: `tests/storeops/programmes/test_service.py` and `tests/storeops/programmes/test_routes.py`
  — check current contents first, add cases.

## Design

- `clone_planogram_template`:
  1. `self.get_programme(project_id)` — reuses the existing lookup, raises `NotFoundError` if the
     programme doesn't exist (Rule 3 — no raw exception).
  2. For each item in the fixed template list, build a `TaskCreate` (imported from
     `storeops.activities.types`) with `category=TaskCategory.PLANOGRAM`,
     `programme_id=project_id`, `department=<item.department>`, `priority=<item.priority>`, and the
     item's `title`/`description`.
  3. Call `activities_service.create_activity(task_create)` (imported as
     `from storeops.activities.service import service as activities_service`, mirroring the
     existing `activities/service.py` → `programmes.service` import direction already used for
     reads) for each item and collect the returned `Task` objects.
  4. Return the list of created `Task`s in template order.
- `routes.py`:
  ```python
  @router.post("/{project_id}/templates", response_model=list[Task], status_code=201)
  async def clone_template(project_id: str) -> list[Task]:
      return service.clone_planogram_template(project_id)
  ```
  Import `Task` from `storeops.activities.types` (same cross-module type-import pattern already
  used by `reports/types.py` for `Report.blocked_tasks: list[Task]`). No request body — the
  template is fixed server-side (see spec.md decision #2).
- No new type is added to `programmes/types.py` for the template definition itself unless keeping
  it purely in `service.py` becomes unwieldy — if it does, a small internal (non-exported)
  structure is fine, but it must not appear in `programmes/routes.py`'s public request/response
  surface.

## Acceptance criteria

- **AC1**: GIVEN an existing programme with no tasks, WHEN
  `POST /api/programmes/{project_id}/templates` is called, THEN it returns `201` with a list of
  newly created `Task`s, one per template item, each with `category == PLANOGRAM` and
  `programme_id == project_id`.
- **AC2**: GIVEN the fixed template defines specific `department`/`priority` values per item, WHEN
  the endpoint is called, THEN each created `Task`'s `department` and `priority` match the
  corresponding template item exactly (asserted per item, not just as a count) — proving the
  mapping is applied, not defaulted.
- **AC3**: GIVEN a `project_id` that does not exist, WHEN the endpoint is called, THEN it returns
  the `AppError`-mapped `404` response for `NotFoundError`, and no `Task`s are created as a
  side effect (verify via `GET /api/activities` or the repository directly).
- **AC4**: GIVEN the endpoint is called twice in succession for the same programme, WHEN both
  calls succeed, THEN two independent full sets of cloned tasks exist afterward (distinct `id`s),
  confirming cloning is additive and not deduplicated (see non-goals).

## Non-goals

- No request body / customizable template — the set of tasks cloned is fixed for this sprint; a
  future sprint could add template selection or overrides, not this one.
- No de-duplication or idempotency guard preventing the same programme from being templated twice.
- No new `Department` entity, no template persistence/CRUD endpoints, no event-bus emission for
  "template cloned" (not requested).
- No change to `activities.service.create_activity` itself — if a bug is found there, it belongs
  to a sprint-4.1 fix, not new logic added here.

## Load-bearing architecture-principles.md rules

- **Rule 1** (module boundary) — `programmes/service.py` must call
  `activities.service.create_activity`, never import or touch `activities.repository` (already
  structurally blocked by the "No cross-module import of activities.repository" import-linter
  contract, but confirm the semantic intent holds too).
- **Rule 2** (event bus) nuance — this is the first sprint where `programmes` directly calls
  `activities.service` to perform a *write* (not a read, and not a side-effect notification via
  the event bus). See spec.md decision #4 for why this is the correct approach here (the response
  must synchronously return the created tasks) and confirm it does not read as a Rule 2 violation.
- **Rule 3** (error contract) — missing programme raises `NotFoundError` via the existing
  `get_programme` helper; no bare `raise` of any kind.
- **Rule 4** (layer separation) — `programmes/routes.py`'s new route is a direct pass-through to
  `service.clone_planogram_template`; no template-construction or field-mapping logic in the route.
