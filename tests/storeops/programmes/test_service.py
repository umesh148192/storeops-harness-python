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
