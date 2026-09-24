from __future__ import annotations

from uuid import uuid4

from storeops.programmes.types import Project, ProjectMember


class ProgrammeRepository:
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._members: dict[str, ProjectMember] = {}

    def reset(self) -> None:
        self._projects.clear()
        self._members.clear()

    def list_by_store(self, store_id: str) -> list[Project]:
        return [p for p in self._projects.values() if p.store_id == store_id]

    def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    def create(self, project: Project) -> Project:
        project_id = project.id or str(uuid4())
        stored = project.model_copy(update={"id": project_id})
        self._projects[project_id] = stored
        return stored

    def add_member(self, member: ProjectMember) -> ProjectMember:
        member_id = member.id or str(uuid4())
        stored = member.model_copy(update={"id": member_id})
        self._members[member_id] = stored
        return stored

    def list_members(self, project_id: str) -> list[ProjectMember]:
        return [m for m in self._members.values() if m.project_id == project_id]


repository = ProgrammeRepository()
