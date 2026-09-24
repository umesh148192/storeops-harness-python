from __future__ import annotations

from storeops.programmes.repository import ProgrammeRepository
from storeops.programmes.types import Project, ProjectMember, ProjectRole


def test_create_and_list_by_store():
    repo = ProgrammeRepository()
    repo.create(Project(id="", name="Seasonal rollout", store_id="store-1"))
    repo.create(Project(id="", name="Other store project", store_id="store-2"))

    assert len(repo.list_by_store("store-1")) == 1


def test_get_missing_returns_none():
    repo = ProgrammeRepository()
    assert repo.get("missing") is None


def test_add_member_and_list_members():
    repo = ProgrammeRepository()
    project = repo.create(Project(id="", name="Refit", store_id="store-1"))

    member = repo.add_member(
        ProjectMember(id="", project_id=project.id, user_id="user-1", role=ProjectRole.ASSOCIATE)
    )

    assert member.id
    assert repo.list_members(project.id) == [member]
