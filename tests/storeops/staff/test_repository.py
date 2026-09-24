from __future__ import annotations

from storeops.staff.repository import StaffRepository
from storeops.staff.types import User


def test_seeded_user_available():
    repo = StaffRepository()
    assert repo.get("stub-user-1") is not None


def test_create_and_get_user():
    repo = StaffRepository()
    repo.create(User(id="user-2", email="a@b.test", name="Ana"))
    assert repo.get("user-2").name == "Ana"


def test_get_missing_returns_none():
    repo = StaffRepository()
    assert repo.get("missing") is None
