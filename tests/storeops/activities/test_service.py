from __future__ import annotations

import pytest

from storeops.activities.service import service
from storeops.activities.types import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from storeops.shared.deps import UserContext
from storeops.shared.entities import StaffRole
from storeops.shared.errors import ForbiddenError, NotFoundError
from storeops.shared.events import EventName, event_bus

MANAGER = UserContext(user_id="manager-1", store_id="store-1", role=StaffRole.STORE_MANAGER)
ASSOCIATE = UserContext(user_id="associate-1", store_id="store-1", role=StaffRole.ASSOCIATE)


def test_create_activity_without_programme():
    task = service.create_activity(TaskCreate(title="Restock aisle 4"))
    assert task.id
    assert task.title == "Restock aisle 4"


def test_create_activity_with_unknown_programme_raises_not_found():
    with pytest.raises(NotFoundError):
        service.create_activity(TaskCreate(title="Restock aisle 4", programme_id="missing"))


def test_get_activity_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        service.get_activity("missing")


def test_update_activity_to_blocked_critical_emits_sla_breach_event():
    task = service.create_activity(TaskCreate(title="Check freezer", assignee_id="associate-1"))
    received = []
    event_bus.subscribe(EventName.SLA_BREACH, received.append)

    service.update_activity(
        task.id, TaskUpdate(status=TaskStatus.BLOCKED, priority=TaskPriority.CRITICAL)
    )

    assert len(received) == 1
    assert received[0]["task_id"] == task.id


def test_update_activity_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        service.update_activity("missing", TaskUpdate(status=TaskStatus.DONE))


def test_delete_activity_allowed_for_store_manager():
    task = service.create_activity(TaskCreate(title="Audit"))
    service.delete_activity(task.id, MANAGER)
    with pytest.raises(NotFoundError):
        service.get_activity(task.id)


def test_delete_activity_forbidden_for_non_owner_non_manager():
    task = service.create_activity(TaskCreate(title="Audit", assignee_id="someone-else"))
    with pytest.raises(ForbiddenError):
        service.delete_activity(task.id, ASSOCIATE)
