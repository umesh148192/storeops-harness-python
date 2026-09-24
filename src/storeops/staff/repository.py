from __future__ import annotations

from storeops.staff.types import User

_SEED_USERS = [
    User(id="stub-user-1", email="stub.manager@storeops.test", name="Stub Manager"),
]


class StaffRepository:
    def __init__(self) -> None:
        self._users: dict[str, User] = {user.id: user for user in _SEED_USERS}

    def reset(self) -> None:
        self._users = {user.id: user for user in _SEED_USERS}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def create(self, user: User) -> User:
        self._users[user.id] = user
        return user


repository = StaffRepository()
