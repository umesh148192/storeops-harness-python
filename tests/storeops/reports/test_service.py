from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from storeops.activities.service import service as activities_service
from storeops.activities.types import TaskCategory, TaskCreate, TaskStatus, TaskUpdate
from storeops.programmes.service import service as programmes_service
from storeops.programmes.types import ProjectCreate
from storeops.reports.repository import repository as reports_repo
from storeops.reports.service import service
from storeops.reports.types import ReportStatus, ReportType
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventBus, EventName, event_bus

PAST = datetime.now(timezone.utc) - timedelta(days=1)
FUTURE = datetime.now(timezone.utc) + timedelta(days=1)


def test_get_report_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        service.get_report("missing")


def test_generate_store_summary_aggregates_read_only():
    programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    task = activities_service.create_activity(TaskCreate(title="Restock"))
    activities_service.update_activity(task.id, TaskUpdate(status=TaskStatus.DONE))

    report = service.generate_store_summary("store-1")

    assert report.status == ReportStatus.READY
    assert report.data["programme_count"] == 1
    assert report.data["completed_tasks"] == 1


def test_programme_closed_event_triggers_summary_generation():
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(EventName.PROGRAMME_CLOSED, {"store_id": "store-1"})

    stored_reports = reports_repo.list_all()
    assert len(stored_reports) == 1
    assert stored_reports[0].store_id == "store-1"


def test_programme_closed_event_without_store_id_is_ignored():
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(EventName.PROGRAMME_CLOSED, {})


def test_generate_regional_rollup_aggregates_across_stores_in_region():
    programme_1 = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    programme_2 = programmes_service.create_programme(ProjectCreate(name="Reset"), store_id="store-2")
    task_1 = activities_service.create_activity(
        TaskCreate(title="Restock", programme_id=programme_1.id)
    )
    activities_service.update_activity(task_1.id, TaskUpdate(status=TaskStatus.DONE))
    activities_service.create_activity(TaskCreate(title="Audit", programme_id=programme_2.id))

    report = service.generate_regional_rollup("North")

    assert report.report_type == ReportType.REGIONAL_ROLLUP
    assert report.data["total_tasks"] == 2
    assert report.data["completed_tasks"] == 1


def test_generate_regional_rollup_counts_overdue_by_category():
    programme = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    activities_service.create_activity(
        TaskCreate(
            title="Restock overdue",
            programme_id=programme.id,
            category=TaskCategory.RESTOCKING,
            due_date=PAST,
        )
    )
    activities_service.create_activity(
        TaskCreate(
            title="Audit not due",
            programme_id=programme.id,
            category=TaskCategory.AUDIT,
            due_date=FUTURE,
        )
    )

    report = service.generate_regional_rollup("North")

    assert report.data["overdue_RESTOCKING"] == 1
    assert report.data["overdue_AUDIT"] == 0


def test_generate_regional_rollup_lists_blocked_tasks():
    programme = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    blocked_task = activities_service.create_activity(
        TaskCreate(title="Blocked task", programme_id=programme.id)
    )
    activities_service.update_activity(blocked_task.id, TaskUpdate(status=TaskStatus.BLOCKED))
    activities_service.create_activity(TaskCreate(title="Normal task", programme_id=programme.id))

    report = service.generate_regional_rollup("North")

    assert [task.id for task in report.blocked_tasks] == [blocked_task.id]


def test_generate_regional_rollup_missing_region_raises_not_found():
    with pytest.raises(NotFoundError):
        service.generate_regional_rollup("Nonexistent")

    assert reports_repo.list_all() == []


def test_generate_regional_rollup_emits_event_exactly_once():
    programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    received: list[dict[str, str]] = []
    event_bus.subscribe(EventName.REGIONAL_ROLLUP_GENERATED, received.append)

    report = service.generate_regional_rollup("North")

    assert received == [{"region": "North", "report_id": report.id}]
