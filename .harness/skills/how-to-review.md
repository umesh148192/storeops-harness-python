# Skill: How to Review

Evaluator-specific. The review procedure — run this in order, every time, on every Generator
iteration. Pairs with `grading-criteria.md`, which defines how the results below convert into a
verdict.

## 1. Run the automated commands, in this order, and capture raw output

```
uv run mypy src
uv run pylint src
uv run lint-imports
uv run pytest
uv run python scripts/check_coverage.py
```

Stop and record a hard-gate FAIL immediately on the first of these that fails
(`grading-criteria.md` maps each to a specific dimension) — still run the rest for the feedback
file, since a Generator retry needs to see everything wrong at once, not one issue per iteration.

## 2. Grep-based checks

```
grep -rn "raise Exception" src/storeops
grep -rn "raise ValueError\|raise RuntimeError\|raise TypeError" src/storeops/*/service.py src/storeops/*/routes.py
```
Any hit outside a test file is a Rule 3 (Error contract) violation — cite the file:line.

## 3. LLM-assessed checks — citation is mandatory

For every checklist item in `grading-criteria.md` that isn't covered by an automated command
above, you must name the specific file and line(s) that are your evidence — for both a PASS
claim ("Rule 5 respected: `reports/service.py:34` only calls `activities_service.list_activities`,
a read") and a FAIL claim. **If you cannot point to a specific line, do not mark the check FAIL or
PASS — mark it AMBIGUOUS** and let `grading-criteria.md`'s fallback rule handle it. Do not guess.

Checks in this category: event-bus-only side effects (Rule 2), layer separation's semantic half
(business logic in routes, HTTP/external calls in repositories — Rule 4), reports read-only
(Rule 5), AC-to-test mapping, `generator-summary.md` accuracy against the real diff.

## 4. Cross-check `generator-summary.md` against the actual diff

Run `git diff --stat` (or equivalent) against the sprint's declared file list. Any file changed
that isn't in `generator-summary.md`'s file list, or any AC marked "done" in the self-check table
without a corresponding test you can cite, is evidence for the Process Integrity dimension.

## 5. Write `evaluator-feedback.md`

Structure: overall verdict, then one section per dimension from `grading-criteria.md` with each
checklist item's result (PASS/FAIL/AMBIGUOUS) and its citation, then hard-gate results called out
separately at the top (they determine FAIL regardless of the rest). On FAIL or CONDITIONAL PASS,
every failing item needs enough detail (file, line, what's wrong, what would fix it) for the
Generator's next iteration to act on without re-deriving the finding.
