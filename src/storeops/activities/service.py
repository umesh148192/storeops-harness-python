from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from storeops.activities.repository import ActivityRepository, repository
from storeops.activities.types import (
    BulkStatusFailure,
    BulkStatusUpdateItem,
    BulkStatusUpdateResponse,
    SlaCheckResult,
    Task,
    TaskAuditEntry,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)
from storeops.programmes.service import service as programmes_service
from storeops.shared.deps import UserContext
from storeops.shared.entities import StaffRole
from storeops.shared.errors import AppError, ForbiddenError, NotFoundError, ValidationError
from storeops.shared.events import EventBus, EventName, event_bus

DEFAULT_SLA_GRACE_PERIOD_HOURS = 24

_SLA_ELIGIBLE_PRIORITIES = (TaskPriority.HIGH, TaskPriority.CRITICAL)


class ActivityService:
    def __init__(self, repo: ActivityRepository) -> None:
        self._repo = repo

    def register_event_handlers(self, bus: EventBus) -> None:
        bus.subscribe(
            EventName.PLANOGRAM_TEMPLATE_CLONE_REQUESTED,
            self._on_planogram_template_clone_requested,
        )

    def _on_planogram_template_clone_requested(self, payload: Any) -> None:
        if not payload:
            return
        for item in payload.get("tasks", []):
            self.create_activity(TaskCreate(**item))

    def list_activities(
        self, programme_id: str | None = None, status: TaskStatus | None = None
    ) -> list[Task]:
        return self._repo.list(programme_id=programme_id, status=status)

    def create_activity(self, data: TaskCreate) -> Task:
        if data.programme_id is not None:
            programmes_service.get_programme(data.programme_id)

        task = Task(id=str(uuid4()), **data.model_dump())
        return self._repo.create(task)

    def get_activity(self, task_id: str) -> Task:
        task = self._repo.get(task_id)
        if task is None:
            raise NotFoundError(f"Activity {task_id} not found")
        return task

    def get_audit_entries(self, task_id: str) -> list[TaskAuditEntry]:
        return self._repo.list_audit_entries(task_id)

    def update_activity(self, task_id: str, data: TaskUpdate) -> Task:
        self.get_activity(task_id)
        fields = data.model_dump(exclude_unset=True)
        updated = self._repo.update(task_id, **fields)
        if updated is None:
            raise NotFoundError(f"Activity {task_id} not found")

        if updated.status == TaskStatus.BLOCKED and updated.priority == TaskPriority.CRITICAL:
            payload = {"task_id": updated.id, "assignee_id": updated.assignee_id}
            event_bus.emit(EventName.SLA_BREACH, payload)

        return updated

    def bulk_update_status(
        self, updates: Sequence[BulkStatusUpdateItem | dict[str, object]], ctx: UserContext
    ) -> BulkStatusUpdateResponse:
        updated: list[Task] = []
        failed: list[BulkStatusFailure] = []

        for raw_update in updates:
            try:
                update = BulkStatusUpdateItem.model_validate(raw_update)
                task = self.get_activity(update.task_id)
                if ctx.role != StaffRole.STORE_MANAGER and task.assignee_id != ctx.user_id:
                    raise ForbiddenError(
                        "Only the assignee or a store manager may update this activity"
                    )

                previous_status = task.status
                updated_task = self._repo.update(update.task_id, status=update.status)
                if updated_task is None:
                    raise NotFoundError(f"Activity {update.task_id} not found")

                entry = TaskAuditEntry(
                    task_id=updated_task.id,
                    actor_id=ctx.user_id,
                    previous_status=previous_status,
                    new_status=updated_task.status,
                    note=update.note,
                    updated_at=datetime.now(timezone.utc).isoformat(),
                )
                self._repo.add_audit_entry(updated_task.id, entry)
                updated.append(updated_task)

                if (
                    updated_task.status == TaskStatus.BLOCKED
                    and updated_task.priority == TaskPriority.CRITICAL
                ):
                    payload = {
                        "task_id": updated_task.id,
                        "assignee_id": updated_task.assignee_id,
                    }
                    event_bus.emit(EventName.SLA_BREACH, payload)
            except AppError as exc:
                task_id = getattr(raw_update, "task_id", None)
                if task_id is None and isinstance(raw_update, dict):
                    task_id = raw_update.get("task_id")
                failed.append(
                    BulkStatusFailure(
                        task_id=str(task_id or "unknown"),
                        code=exc.code,
                        message=exc.message,
                    )
                )

        return BulkStatusUpdateResponse(updated=updated, failed=failed)

    def delete_activity(self, task_id: str, ctx: UserContext) -> None:
        task = self.get_activity(task_id)

        # PLACEHOLDER: ownership check, intentionally minimal at stub stage.
        if ctx.role != StaffRole.STORE_MANAGER and task.assignee_id != ctx.user_id:
            raise ForbiddenError("Only the assignee or a store manager may delete this activity")

        self._repo.delete(task_id)

    def evaluate_sla(
        self, grace_period_hours: int = DEFAULT_SLA_GRACE_PERIOD_HOURS
    ) -> SlaCheckResult:
        if grace_period_hours < 0:
            raise ValidationError("grace_period_hours must not be negative")

        now = datetime.now(timezone.utc)
        grace_period = timedelta(hours=grace_period_hours)
        breached: list[str] = []
        escalated: list[str] = []

        for task in self._repo.list():
            if task.status == TaskStatus.DONE:
                continue
            if task.priority not in _SLA_ELIGIBLE_PRIORITIES:
                continue
            if task.due_date is None or task.due_date > now:
                continue

            payload = {
                "task_id": task.id,
                "assignee_id": task.assignee_id,
                "programme_id": task.programme_id,
            }

            if not self._repo.has_sla_breached(task.id):
                self._repo.mark_sla_breached(task.id)
                event_bus.emit(EventName.SLA_BREACH, payload)
                breached.append(task.id)

            if now - task.due_date > grace_period and not self._repo.has_sla_escalated(task.id):
                self._repo.mark_sla_escalated(task.id)
                event_bus.emit(EventName.SLA_ESCALATION, payload)
                escalated.append(task.id)

        return SlaCheckResult(breached=breached, escalated=escalated)


service = ActivityService(repository)
