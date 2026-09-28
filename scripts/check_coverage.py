"""Enforce per-layer coverage thresholds (ProjectSpecifications.txt Section#5).

pytest-cov / coverage.py only support a single global --cov-fail-under. This
script re-reports the same .coverage data (written by `pytest`) scoped to
each architectural layer so the differentiated thresholds can be checked.

Usage: uv run python -m pytest && uv run python scripts/check_coverage.py
"""

from __future__ import annotations

import sys

import coverage

THRESHOLDS = [
    ("Service layer", ["src/storeops/*/service.py"], 80.0),
    ("Route layer", ["src/storeops/*/routes.py"], 70.0),
    ("Shared utilities", ["src/storeops/shared/*.py"], 60.0),
    ("Overall project", ["src/storeops/*"], 70.0),
]


def main() -> int:
    cov = coverage.Coverage(data_file=".coverage")
    cov.load()

    failures: list[str] = []
    for label, include, threshold in THRESHOLDS:
        percent = cov.report(include=include, show_missing=False, file=sys.stdout)
        print(f"{label}: {percent:.1f}% (threshold {threshold:.0f}%)\n")
        if percent < threshold:
            failures.append(f"{label} is below threshold: {percent:.1f}% < {threshold:.0f}%")

    if failures:
        print("Coverage check FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("All coverage thresholds met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
