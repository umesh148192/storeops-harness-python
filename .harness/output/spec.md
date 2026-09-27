STATUS: AWAITING APPROVAL

**sprint-1** — (bulk shift-handover status update) is already complete from a prior run — not part of this feature. This feature — "Add SLA breach alerting" — spans three modules, so it is split into three sub-sprints under sprint-2, ordered by dependency (a module other sub-sprints read from is built first, per Rule 1):

**sprint-2.1** — `programmes`: add read-only service lookups that resolve a programme's Department Lead(s) and Store Manager(s) from existing project membership, so the alerting sub-sprints have a way to find the right recipient.

**sprint-2.2** — `activities`: add a `due_date` field to tasks and a configurable-grace-period SLA evaluation that detects HIGH/CRITICAL tasks past due and not DONE, emitting a first-breach event and a separate escalation event once the grace period elapses, without duplicate-firing on repeated checks.

**sprint-2.3** — `alerts`: subscribe to the new escalation event (and update the existing breach handler) to notify the resolved Department Lead on first breach and the resolved Store Manager on escalation, via the event bus only — using sprint-2.1's lookups.

Note on scheduling: this codebase has no background job runner or cron infrastructure (in-memory storage, single Beanstalk instance — see `app-context.md`). Sprint-2.2 exposes the SLA evaluation as an explicit, idempotent service method reachable via an endpoint intended to be invoked periodically by an external scheduler (e.g. a scheduled CloudWatch/EventBridge call), not by adding a new in-process scheduler dependency, which would be new infrastructure outside this feature's scope.

Note on recipient resolution: "Department Lead" and "Store Manager" are only resolvable today via `programmes` project membership roles (`ProjectRole.DEPARTMENT_LEAD` / `ProjectRole.STORE_MANAGER`). Tasks without a `programme_id`, or programmes without a member in the relevant role, fall back to notifying the task's `assignee_id` for the initial breach and do not escalate — this is called out as an explicit non-goal in sprint-2.3's contract rather than inventing a new store-wide role directory.
