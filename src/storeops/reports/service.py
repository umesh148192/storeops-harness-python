from __future__ import annotations

from typing import Any
from uuid import uuid4

from storeops.activities.service import service as activities_service
from storeops.activities.types import TaskStatus
from storeops.programmes.service import service as programmes_service
from storeops.reports.repository import ReportRepository, repository
from storeops.reports.types import Report, ReportStatus, ReportType
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventBus, EventName


class ReportService:
    def __init__(self, repo: ReportRepository) -> None:
        self._repo = repo

    def get_report(self, report_id: str) -> Report:
        report = self._repo.get(report_id)
        if report is None:
            raise NotFoundError(f"Report {report_id} not found")
        return report

    def generate_store_summary(self, store_id: str) -> Report:
        # Read-only aggregation across activities and programmes; never writes
        # back to those modules.
        programmes = programmes_service.list_programmes(store_id)
        activities = activities_service.list_activities()
        data = {
            "programme_count": len(programmes),
            "completed_tasks": sum(1 for a in activities if a.status == TaskStatus.DONE),
            "overdue_tasks": sum(1 for a in activities if a.status == TaskStatus.BLOCKED),
        }
        report = Report(
            id=str(uuid4()),
            report_type=ReportType.STORE_SUMMARY,
            status=ReportStatus.READY,
            store_id=store_id,
            data=data,
        )
        return self._repo.create(report)

    def register_event_handlers(self, bus: EventBus) -> None:
        bus.subscribe(EventName.PROGRAMME_CLOSED, self._on_programme_closed)

    def _on_programme_closed(self, payload: Any) -> None:
        store_id = payload.get("store_id") if payload else None
        if store_id is None:
            return
        self.generate_store_summary(store_id)


service = ReportService(repository)
