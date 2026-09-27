from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskCategory(str, Enum):
    RESTOCKING = "RESTOCKING"
    PLANOGRAM = "PLANOGRAM"
    AUDIT = "AUDIT"
    COMPLIANCE = "COMPLIANCE"
    GENERAL = "GENERAL"


class Task(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.GENERAL
    programme_id: str | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None
    department: str | None = None


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.GENERAL
    programme_id: str | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None
    department: str | None = None


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    category: TaskCategory | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None
    department: str | None = None


class BulkStatusUpdateItem(BaseModel):
    task_id: str
    status: TaskStatus
    note: str | None = None


class BulkStatusUpdateRequest(BaseModel):
    updates: list[BulkStatusUpdateItem]


class BulkStatusFailure(BaseModel):
    task_id: str
    code: str
    message: str


class TaskAuditEntry(BaseModel):
    task_id: str
    actor_id: str
    previous_status: TaskStatus
    new_status: TaskStatus
    note: str | None = None
    updated_at: str = datetime.now(timezone.utc).isoformat()


class BulkStatusUpdateResponse(BaseModel):
    updated: list[Task]
    failed: list[BulkStatusFailure]


class SlaCheckResult(BaseModel):
    breached: list[str]
    escalated: list[str]
