# Skill: Grading Criteria

Evaluator-specific. The Evaluation Framework — 3 dimensions, weights summing to 100%, each with
hard gates, a checklist, and a stated handling of LLM output variability. Paired with
`how-to-review.md` for the review procedure itself.

## Dimension 1 — Architecture Compliance (40%)

**Hard gates** (any one → immediate sprint FAIL, regardless of everything else):
- `uv run lint-imports` reports any contract broken (Rule 1: module boundary).
- A raw `raise Exception(...)` (or bare `ValueError`/`RuntimeError`/`TypeError`) found in
  `routes.py` or `service.py` outside tests (Rule 3: error contract).

**Checklist** (LLM-assessed, binary per item, citation required — see `how-to-review.md` §3):
1. Cross-module side effects go through `event_bus.emit()`, not a direct import of another
   module's `service` for the purpose of triggering it (Rule 2).
2. `routes.py` contains no business logic; `repository.py` makes no calls outside its own
   in-memory store (Rule 4, semantic half — the structural half is the Rule 1 hard gate above).
3. Any `reports/` change makes only read calls into other modules' services (Rule 5).

## Dimension 2 — Correctness & Coverage (40%)

**Hard gates**:
- `uv run python -m pytest` reports any failing test.
- `uv run python scripts/check_coverage.py` reports any layer below its Section#5 threshold
  (service 80%, routes 70%, shared 60%, overall 70%) for a layer the sprint touched.

**Checklist**:
1. Every GIVEN/WHEN/THEN acceptance criterion in the sprint contract has a citable test function
   that asserts it (not just "coverage is high enough" — coverage measures lines executed, not
   that the right thing was asserted).
2. No `@pytest.mark.skip`/`xfail` introduced to dodge a failing test or inflate coverage.

## Dimension 3 — Process Integrity (20%)

**Hard gates**:
- `generator-summary.md` is missing, or missing its AC self-check table.
- A file was changed outside the sprint contract's declared scope and isn't disclosed in
  `generator-summary.md`'s "known gaps" section.

**Checklist**:
1. Every row in the AC self-check table cites a real test function that exists in the diff.
2. The file-changed list in `generator-summary.md` matches `git diff --stat` exactly.

## Handling LLM output variability

- **Deterministic checks stay deterministic**: every hard gate above is a tool exit code or a
  grep match — the same input always produces the same result, by construction. This is why each
  dimension's hard gates map to an automated command (Section#8's recommendation): the parts of
  the verdict that must never wobble don't depend on LLM judgment at all.
- **Converting LLM judgment to binary**: every non-hard-gate checklist item resolves to exactly one
  of PASS / FAIL / AMBIGUOUS. AMBIGUOUS is not a third checklist state that counts as partial
  credit — it's an escape hatch for "I can't cite evidence," and it is scored as FAIL for the
  numeric total (see below) while also being reported separately so a human reviewing
  `evaluator-feedback.md` can tell "the Generator did this wrong" apart from "the Evaluator
  couldn't tell."
- **Fallback when the Evaluator's own output is ambiguous**: if any checklist item comes back
  AMBIGUOUS, the sprint's verdict ceiling is CONDITIONAL PASS — it can never be a clean PASS, even
  if the numeric score below would otherwise clear the PASS threshold. Ambiguity never silently
  resolves in the Generator's favor.

## Verdict combination

1. Any hard gate breached, in any dimension → **FAIL**. Stop; don't compute a score.
2. Otherwise, per dimension: `dimension_score = (checklist items scored PASS) / (total checklist
   items in that dimension) × 100`. AMBIGUOUS counts as not-PASS for this computation.
3. `weighted_total = 0.4×dim1 + 0.4×dim2 + 0.2×dim3`.
4. `weighted_total ≥ 90` → **PASS** (and no item was AMBIGUOUS — see the ceiling rule above).
   `70 ≤ weighted_total < 90`, OR any AMBIGUOUS item regardless of score → **CONDITIONAL PASS**.
   `weighted_total < 70` → **FAIL**.

CONDITIONAL PASS advances to the next sprint (it's not blocking) but the Monitor must record the
specific follow-up item(s) in `run-log.md`'s quality-trend notes — it's a signal for skill-file
drift detection, not a free pass to forget about.
