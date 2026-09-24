from __future__ import annotations

from uuid import uuid4

from storeops.activities.repository import ActivityRepository, repository
from storeops.activities.types import Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from storeops.programmes.service import service as programmes_service
from storeops.shared.deps import UserContext
from storeops.shared.entities import StaffRole
from storeops.shared.errors import ForbiddenError, NotFoundError
from storeops.shared.events import EventName, event_bus


class ActivityService:
    def __init__(self, repo: ActivityRepository) -> None:
        self._repo = repo

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

    def delete_activity(self, task_id: str, ctx: UserContext) -> None:
        task = self.get_activity(task_id)

        # PLACEHOLDER: ownership check, intentionally minimal at stub stage.
        if ctx.role != StaffRole.STORE_MANAGER and task.assignee_id != ctx.user_id:
            raise ForbiddenError("Only the assignee or a store manager may delete this activity")

        self._repo.delete(task_id)


service = ActivityService(repository)
