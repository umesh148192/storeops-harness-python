# DEPLOYMENT.md

## Deployment target **Local**

- The repository ships a `Dockerfile` and `docker-compose.yml` for containerized local deployment
(`docker compose up --build`, exposing port 8000). 
- This demonstration was run in a local environment which does not have the Docker CLI/daemon installed. 
Hence, the app was run directly as a local process with the same entry point the container image uses 
(`uvicorn storeops.main:app`), against the same in-memory app on the same port. 
- The steps below cover both: what was actually run for this demonstration, and the equivalent Docker 
command for an environment where Docker is available.

## Steps taken (this demonstration)

1. Installed/synced dependencies via `uv`:
   ```
   uv sync
   ```
2. Ran the local check suite to confirm the build is healthy before deploying. See 
.harness/reviews/sprint-*-evaluator-feedback.md for full output — all green.
   ```
   uv run python -m mypy src, 
   uv run python pylint src, 
   uv run python -c "from importlinter.cli import lint_imports; raise SystemExit(lint_imports())", 
   uv run python -m pytest,
   uv run python scripts/check_coverage.py
   ```

3. Started the app the same way the container's `CMD` does:
   ```
   uv run uvicorn storeops.main:app --host 0.0.0.0 --port 8000
   ```
   Startup log:
   ```
   INFO:     Started server process [20724]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```
4. Confirmed the container's own health check target responds:
   ```
   GET http://localhost:8000/health → { "status": "ok" }
   ```

## Equivalent Docker command (for an environment with Docker installed)

```
docker compose up --build
```

This builds from the repo's `Dockerfile` (Python 3.14-slim, `uv sync --frozen`, non-root
`appuser`, `HEALTHCHECK` against `/health`) and publishes the same port mapping
(`8000:8000`) declared in `docker-compose.yml` — no code or configuration difference from the
direct-process run above; the app entrypoint (`uvicorn storeops.main:app`) is identical.

## Evidence: the new endpoint responding in the running application

**URL**: `http://localhost:8000/docs` — the running app's interactive OpenAPI/Swagger UI, listing
`PATCH /api/activities/bulk-status` under the `activities` tag.

**Live transcript** (captured against the running local server started in step 3 above):

Created two tasks, then called the sprint-1 feature endpoint with a mixed valid/invalid batch —
this exercises AC1 (single-request batch), AC2 (partial failure doesn't abort the batch), and the
`NOT_FOUND` per-item failure shape from AC2/AC4 in one call:

```
POST /api/activities   {"title":"Restock dairy aisle","assignee_id":"stub-user-1"}
POST /api/activities   {"title":"Audit shelf labels","assignee_id":"stub-user-1"}

Task1=ce3288c1-9b70-4eed-b0f0-8ad2523fb897 Task2=0b708a2f-a7f1-4427-a782-b08db50600e2

PATCH /api/activities/bulk-status
{
  "updates": [
    { "task_id": "ce3288c1-...", "status": "DONE",    "note": "Handover complete" },
    { "task_id": "0b708a2f-...", "status": "BLOCKED", "note": "Waiting on new labels" },
    { "task_id": "does-not-exist", "status": "DONE",  "note": "Should fail" }
  ]
}

→ 200 OK
{
    "updated":  [
        { "id": "ce3288c1-...", "title": "Restock dairy aisle",  "status": "DONE",    "assignee_id": "stub-user-1", ... },
        { "id": "0b708a2f-...", "title": "Audit shelf labels",   "status": "BLOCKED", "assignee_id": "stub-user-1", ... }
    ],
    "failed":  [
        { "task_id": "does-not-exist", "code": "NOT_FOUND", "message": "Activity does-not-exist not found" }
    ]
}
```

This confirms, against the live running application (not just the test suite): both valid updates
applied in one request, the invalid item failed independently without aborting the batch, and the
response shape matches `BulkStatusUpdateResponse` (`updated`/`failed`) exactly as specified in
`.harness/reviews/sprint-1-contract.md`.
