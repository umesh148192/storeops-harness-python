# Skill: Sprint Decomposition

Planner-specific. How to break a developer's feature request into sprints.

## Sizing a sprint

Use StoreOps' own existing scale as the precedent: the 9 live endpoints across `activities` (5),
`programmes` (3), `alerts` (1) were each shipped as an independently testable unit. A sprint should
be similarly sized:

- **One sprint per new endpoint** (route + service method + repository method + types, plus tests)
  is the default unit.
- **One sprint per cross-cutting change** that touches one module's internals without adding a
  route (e.g. "add an `overdue` computed field to `Task`") — still gets its own sprint so the
  Evaluator can review it in isolation.
- A feature that spans multiple modules (e.g. "notify staff when a programme closes") becomes
  multiple sprints: one per module touched, ordered so a module that others read from (per Rule 1)
  is built before the modules that read it. `reports`' read-only aggregation of `activities`/
  `programmes`/`staff` means reports-side sprints go last.
- If a sprint contract would touch more than ~3 files outside tests, split it — the Generator
  and Evaluator both work better on a small, reviewable diff, and `generator-summary.md`'s
  AC self-check table stops being trustworthy past that size.

## Writing sprint-N-contract.md

Each sprint contract needs:
- **Sprint ID** (`sprint-1`, `sprint-2`, ...) and a one-line goal.
- **Module(s) touched** and which layer(s) — this feeds the Evaluator's layer-separation check.
- **Acceptance criteria in GIVEN/WHEN/THEN form**, each one independently testable. Every AC must
  be phrased so a single test function could assert it — avoid ACs like "the feature works
  correctly," which the Generator's AC self-check table can't honestly map to a test.
- **Explicit non-goals** — what this sprint does NOT do, so the Generator doesn't scope-creep into
  the next sprint (scope creep without disclosure is a Process Integrity hard gate — see
  `grading-criteria.md`).
- Cross-reference which architecture-principles.md rules are load-bearing for this sprint (e.g. a
  sprint adding an alert on task deletion should call out Rule 2 explicitly).

## spec.md

`spec.md` is the developer-facing summary: the full sprint list in order, each with its one-line
goal, and the `STATUS: AWAITING APPROVAL` marker at the top. The developer reviews this file (not
each `sprint-N-contract.md`) before typing `APPROVED`.
