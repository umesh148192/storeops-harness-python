# Architecture Journal

This is a running record of design decisions, trade-offs, and lessons from building the StoreOps harness.

---

## Building the harness

The first challenge was giving all four agents the same understanding of StoreOps, while keeping their instructions focused.

**How skill files were split:**
- Shared files (read by everyone): `app-context.md`, `architecture-principles.md`
- Planner only: `sprint-decomposition.md`
- Generator only: `coding-conventions.md`, `how-to-test.md`
- Evaluator only: `how-to-review.md`, `grading-criteria.md`

**Why not one big shared file?**
- Every agent would have to read instructions it doesn't need.
- That goes against the bounded-context design.
- Each turn becomes less focused.

**On architecture rules:**
- Rules were kept very concrete on purpose.
- Instead of "follow clean architecture," the rules point to real checks like `uv run lint-imports`.
- The Evaluator shouldn't have to guess what a rule means or how to verify it.

---

## Sprint 1 — bulk shift-handover status update

This was the first full run through the harness loop.

**What came up:**
- `ActivityRepository.list` caused a `mypy` self-shadowing error.
- The method name `list` conflicted with the lowercase builtin in its return type.
- Fix was simple: use `typing.List` instead.
- Minor issue, but worth noting — it came up again later.

**The sprint passed cleanly.**

- Later, while preparing this submission, I re-ran the evaluation from scratch.
- I wanted to check that the Evaluator's earlier citations still held up.
- That re-check found a real but non-blocking gap: one test covered the audit entry only partly, not fully.

---

## Sprints 2.1 to 2.3 — SLA breach alerting

This feature was a good test of splitting multi-module work into separate sprints.

**Why order mattered:**
- `programmes` needed to provide read-only lookups first.
- Then `activities` could add the SLA evaluation logic.
- After that, `alerts` could add the notification behavior.

**Result:**
- All three sprints passed on the first Generator iteration.
- Because each dependency was built before the next sprint needed it, the Generator never had to guess what a later interface might look like.

---

## Sprints 3.1 to 3.3 — regional rollup report

This was the first feature that touched the `reports` module in a way that affected routing.

**Key detail:**
- Before this, the `reports` router was intentionally left out of `main.py`.
- That was a deliberate design choice, not an unfinished task.
- It only changed when sprint-3.3 explicitly asked for it.

**Lesson learned:**
- Some missing pieces in a codebase are intentional.
- The harness needs to know the difference between incomplete and deliberately left out.

**Other things that came up:**
- The Planner surfaced several scope decisions early in `spec.md` before approval. That was helpful — much cheaper to decide during planning than mid-iteration.
- A repeated testing mistake showed up: using a fresh `EventBus()` in tests instead of the shared `event_bus` singleton.
- It was caught before Evaluator review and logged in `run-log.md` as a repeat-risk pattern.
- It happened twice overall — not enough to trigger a mandatory skill-file update.

---

## Sprints 4.1 to 4.2 — planogram task template

This was the clearest example of the Evaluator changing the design, not just the score.

**What happened in the first attempt:**
- `programmes.service` called `activities.service.create_activity` directly.
- That was the easy way to return newly created tasks in the HTTP response.
- But it created a direct cross-module write, which broke the architecture rule.

**What the Evaluator did:**
- Marked the item as AMBIGUOUS instead of approving it.
- That forced a better solution instead of letting the shortcut through.

**What the final design looked like:**
- Sent the request through `event_bus`.
- A new subscriber in `activities.service` performed the write.
- The result was read back through a permitted read path.

**The takeaway:**
- The harness didn't relax the rule because the shortcut was convenient.
- The implementation changed to fit the rule — not the other way around.

---

## Retrospective

Writing `DESIGN_BRIEF.md` after the build helped surface two gaps worth noting.

**Gap 1 — The Monitor can spot trends, but it doesn't force action.**
- Two different issues each appeared twice across the run.
- The threshold for mandatory action is three repeats.
- The system can highlight patterns, but someone still has to read `run-log.md` and act.

**Gap 2 — A test can pass while only checking part of a requirement.**
- Re-checking sprint-1 for this submission showed exactly that.
- The implementation was correct, but one test only covered part of the audit-entry contract.
- Keeping this as a real example for future skill-file updates makes sense.
