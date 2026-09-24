from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ReportType(str, Enum):
    STORE_SUMMARY = "STORE_SUMMARY"
    REGIONAL_ROLLUP = "REGIONAL_ROLLUP"
    DEPARTMENT_PERFORMANCE = "DEPARTMENT_PERFORMANCE"


class ReportStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"


class Report(BaseModel):
    id: str
    report_type: ReportType
    status: ReportStatus = ReportStatus.PENDING
    store_id: str
    data: dict[str, int] = {}
