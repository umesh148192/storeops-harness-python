from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class Store(BaseModel):
    id: str
    name: str
    region: str


class StaffRole(str, Enum):
    REGIONAL_MANAGER = "REGIONAL_MANAGER"
    STORE_MANAGER = "STORE_MANAGER"
    DEPARTMENT_LEAD = "DEPARTMENT_LEAD"
    ASSOCIATE = "ASSOCIATE"
