from __future__ import annotations

import pytest

from storeops.programmes.service import service
from storeops.programmes.types import ProjectCreate, ProjectMemberCreate, ProjectRole
from storeops.shared.errors import NotFoundError


def test_create_and_list_programmes():
    service.create_programme(ProjectCreate(name="Seasonal rollout"), store_id="store-1")

    programmes = service.list_programmes("store-1")

    assert len(programmes) == 1
    assert programmes[0].name == "Seasonal rollout"


def test_get_programme_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        service.get_programme("missing")


def test_add_member_validates_programme_exists():
    with pytest.raises(NotFoundError):
        service.add_member("missing", ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE))


def test_add_member_validates_user_exists():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")

    with pytest.raises(NotFoundError):
        service.add_member(project.id, ProjectMemberCreate(user_id="unknown-user", role=ProjectRole.ASSOCIATE))


def test_add_member_success():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")

    member = service.add_member(
        project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE)
    )

    assert member.project_id == project.id
    assert member.user_id == "stub-user-1"


def test_list_department_leads_returns_only_department_lead_members():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.DEPARTMENT_LEAD))
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE))

    leads = service.list_department_leads(project.id)

    assert len(leads) == 1
    assert leads[0].user_id == "stub-user-1"
    assert leads[0].role == ProjectRole.DEPARTMENT_LEAD


def test_list_department_leads_returns_empty_list_when_none_exist():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE))

    leads = service.list_department_leads(project.id)

    assert leads == []


def test_list_department_leads_missing_programme_raises_not_found():
    with pytest.raises(NotFoundError):
        service.list_department_leads("missing")


def test_list_store_managers_returns_only_store_manager_members():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.STORE_MANAGER))
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE))

    managers = service.list_store_managers(project.id)

    assert len(managers) == 1
    assert managers[0].user_id == "stub-user-1"
    assert managers[0].role == ProjectRole.STORE_MANAGER


def test_list_store_managers_returns_empty_list_when_none_exist():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    service.add_member(project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.ASSOCIATE))

    managers = service.list_store_managers(project.id)

    assert managers == []


def test_list_store_managers_missing_programme_raises_not_found():
    with pytest.raises(NotFoundError):
        service.list_store_managers("missing")
