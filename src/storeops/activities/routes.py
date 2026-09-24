from __future__ import annotations

from fastapi import APIRouter, Depends

from storeops.activities.service import service
from storeops.activities.types import Task, TaskCreate, TaskStatus, TaskUpdate
from storeops.shared.deps import UserContext, get_current_user

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=list[Task])
async def list_activities(
    programme_id: str | None = None, status: TaskStatus | None = None
) -> list[Task]:
    return service.list_activities(programme_id=programme_id, status=status)


@router.post("", response_model=Task, status_code=201)
async def create_activity(data: TaskCreate) -> Task:
    return service.create_activity(data)


@router.get("/{task_id}", response_model=Task)
async def get_activity(task_id: str) -> Task:
    return service.get_activity(task_id)


@router.patch("/{task_id}", response_model=Task)
async def update_activity(task_id: str, data: TaskUpdate) -> Task:
    return service.update_activity(task_id, data)


@router.delete("/{task_id}", status_code=204)
async def delete_activity(task_id: str, ctx: UserContext = Depends(get_current_user)) -> None:
    service.delete_activity(task_id, ctx)
