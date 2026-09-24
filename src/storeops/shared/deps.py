from __future__ import annotations

from pydantic import BaseModel

from storeops.shared.entities import StaffRole, Store

_FAKE_STORE = Store(id="store-1", name="Downtown", region="North")


class UserContext(BaseModel):
    user_id: str
    store_id: str
    role: StaffRole


# PLACEHOLDER: authentication is out of scope for this phase. Real auth would
# derive this from a token; here it is a fixed stand-in every request receives.
def get_current_user() -> UserContext:
    return UserContext(user_id="stub-user-1", store_id=_FAKE_STORE.id, role=StaffRole.STORE_MANAGER)


def get_current_store() -> Store:
    return _FAKE_STORE
