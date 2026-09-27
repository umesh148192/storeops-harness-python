from __future__ import annotations

from uuid import uuid4

from storeops.activities.types import Task, TaskCategory, TaskPriority
from storeops.programmes.repository import ProgrammeRepository, repository
from storeops.programmes.types import (
    Project,
    ProjectCreate,
    ProjectMember,
    ProjectMemberCreate,
    ProjectRole,
)
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventName, event_bus
from storeops.staff.service import service as staff_service

# Fixed standard PLANOGRAM task set cloned by `clone_planogram_template`. Each item is
# (title, department, priority) — a hardcoded definition, not a manageable/persisted resource
# (see spec.md decision #2).
_PLANOGRAM_TEMPLATE: list[tuple[str, str, TaskPriority]] = [
    ("Reset front-of-store endcap", "Front End", TaskPriority.HIGH),
    ("Restock grocery aisle planogram", "Grocery", TaskPriority.MEDIUM),
    ("Update seasonal display signage", "Marketing", TaskPriority.MEDIUM),
]


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

    def list_department_leads(self, project_id: str) -> list[ProjectMember]:
        self.get_programme(project_id)
        return [
            member
            for member in self._repo.list_members(project_id)
            if member.role == ProjectRole.DEPARTMENT_LEAD
        ]

    def list_store_managers(self, project_id: str) -> list[ProjectMember]:
        self.get_programme(project_id)
        return [
            member
            for member in self._repo.list_members(project_id)
            if member.role == ProjectRole.STORE_MANAGER
        ]

    def clone_planogram_template(self, project_id: str) -> list[Task]:
        # Local import: activities.service already imports programmes.service at module
        # level (to validate programme_id in create_activity), so importing
        # activities.service at this module's top level would create a circular import
        # deadlock. Deferring to call time is safe because by the time this method runs,
        # the app has finished starting up and both modules are fully initialized. This
        # import is only ever used below for reads (list_activities), which Rule 2
        # explicitly permits via direct service import; the actual task-creation write
        # crosses the module boundary via event_bus.emit() only, per Rule 2.
        # pylint: disable-next=import-outside-toplevel,cyclic-import
        from storeops.activities.service import service as activities_service

        self.get_programme(project_id)

        existing_ids = {
            task.id for task in activities_service.list_activities(programme_id=project_id)
        }

        payload = {
            "tasks": [
                {
                    "title": title,
                    "category": TaskCategory.PLANOGRAM,
                    "programme_id": project_id,
                    "department": department,
                    "priority": priority,
                }
                for title, department, priority in _PLANOGRAM_TEMPLATE
            ]
        }
        event_bus.emit(EventName.PLANOGRAM_TEMPLATE_CLONE_REQUESTED, payload)

        return [
            task
            for task in activities_service.list_activities(programme_id=project_id)
            if task.id not in existing_ids
        ]


service = ProgrammeService(repository)
