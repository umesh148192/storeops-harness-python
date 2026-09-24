from __future__ import annotations

from storeops.reports.repository import ReportRepository
from storeops.reports.types import Report, ReportType


def test_create_and_get_roundtrip():
    repo = ReportRepository()
    report = repo.create(Report(id="", report_type=ReportType.STORE_SUMMARY, store_id="store-1"))

    assert repo.get(report.id) == report


def test_get_missing_returns_none():
    repo = ReportRepository()
    assert repo.get("missing") is None
