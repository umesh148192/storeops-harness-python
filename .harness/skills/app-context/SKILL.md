# Skill: App Context

Shared foundation — every agent (Planner, Generator, Evaluator, Monitor) reads this first.

## What StoreOps is

A retail store operations REST API. Domain: activities (tasks), programmes (seasonal/compliance
initiatives), staff, alerts (notifications), reports (aggregated metrics).

## Current state (check this file, not memory, before planning new work)

- **Stack**: Python 3.14+, FastAPI, Pydantic v2, `uv`-managed deps, in-memory storage only (no
  database — every repository is a module-level singleton holding a dict).
- **5 modules**, each `src/storeops/<module>/{routes,service,repository,types}.py`:
  `activities`, `programmes`, `staff`, `alerts`, `reports`.
- **9 live REST endpoints** (activities ×5, programmes ×3, alerts ×1) wired into `main.py`. `staff`
  and `reports` have full Routes→Service→Repository scaffolding but their routers are **not**
  included in the app — `staff` because authentication is out of scope, `reports` because its
  endpoints are a deferred demonstration feature. Don't "fix" this by wiring them in unless a sprint
  contract explicitly asks for it.
- **Auth is a placeholder**: `shared/deps.py`'s `get_current_user`/`get_current_store` return a
  hardcoded `UserContext`/`Store`. There is no real login flow. Treat this as intentional, not a bug.
- **`GET /health`** exists on the bare app (`main.py`), outside the Section#3 API surface — a
  liveness probe for deployment, not a domain endpoint.
- **Deployment target**: AWS Elastic Beanstalk (Docker platform), single instance — see
  `terraform/` and `Dockerrun.aws.json`. In-memory storage means the app cannot scale to more than
  one instance without a real datastore; don't propose auto-scaling in a sprint contract.
- **CI**: `.github/workflows/deploy.yml` runs `mypy`, `pylint`, `import-linter`, `python -m pytest`, and the
  per-layer coverage script on every push; deploys to Beanstalk on `main` if `AWS_DEPLOY_ROLE_ARN`
  is configured.

## Before planning or generating anything

Re-read `src/storeops/<module>/` for the module(s) a feature touches — this file gives orientation,
not a substitute for reading the current code.
