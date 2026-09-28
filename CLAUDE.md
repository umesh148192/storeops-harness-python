# StoreOps Agentic Harness — Orchestrator

This is the main orchestrator for the StoreOps harness. It explains how a run works. The details for each agent live in `.harness/agents/*.agent.md`, and skill details are in `.harness/skills/*/SKILL.md`.

## How to start a run

As a developer, you only need to do two things:

1. **Call the Planner** with a short prompt that names the feature you want:
   `@planner Add shift handover bulk update to tasks`
2. **Open `.harness/output/spec.md`** — it will show `STATUS: AWAITING APPROVAL` at the top with the sprint plan. If it looks good, just reply `APPROVED`.

After you say `APPROVED`, everything runs on its own. You don't need to kick off each step — you only get pulled back in if something escalates (see below).

## The four agents

There are four agents, all defined in `.harness/agents/`:

1. planner.agent.md
2. generator.agent.md
3. evaluator.agent.md
4. monitor.agent.md

Each agent file tells it what to read and what files to hand off. Always read the agent's own file before acting as that agent — don't rely on this summary alone.

Each agent runs as its own fresh turn. It reads its `.agent.md`, the skill files it needs, and the current sprint's handoff files. It doesn't carry memory from previous sprints.

## What happens each sprint (after APPROVED)

After sprint is approved, this is what happens in order for each `sprint-N-contract.md` the planner created :

1. **Generator** 
   - Writes the code and tests for the sprint. 
   - If it's a retry, it also reads the previous `evaluator-feedback.md`. 
   - It produces code, tests, and a `generator-summary.md`.
2. **Evaluator** 
   - independently reviews the Generator's work and writes `evaluator-feedback.md` with one of three verdicts: **PASS**, **CONDITIONAL PASS**, or **FAIL**. 
   - Full grading rules are in `.harness/skills/grading-criteria/SKILL.md`.
3. **What happens next depends on the verdict**:
   - **PASS** → Monitor runs (writes `run-log.md`), then move on to the next sprint.
   - **CONDITIONAL PASS** → Monitor runs (notes the follow-up items in `run-log.md`), then move on. Not a blocker.
   - **FAIL** → Try again. If this sprint has failed fewer than 3 times, send the feedback back to a fresh Generator turn. If it has failed 3 times in a row, escalate instead of retrying.
4. Once all sprints reach PASS or CONDITIONAL PASS, the run is done and you'll get a completion report.

## Escalation
- Escalation happens when a sprint fails 3 times in a row. 
- When Escalation happens, the orchestrator writes `.harness/output/escalation.md` with the sprint ID, the iteration count (3), and the exact blocking item from the final `evaluator-feedback.md`. 
- Then it stops and hands things back to you. It won't try a 4th time automatically.

## Why each agent starts fresh

If agents carried the full conversation history across many sprints and retries, quality would drop over time. To avoid that:

- Each Generator and Evaluator turn reads only what its `.agent.md` says to read plus the current sprint's files. It never sees previous sprints or earlier iterations (except for the one `evaluator-feedback.md` it needs on a retry).
- The orchestrator itself stays lightweight — it just tracks which sprint is active and the iteration count, then routes based on verdicts. The actual code and review details stay in the handoff files on disk.
- `.harness/output/` only keeps the current sprint's files. The lasting record is in `.harness/reviews/run-log.md`.

## How this fits with CI/CD

The Evaluator runs the same checks that CI does — `mypy src`, `pylint src`, `lint-imports`, `pytest`, and `scripts/check_coverage.py` (see `.harness/skills/how-to-review/SKILL.md`). These are the exact same commands in `.github/workflows/deploy.yml`.

The harness runs *before* CI, not instead of it. If a sprint passes the harness, it should sail through CI too — because CI is just running the same checks again as a safety net. It catches things like someone editing code by hand after a PASS, or a harness run that got interrupted.
