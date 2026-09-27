from __future__ import annotations

from storeops.reports.types import Report, ReportType


def test_report_defaults_store_id_region_and_blocked_tasks():
    report = Report(id="r1", report_type=ReportType.REGIONAL_ROLLUP)

    assert report.store_id is None
    assert report.region is None
    assert report.blocked_tasks == []


def test_report_still_accepts_explicit_store_id():
    report = Report(id="r1", report_type=ReportType.STORE_SUMMARY, store_id="store-1")

    assert report.store_id == "store-1"
