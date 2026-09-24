from __future__ import annotations

from storeops.shared.errors import NotFoundError
from storeops.staff.repository import StaffRepository, repository
from storeops.staff.types import User


class StaffService:
    def __init__(self, repo: StaffRepository) -> None:
        self._repo = repo

    def get_user(self, user_id: str) -> User:
        user = self._repo.get(user_id)
        if user is None:
            raise NotFoundError(f"Staff member {user_id} not found")
        return user


service = StaffService(repository)
