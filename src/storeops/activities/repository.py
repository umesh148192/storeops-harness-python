from __future__ import annotations

from typing import List
from uuid import uuid4

from storeops.activities.types import Task, TaskAuditEntry, TaskStatus


class ActivityRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._audit_entries: dict[str, list[TaskAuditEntry]] = {}

    def reset(self) -> None:
        self._tasks.clear()
        self._audit_entries.clear()

    def list(
        self, programme_id: str | None = None, status: TaskStatus | None = None
    ) -> List[Task]:
        tasks = list(self._tasks.values())
        if programme_id is not None:
            tasks = [t for t in tasks if t.programme_id == programme_id]
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return list(tasks)

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def create(self, task: Task) -> Task:
        task_id = task.id or str(uuid4())
        stored = task.model_copy(update={"id": task_id})
        self._tasks[task_id] = stored
        return stored

    def update(self, task_id: str, **fields: object) -> Task | None:
        existing = self._tasks.get(task_id)
        if existing is None:
            return None
        updated = existing.model_copy(update=fields)
        self._tasks[task_id] = updated
        return updated

    def add_audit_entry(self, task_id: str, entry: TaskAuditEntry) -> TaskAuditEntry:
        self._audit_entries.setdefault(task_id, []).append(entry)
        return entry

    def list_audit_entries(self, task_id: str) -> List[TaskAuditEntry]:
        return list(self._audit_entries.get(task_id, []))

    def delete(self, task_id: str) -> bool:
        self._audit_entries.pop(task_id, None)
        return self._tasks.pop(task_id, None) is not None


repository = ActivityRepository()
