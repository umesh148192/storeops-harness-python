from __future__ import annotations

import pytest

from storeops.activities.service import service as activities_service
from storeops.activities.types import TaskCreate, TaskStatus, TaskUpdate
from storeops.programmes.service import service as programmes_service
from storeops.programmes.types import ProjectCreate
from storeops.reports.repository import repository as reports_repo
from storeops.reports.service import service
from storeops.reports.types import ReportStatus
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventBus, EventName


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
