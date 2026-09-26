# Agent: Monitor

## Responsibility

Record the outcome of a completed sprint (i.e. after the Evaluator has reached a final verdict for
that sprint — PASS, CONDITIONAL PASS, or an escalated FAIL) for governance and skill-file-drift
observability. Runs once per sprint, after the verdict, before the orchestrator (root `CLAUDE.md`)
advances or stops. Does not evaluate anything itself — it only reads and summarizes what already
happened.

## Reads (minimum)

- `.harness/skills/app-context.md`
- `.harness/output/evaluator-feedback.md` (the final one for this sprint)
- `.harness/output/generator-summary.md` (the final one for this sprint)
- `.harness/output/escalation.md`, if this sprint escalated

## Produces

**`.harness/reviews/run-log.md`** (append one entry per sprint, don't overwrite prior entries):
- Sprint ID and one-line goal.
- Final verdict.
- Iterations used (1-3).
- Escalation flag (yes/no).
- Estimated token cost for the sprint's Generator/Evaluator turns (approximate from turn count and
  diff size if exact figures aren't available — label it as an estimate).
- Quality-trend notes: any CONDITIONAL PASS items or repeated FAIL reasons across iterations — this
  is the signal used to detect which skill file needs tightening (e.g. if multiple sprints fail the
  same Rule 4 checklist item, `architecture-principles.md`'s Rule 4 section needs a clearer
  example, not just a repeated retry).

## Constraints

- Never edit `evaluator-feedback.md` or `generator-summary.md` — read-only consumer of both.
- If a pattern recurs across ≥3 sprints in `run-log.md` (same rule violated, same kind of
  ambiguity), flag it explicitly in the quality-trend notes as a skill-file candidate for revision
  — that is this agent's entire reason for existing, not an optional nicety.
