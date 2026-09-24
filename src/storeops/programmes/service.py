from __future__ import annotations

from uuid import uuid4

from storeops.programmes.repository import ProgrammeRepository, repository
from storeops.programmes.types import Project, ProjectCreate, ProjectMember, ProjectMemberCreate
from storeops.shared.errors import NotFoundError
from storeops.staff.service import service as staff_service


class ProgrammeService:
    def __init__(self, repo: ProgrammeRepository) -> None:
        self._repo = repo

    def list_programmes(self, store_id: str) -> list[Project]:
        return self._repo.list_by_store(store_id)

    def create_programme(self, data: ProjectCreate, store_id: str) -> Project:
        project = Project(id=str(uuid4()), store_id=store_id, **data.model_dump())
        return self._repo.create(project)

    def get_programme(self, project_id: str) -> Project:
        project = self._repo.get(project_id)
        if project is None:
            raise NotFoundError(f"Programme {project_id} not found")
        return project

    def add_member(self, project_id: str, data: ProjectMemberCreate) -> ProjectMember:
        self.get_programme(project_id)
        staff_service.get_user(data.user_id)

        member = ProjectMember(id=str(uuid4()), project_id=project_id, **data.model_dump())
        return self._repo.add_member(member)


service = ProgrammeService(repository)
