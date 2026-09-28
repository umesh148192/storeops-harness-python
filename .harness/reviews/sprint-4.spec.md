STATUS: AWAITING APPROVAL

Feature: **"Add planogram task template"** — `POST /api/programmes/{project_id}/templates` clones a
standard, fixed set of `PLANOGRAM` tasks into a new (or existing) store programme, applying a
department assignment and a default priority to each cloned task from the template definition. Two
sprints, ordered by dependency (a module other sprints depend on is built first, per Rule 1):

**sprint-4.1** — `activities`: add a `department: str | None` field to `Task`/`TaskCreate`/
`TaskUpdate`. This does not exist anywhere in the codebase today (no `Department` entity, only the
`DEPARTMENT_LEAD` staff *role*) and is the prerequisite the template-cloning sprint needs to stamp
a department onto each cloned task.

**sprint-4.2** — `programmes`: add a fixed `PLANOGRAM` task template definition and the
`POST /api/programmes/{project_id}/templates` route/service method that clones it into the target
programme's tasks via `activities.service.create_activity`, applying each template item's
department and priority.

## Decisions flagged for review before approval

1. **New `department` field, not a new `Department` module.** The request says "applying
   department assignments," but nothing in the codebase models a department as a first-class
   entity — `StaffRole.DEPARTMENT_LEAD` is a role, not a department name/id. Sprint-4.1 adds a
   free-form `department: str | None = None` to `Task` (and the create/update schemas), the same
   minimal-scope pattern used for `due_date` in the earlier SLA feature, rather than inventing a
   `Department` domain module with its own routes/repository — that is far more than this request
   asks for.
2. **The template definition is a fixed, hardcoded list, not a manageable resource.** The request
   asks to clone "a standard set" of tasks — it does not ask for a way to create/edit/list
   templates via the API. Sprint-4.2 defines the standard `PLANOGRAM` task set (title, department,
   priority per item) as a constant inside `programmes/service.py`. No new repository storage, no
   template CRUD endpoints, no persistence of the template itself — only the *cloning* is exposed.
3. **Cloning is additive, not idempotent.** Calling the endpoint twice for the same programme
   produces two independent full sets of cloned tasks (distinct ids each time). The request does
   not ask for de-duplication or "only clone if not already applied," so no such guard is added —
   called out explicitly so it isn't mistaken for an oversight.
4. **First direct `programmes` → `activities.service` *write* call.** Every existing cross-module
   service call in the codebase today is either a read (e.g. `activities/service.py` calling
   `programmes_service.get_programme`) or a side effect fired through the event bus (Rule 2). This
   feature is neither: the endpoint must synchronously return the newly created `Task` records in
   its response, which the fire-and-forget event bus (`EventBus.emit` returns nothing) cannot do.
   Sprint-4.2 therefore has `programmes/service.py` call `activities.service.create_activity(...)`
   directly for each template item. This is structurally permitted — the import-linter "no
   direct side-effect imports" contract only forbids `activities`/`programmes` importing
   `alerts.service`/`reports.service`, not each other — and Rule 1 (module boundary) is satisfied
   because it's a service-to-service call, never `activities.repository`. Flagging this because
   it's a new direction of direct write call that hasn't occurred before in this codebase, so the
   Evaluator should confirm it reads as intentional, not a boundary violation.
5. **Response shape reuses the existing `Task` schema.** `POST /api/programmes/{project_id}/templates`
   returns `list[Task]` (imported from `activities.types`, the same cross-module type-import
   pattern `reports/types.py` already uses for `Report.blocked_tasks: list[Task]`) — no new
   wrapper/response type is introduced for this sprint.
