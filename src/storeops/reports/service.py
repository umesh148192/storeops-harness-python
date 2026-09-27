from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from storeops.activities.service import service as activities_service
from storeops.activities.types import Task, TaskCategory, TaskStatus
from storeops.programmes.service import service as programmes_service
from storeops.reports.repository import ReportRepository, repository
from storeops.reports.types import Report, ReportStatus, ReportType
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventBus, EventName, event_bus
from storeops.shared.stores import list_stores_by_region


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

    def generate_regional_rollup(self, region: str) -> Report:
        # Read-only aggregation across every store in the region; never writes
        # back to programmes/activities.
        stores = list_stores_by_region(region)
        if not stores:
            raise NotFoundError(f"No stores found in region {region}")

        tasks: list[Task] = []
        for store in stores:
            for programme in programmes_service.list_programmes(store.id):
                tasks.extend(activities_service.list_activities(programme_id=programme.id))

        now = datetime.now(timezone.utc)
        data = {
            "completed_tasks": sum(1 for task in tasks if task.status == TaskStatus.DONE),
            "total_tasks": len(tasks),
        }
        for category in TaskCategory:
            data[f"overdue_{category.value}"] = sum(
                1
                for task in tasks
                if task.category == category
                and task.due_date is not None
                and task.due_date < now
                and task.status != TaskStatus.DONE
            )
        blocked_tasks = [task for task in tasks if task.status == TaskStatus.BLOCKED]

        report = Report(
            id=str(uuid4()),
            report_type=ReportType.REGIONAL_ROLLUP,
            status=ReportStatus.READY,
            region=region,
            data=data,
            blocked_tasks=blocked_tasks,
        )
        created = self._repo.create(report)
        event_bus.emit(
            EventName.REGIONAL_ROLLUP_GENERATED,
            {"region": region, "report_id": created.id},
        )
        return created

    def register_event_handlers(self, bus: EventBus) -> None:
        bus.subscribe(EventName.PROGRAMME_CLOSED, self._on_programme_closed)

    def _on_programme_closed(self, payload: Any) -> None:
        store_id = payload.get("store_id") if payload else None
        if store_id is None:
            return
        self.generate_store_summary(store_id)


service = ReportService(repository)
