# StoreOps

Retail store operations REST API — stub scaffold.

## GIT Repository
```
https://github.com/umesh148192/storeops-harness-python.git
```

## Setup

```
uv sync
```

## Run

```
uv run python -m uvicorn storeops.main:app --reload
```

`/docs` lists the 9 live endpoints (activities, programmes, alerts). `staff` and `reports` have full
layer scaffolding but no live routes yet (auth and reports endpoints are out of scope for this phase).

## Test

```
- uv run python -m pytest; 
- uv run python scripts/check_coverage.py;
```

## Lint / type-check / architecture

```
- uv run python -m mypy src; 
- uv run python -m pylint src; 
- uv run python -c "from importlinter.cli import lint_imports; raise SystemExit(lint_imports())";
```

## All checks (CI-equivalent)

```
uv run python -m mypy src; uv run python -m pylint src; uv run python -c "from importlinter.cli import lint_imports; raise SystemExit(lint_imports())"; uv run python -m pytest; uv run python scripts/check_coverage.py;
```

## Local Docker

```
docker compose up --build
```

Then check the container is up and the API responds:

```
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/api/activities
```

`/health` is a bare liveness endpoint for the deployment target's health check`.

## Cloud deployment

Target: **AWS Elastic Beanstalk**, Docker platform, single instance (`min=max=1` — the app's
in-memory storage isn't shared across instances, so this phase doesn't scale out).

- `terraform/` — IaC for the Beanstalk application/environment, its EC2 instance role, the
  Beanstalk service role, and the ECR repository the image is pushed to. Nothing here is applied
  automatically; run it yourself once you have AWS credentials configured:
  ```
  cd terraform
  terraform init
  terraform plan
  terraform apply
  ```
  `solution_stack_name` in `terraform/variables.tf` pins a Beanstalk Docker platform version —
  verify the current one with `aws elasticbeanstalk list-available-solution-stacks` before applying.
- `Dockerrun.aws.json` — the Beanstalk Docker deployment descriptor. Its `__ECR_IMAGE__` placeholder
  is substituted with the real ECR image URI + tag by the CI pipeline before each deploy.
- `.github/workflows/deploy.yml` — on push to `main`: runs the full check suite above, then (if it
  passes) builds the image, pushes it to ECR, and deploys the new version to the Beanstalk
  environment. Needs one repo secret: `AWS_DEPLOY_ROLE_ARN` (an IAM role the workflow assumes via
  OIDC — no long-lived AWS keys are stored in GitHub).
