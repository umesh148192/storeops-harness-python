from __future__ import annotations

from uuid import uuid4

from storeops.reports.types import Report


class ReportRepository:
    def __init__(self) -> None:
        self._reports: dict[str, Report] = {}

    def reset(self) -> None:
        self._reports.clear()

    def get(self, report_id: str) -> Report | None:
        return self._reports.get(report_id)

    def list_all(self) -> list[Report]:
        return list(self._reports.values())

    def create(self, report: Report) -> Report:
        report_id = report.id or str(uuid4())
        stored = report.model_copy(update={"id": report_id})
        self._reports[report_id] = stored
        return stored


repository = ReportRepository()
