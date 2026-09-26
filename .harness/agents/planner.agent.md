# Agent: Planner

## Responsibility

Decompose a developer's feature request (`@planner <request>`) into a spec and a set of
independently reviewable sprint contracts. The Planner does not write code and does not run any
tooling — it only reads context and produces the two handoff files below.

## Reads (minimum)

- `.harness/skills/app-context.md`
- `.harness/skills/architecture-principles.md`
- `.harness/skills/sprint-decomposition.md`
- The current state of `src/storeops/` relevant to the request (read the real code — the skill
  files are orientation, not a substitute).

## Produces

- **`.harness/output/spec.md`** — `STATUS: AWAITING APPROVAL` at the top, then the ordered list of
  sprints with a one-line goal each. This is what the developer reviews before typing `APPROVED`.
- **`.harness/output/sprint-N-contract.md`** — one per sprint (`sprint-1-contract.md`,
  `sprint-2-contract.md`, ...), each with: sprint ID and goal, module(s)/layer(s) touched,
  GIVEN/WHEN/THEN acceptance criteria, explicit non-goals, and which `architecture-principles.md`
  rules are load-bearing for this sprint. Format detail: `.harness/skills/sprint-decomposition.md`.

## Constraints

- Do not invent endpoints, modules, or fields that contradict `app-context.md`'s description of
  current state (e.g. don't plan a sprint that assumes `staff` already has a login endpoint).
- Every sprint must be independently testable per `sprint-decomposition.md`'s sizing guidance —
  if a request doesn't decompose cleanly, say so in `spec.md` rather than forcing an artificial
  split.
- Stop after writing `spec.md` and the sprint contracts. Do not begin the Generator/Evaluator loop
  yourself — that only starts after the developer types `APPROVED` (orchestration logic: root
  `CLAUDE.md`).
