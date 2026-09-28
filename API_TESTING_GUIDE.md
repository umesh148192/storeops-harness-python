# StoreOps API Testing Guide

Manual end-to-end test sequence for the running dev server. Data created in
earlier steps is reused by later steps, so run them **in order, top to
bottom** in a single PowerShell session.

## Prerequisites

Start the dev server:

```powershell
uv run uvicorn storeops.main:app --reload
```

- Server runs at `http://127.0.0.1:8000`. 
- Interactive Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Notes on how this app behaves

- **Auth is stubbed.** Every request is treated as `user_id=stub-user-1`,
  `store_id=store-1`, role `STORE_MANAGER` — no token/header needed
  ([deps.py](src/storeops/shared/deps.py)).
- **Only one seed user exists** (`stub-user-1`,
  [staff/repository.py](src/storeops/staff/repository.py)), so it's reused for
  every "add member" role in this walkthrough.
- **Alerts and Reports have no write endpoints.** They're populated as side
  effects of activity/programme events, so the sequence triggers those events
  first, then reads the results.
- **No Staff API is registered yet** — `staff` has a service/repository but no
  router wired into [main.py](src/storeops/main.py), so there's nothing to
  call there directly.
- **State is in-memory** and resets whenever the `--reload` server restarts
  (e.g. after a code change). If that happens, rerun the sequence from Step 2.

## Test sequence

```powershell
$base = "http://127.0.0.1:8000"

# 1. Health check
Invoke-RestMethod "$base/health"

# 2. Create a programme (store_id is fixed to "store-1" via the stub user)
$programme = Invoke-RestMethod -Method Post "$base/api/programmes" `
  -ContentType "application/json" `
  -Body (@{ name = "Q4 Store Refresh"; description = "Store refresh programme" } | ConvertTo-Json)
$programme
$projectId = $programme.id

# 3. Add the seeded user as DEPARTMENT_LEAD and STORE_MANAGER (needed later for alert routing)
Invoke-RestMethod -Method Post "$base/api/programmes/$projectId/members" `
  -ContentType "application/json" `
  -Body (@{ user_id = "stub-user-1"; role = "DEPARTMENT_LEAD" } | ConvertTo-Json)

Invoke-RestMethod -Method Post "$base/api/programmes/$projectId/members" `
  -ContentType "application/json" `
  -Body (@{ user_id = "stub-user-1"; role = "STORE_MANAGER" } | ConvertTo-Json)

# 4. List programmes for the stub store
Invoke-RestMethod "$base/api/programmes"

# 5. Clone the planogram template onto the programme -> creates 3 activities
$templateTasks = Invoke-RestMethod -Method Post "$base/api/programmes/$projectId/templates"
$templateTasks
$planogramTaskId = $templateTasks[0].id

# 6. List activities scoped to the programme
Invoke-RestMethod "$base/api/activities?programme_id=$projectId"

# 7. Create an additional activity manually: overdue, CRITICAL, assigned to the stub user
$activity = Invoke-RestMethod -Method Post "$base/api/activities" `
  -ContentType "application/json" `
  -Body (@{
      title        = "Emergency restock - dairy aisle"
      description  = "Fridge outage, needs immediate restock"
      priority     = "CRITICAL"
      category     = "RESTOCKING"
      programme_id = $projectId
      assignee_id  = "stub-user-1"
      due_date     = (Get-Date).ToUniversalTime().AddDays(-2).ToString("o")
      department   = "Grocery"
  } | ConvertTo-Json)
$activity
$taskId = $activity.id

# 8. Get the activity by id
Invoke-RestMethod "$base/api/activities/$taskId"

# 9. Update it to BLOCKED — status BLOCKED + priority CRITICAL fires an immediate SLA_BREACH alert to the assignee
Invoke-RestMethod -Method Patch "$base/api/activities/$taskId" `
  -ContentType "application/json" `
  -Body (@{ status = "BLOCKED" } | ConvertTo-Json)

# 10. Bulk-update status back to IN_PROGRESS (exercises the bulk endpoint, reusing $taskId)
Invoke-RestMethod -Method Patch "$base/api/activities/bulk-status" `
  -ContentType "application/json" `
  -Body (@{ updates = @(@{ task_id = $taskId; status = "IN_PROGRESS"; note = "Resuming after fridge repair" }) } | ConvertTo-Json -Depth 5)

# 11. Run the SLA sweep — task is CRITICAL, ~48h overdue, grace period 24h -> breach + escalation both fire,
#     routed to the DEPARTMENT_LEAD / STORE_MANAGER added in step 3 (both stub-user-1)
Invoke-RestMethod -Method Post "$base/api/activities/sla-check?grace_period_hours=24"

# 12. List alerts — expect 3 notifications: BLOCKED-update breach, sla-check breach, sla-check escalation
Invoke-RestMethod "$base/api/alerts"

# 13. Regional rollup report — aggregates every store in "North" (store-1 + store-2), reflecting the data above
Invoke-RestMethod "$base/api/reports/region/North"

# 14. Clean up: delete the manual activity, then confirm it's gone (expect 404)
Invoke-RestMethod -Method Delete "$base/api/activities/$taskId"
try { Invoke-RestMethod "$base/api/activities/$taskId" } catch { $_.Exception.Response.StatusCode }

# 15. Confirm the template-cloned activity still exists
Invoke-RestMethod "$base/api/activities/$planogramTaskId"
```

## What each step proves

| Step | API | Verifies |
|---|---|---|
| 1 | `GET /health` | app is up, no auth/deps |
| 2 | `POST /api/programmes` | create programme |
| 3 | `POST /api/programmes/{id}/members` | add member (x2 roles) |
| 4 | `GET /api/programmes` | list programmes |
| 5 | `POST /api/programmes/{id}/templates` | clone template → creates activities via event bus |
| 6, 8, 15 | `GET /api/activities`, `GET /api/activities/{id}` | list & get activity |
| 7 | `POST /api/activities` | create activity |
| 9 | `PATCH /api/activities/{id}` | update activity + triggers SLA_BREACH alert |
| 10 | `PATCH /api/activities/bulk-status` | bulk status update |
| 11 | `POST /api/activities/sla-check` | SLA sweep → breach + escalation events |
| 12 | `GET /api/alerts` | alerts populated by prior events |
| 13 | `GET /api/reports/region/{region}` | cross-module aggregation (programmes + activities) |
| 14 | `DELETE /api/activities/{id}` | delete activity + 404 confirmation |

## Troubleshooting

- **`ConvertFrom-Json`/404 errors on `/api/activities/{id}` after delete**:
  expected — `Invoke-RestMethod` throws on non-2xx, caught in the `try/catch`
  in step 14.
- **Empty alerts list in step 12**: confirm step 3 ran (department
  lead/store manager membership is required for `_resolve_department_lead`
  / `_resolve_store_manager` in [alerts/service.py](src/storeops/alerts/service.py)
  to find a recipient).
- **`404 Programme not found`**: server was restarted (via `--reload` picking
  up a file change) and in-memory state was cleared — rerun from Step 2.
