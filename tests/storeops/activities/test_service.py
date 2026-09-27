from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from storeops.activities.service import service
from storeops.activities.types import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from storeops.shared.deps import UserContext
from storeops.shared.entities import StaffRole
from storeops.shared.errors import ForbiddenError, NotFoundError, ValidationError
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


def test_bulk_update_status_updates_valid_tasks_and_records_audit_entries():
    task_one = service.create_activity(TaskCreate(title="Restock freezer", assignee_id=ASSOCIATE.user_id))
    task_two = service.create_activity(TaskCreate(title="Audit shelf labels", assignee_id=ASSOCIATE.user_id))
    task_three = service.create_activity(TaskCreate(title="Open task", assignee_id="someone-else"))

    result = service.bulk_update_status(
        [
            {"task_id": task_one.id, "status": TaskStatus.DONE, "note": "Completed"},
            {"task_id": task_two.id, "status": TaskStatus.BLOCKED, "note": "Waiting on replacement"},
            {"task_id": task_three.id, "status": TaskStatus.DONE, "note": "Forbidden"},
            {"task_id": "missing-task", "status": TaskStatus.DONE, "note": "Missing"},
        ],
        ASSOCIATE,
    )

    assert {task.id for task in result.updated} == {task_one.id, task_two.id}
    assert {failure.task_id for failure in result.failed} == {task_three.id, "missing-task"}
    assert service.get_audit_entries(task_one.id)[0].new_status == TaskStatus.DONE
    assert service.get_audit_entries(task_two.id)[0].new_status == TaskStatus.BLOCKED
    assert service.get_audit_entries(task_three.id) == []


def test_evaluate_sla_fires_breach_exactly_once_for_overdue_critical_task():
    task = service.create_activity(
        TaskCreate(
            title="Overdue restock",
            priority=TaskPriority.CRITICAL,
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )
    received = []
    event_bus.subscribe(EventName.SLA_BREACH, received.append)

    first = service.evaluate_sla(grace_period_hours=24)
    second = service.evaluate_sla(grace_period_hours=24)

    assert first.breached == [task.id]
    assert second.breached == []
    assert len(received) == 1
    assert received[0]["task_id"] == task.id


def test_evaluate_sla_ignores_not_due_done_and_low_priority_tasks():
    not_due = service.create_activity(
        TaskCreate(
            title="Future due date",
            priority=TaskPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    already_done = service.create_activity(
        TaskCreate(
            title="Already resolved",
            priority=TaskPriority.HIGH,
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )
    service.update_activity(already_done.id, TaskUpdate(status=TaskStatus.DONE))
    low_priority = service.create_activity(
        TaskCreate(
            title="Low priority overdue",
            priority=TaskPriority.LOW,
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )

    result = service.evaluate_sla(grace_period_hours=24)

    assert not_due.id not in result.breached
    assert already_done.id not in result.breached
    assert low_priority.id not in result.breached
    assert result.breached == []
    assert result.escalated == []


def test_evaluate_sla_escalates_exactly_once_after_grace_period_elapses():
    task = service.create_activity(
        TaskCreate(
            title="Overdue restock",
            priority=TaskPriority.CRITICAL,
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )

    within_grace = service.evaluate_sla(grace_period_hours=24)
    assert within_grace.breached == [task.id]
    assert within_grace.escalated == []

    past_grace_first = service.evaluate_sla(grace_period_hours=0)
    assert past_grace_first.breached == []
    assert past_grace_first.escalated == [task.id]

    past_grace_second = service.evaluate_sla(grace_period_hours=0)
    assert past_grace_second.escalated == []


def test_evaluate_sla_stops_alerting_once_task_is_done():
    task = service.create_activity(
        TaskCreate(
            title="Overdue restock",
            priority=TaskPriority.CRITICAL,
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )
    service.evaluate_sla(grace_period_hours=24)

    service.update_activity(task.id, TaskUpdate(status=TaskStatus.DONE))
    result = service.evaluate_sla(grace_period_hours=0)

    assert result.breached == []
    assert result.escalated == []


def test_evaluate_sla_rejects_negative_grace_period():
    with pytest.raises(ValidationError):
        service.evaluate_sla(grace_period_hours=-1)
