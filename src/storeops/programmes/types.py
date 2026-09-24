from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ProjectRole(str, Enum):
    STORE_MANAGER = "STORE_MANAGER"
    DEPARTMENT_LEAD = "DEPARTMENT_LEAD"
    ASSOCIATE = "ASSOCIATE"


class Project(BaseModel):
    id: str
    name: str
    description: str | None = None
    store_id: str


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectMember(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: ProjectRole


class ProjectMemberCreate(BaseModel):
    user_id: str
    role: ProjectRole
