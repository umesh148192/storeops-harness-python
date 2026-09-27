from __future__ import annotations

from fastapi import APIRouter, Depends

from storeops.activities.types import Task
from storeops.programmes.service import service
from storeops.programmes.types import Project, ProjectCreate, ProjectMember, ProjectMemberCreate
from storeops.shared.deps import UserContext, get_current_user

router = APIRouter(prefix="/api/programmes", tags=["programmes"])


@router.get("", response_model=list[Project])
async def list_programmes(ctx: UserContext = Depends(get_current_user)) -> list[Project]:
    return service.list_programmes(ctx.store_id)


@router.post("", response_model=Project, status_code=201)
async def create_programme(
    data: ProjectCreate, ctx: UserContext = Depends(get_current_user)
) -> Project:
    return service.create_programme(data, ctx.store_id)


@router.post("/{project_id}/members", response_model=ProjectMember, status_code=201)
async def add_member(project_id: str, data: ProjectMemberCreate) -> ProjectMember:
    return service.add_member(project_id, data)


@router.post("/{project_id}/templates", response_model=list[Task], status_code=201)
async def clone_template(project_id: str) -> list[Task]:
    return service.clone_planogram_template(project_id)
