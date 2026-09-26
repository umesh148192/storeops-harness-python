# StoreOps Agentic Harness — Orchestrator

This file is the root orchestrator for the StoreOps development harness. It defines how a harness
run is driven — the agent-specific "how" lives in `.harness/agents/*.agent.md` and `.harness/skills/*.md`.

## Starting a run

The developer has only two active steps in a run:

1. **Invoke the Planner** with a single prompt naming the feature:
   `@planner Add shift handover bulk update to tasks`
2. **Review `.harness/output/spec.md`** (it will have `STATUS: AWAITING APPROVAL` at the top,
   listing the sprint breakdown) and reply `APPROVED`.

Everything after `APPROVED` runs autonomously. The developer is not asked to trigger each
Generator/Evaluator iteration — they re-enter only at an escalation (see below).

## Agents

Four agents, defined in `.harness/agents/` → 1. `planner.agent.md` 2. `generator.agent.md`
3. `evaluator.agent.md` and 4. `monitor.agent.md`. 
Each names its own required reading (from `.harness/skills/`) and its handoff file(s) — read the agent file itself before acting as that agent, do not act from this summary alone.

**Invocation model**: Each agent turn as the Planner call, and every Generator/Evaluator iteration
of every sprint — is driven as its own bounded turn that reads only that agent's `.agent.md`, its
named skill files, and the specific handoff file(s) named below. It does not carry forward the
full conversation history of prior sprints. See "Context scoping" below for why.

## The loop, per sprint (after APPROVED)

For each `sprint-N-contract.md` produced by the Planner, in order:

1. **Generator** implements the sprint (reads the contract, and on a retry, the prior
   `evaluator-feedback.md`). Produces code + tests + `generator-summary.md`.
2. **Evaluator** reviews the Generator's output independently. Produces `evaluator-feedback.md`
   with a verdict: **PASS**, **CONDITIONAL PASS**, or **FAIL** (full grading logic:
   `.harness/skills/grading-criteria.md`).
3. **Routing on the verdict**:
   - **PASS** → run the Monitor (writes `run-log.md`), then advance to the next sprint contract.
   - **CONDITIONAL PASS** → run the Monitor (records the specific follow-up item(s) in
     `run-log.md`'s quality-trend notes), then advance — non-blocking.
   - **FAIL** → increment this sprint's iteration count. If iteration count < 3, send
     `evaluator-feedback.md` back to a fresh Generator turn (step 1 again, same sprint). If
     iteration count has reached 3 and the verdict is still FAIL, **escalate** (below) instead of
     retrying again.
4. When every sprint contract has reached PASS or CONDITIONAL PASS, the run is done — report
   completion to the developer.

## Escalation

Triggered only by a 3rd consecutive FAIL on the same sprint. The orchestrator writes
`.harness/output/escalation.md` naming: the sprint ID, the iteration count (3), and the specific
blocking hard-gate or checklist item copied from the final `evaluator-feedback.md` (not a
paraphrase — copy the cited evidence). Then stop and hand control back to the developer; do not
attempt a 4th Generator iteration automatically.

## Context scoping

Long runs (many sprints, each with up to 3 iterations) would otherwise accumulate unbounded
conversation history and degrade quality over the run. To prevent that:

- Every Generator and Evaluator turn starts fresh, reading only what its `.agent.md` names as
  required reading plus the current sprint's handoff files — never the transcript of previous
  sprints or previous iterations of the same sprint beyond the one `evaluator-feedback.md` a retry
  needs.
- The orchestrator (this file, running in the main session) stays lightweight: it tracks which
  sprint is active and the iteration count, and reads verdicts to route — it does not itself hold
  the full code diff or review detail in its own context across many sprints. That detail lives in
  the handoff files on disk, not in orchestrator memory.
- `.harness/output/` holds only the current/most-recent sprint's handoff files (see its `README.md`)
  — `.harness/reviews/run-log.md` is the durable record, so nothing needs to be kept in context to
  preserve history.

## Relationship to CI/CD

The Evaluator's automated checks (`mypy src`, `pylint src`, `lint-imports`, `pytest`,
`scripts/check_coverage.py` — see `.harness/skills/how-to-review.md`) are the **same commands**
already run by `.github/workflows/deploy.yml`'s `test` job. The harness **precedes** CI, it does
not replace or bypass it: a sprint that reaches PASS in the harness is expected to pass CI
trivially, because CI is re-running identical checks as a safety net against harness or human
error (e.g. someone hand-editing code after a PASS, or a harness run being interrupted) — not as a
second, different gate the Generator wasn't already held to.
