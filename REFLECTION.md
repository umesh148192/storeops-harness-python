# REFLECTION.md

## What the harness did well

**Clear roles made reviews more honest.**
- The Evaluator always starts fresh.
- It sees the sprint contract, the Generator summary, and the code changes — but not the Generator's full reasoning.
- That helps it catch issues a self-review might miss.

A good example was sprint-4.2.
- The first version had `programmes.service` calling `activities.service.create_activity` directly.
- That broke the rule: cross-module side effects must go through the event bus.
- The Evaluator marked it AMBIGUOUS instead of letting it pass.
- That forced a better design — using the event bus and reading the result back through a permitted path.

When I re-ran the evaluation for this submission:
- The same pattern held.
- Every claim in `evaluator-feedback.md` was backed by a file reference or real command output.
- Nothing was just repeating what the Generator said.

**Hard checks kept the process consistent.**
- `lint-imports`, `pytest`, and `check_coverage.py` give clear pass or fail results.
- A sprint can't get a PASS just because the review sounds convincing.
- If a contract is broken or a test fails, the sprint fails — no exceptions.
- This also makes escalation more trustworthy. After 3 FAILs, control goes back to the developer for a real decision.

---

## Where it fell short

**The Monitor still depends on someone checking the log.**
- The harness did record repeated issues across sprints.
- For example: the `ActivityRepository.list` mypy self-shadowing problem from sprint-1, and the shared-`event_bus` vs local-`EventBus()` mistake in sprint-3.2.
- But the skill files were never updated.
- The reason: the trend rule only triggers after the same issue appears 3 times. Both issues only appeared twice.
- So the system can spot patterns — but it still needs a person to read `run-log.md` and turn those notes into better guidance.

**Some tests prove part of a requirement, not all of it.**
- I noticed this when re-reviewing sprint-1 for this submission.
- The test `test_bulk_update_status_updates_valid_tasks_and_records_audit_entries` covers AC3 — but only partly.
- It checks that audit records are created for changed tasks and not for rejected ones.
- But it only checks the `new_status` field.
- AC3 also mentions `actor_id`, `previous_status`, `note`, and `updated_at`.
- The implementation is correct, but the test doesn't fully prove the whole requirement.
- A future bug in one of those other fields could slip through undetected.

---

## One concrete improvement

I'd add one rule to `how-to-review.md`:

- If an acceptance criterion lists several specific fields or outcomes, the Evaluator should check whether the cited test covers **all** of them — not just one.
- If the test only covers some of the required fields, the item should be marked **AMBIGUOUS** instead of PASS.
- This would make partial test coverage visible in the next iteration.
- No new verdict type needed. No changes to `grading-criteria.md` scoring rules.
