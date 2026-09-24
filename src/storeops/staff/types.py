from __future__ import annotations

from pydantic import BaseModel

from storeops.shared.entities import StaffRole

__all__ = ["StaffRole", "User", "UserProfile", "AuthToken"]


class User(BaseModel):
    id: str
    email: str
    name: str


class UserProfile(BaseModel):
    user_id: str
    store_id: str
    role: StaffRole


class AuthToken(BaseModel):
    token: str
    user_id: str
    expires_at: str
