from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from storeops.activities.types import Task


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
    store_id: str | None = None
    region: str | None = None
    data: dict[str, int] = {}
    blocked_tasks: list[Task] = []
