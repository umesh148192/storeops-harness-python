# .harness/output/

Handoff files between harness agents for the run **currently in progress**. Empty until a
`@planner` run starts (see root `CLAUDE.md`). Not archival — `.harness/reviews/run-log.md` is the
permanent record; these files reflect only the current/most recent sprint.

| File | Written by | Read by |
|---|---|---|
| `spec.md` | Planner | developer (approval gate), orchestrator |
| `sprint-N-contract.md` | Planner | Generator, Evaluator |
| `generator-summary.md` | Generator | Evaluator, Monitor |
| `evaluator-feedback.md` | Evaluator | orchestrator (routing), Generator (on retry), Monitor |
| `escalation.md` | orchestrator | developer |

`escalation.md` only appears if a sprint hits the 3-iteration cap while still failing — format:
sprint ID, iteration count, and the specific blocking hard-gate/checklist item copied from the
final `evaluator-feedback.md`. See root `CLAUDE.md` for the full routing logic that produces it.
