from __future__ import annotations

import pytest

from storeops.activities.service import service as activities_service
from storeops.activities.types import TaskCategory, TaskPriority
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


def test_clone_planogram_template_creates_one_task_per_template_item():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")

    created = service.clone_planogram_template(project.id)

    assert len(created) == 3
    for task in created:
        assert task.category == TaskCategory.PLANOGRAM
        assert task.programme_id == project.id


def test_clone_planogram_template_applies_department_and_priority_per_item():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")

    created = service.clone_planogram_template(project.id)

    by_department = {task.department: task for task in created}
    assert by_department["Front End"].priority == TaskPriority.HIGH
    assert by_department["Grocery"].priority == TaskPriority.MEDIUM
    assert by_department["Marketing"].priority == TaskPriority.MEDIUM


def test_clone_planogram_template_missing_programme_raises_not_found_and_creates_nothing():
    before = len(activities_service.list_activities())

    with pytest.raises(NotFoundError):
        service.clone_planogram_template("missing")

    assert len(activities_service.list_activities()) == before


def test_clone_planogram_template_is_additive_not_deduplicated():
    project = service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")

    first = service.clone_planogram_template(project.id)
    second = service.clone_planogram_template(project.id)

    assert len(first) == len(second) == 3
    assert {task.id for task in first}.isdisjoint({task.id for task in second})
    all_tasks = activities_service.list_activities(programme_id=project.id)
    assert len(all_tasks) == 6
