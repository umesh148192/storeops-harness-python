from __future__ import annotations

from fastapi import APIRouter

# No routes registered yet: reports is added later as a demonstration feature
# (Section#2/#3 of ProjectSpecifications.txt). This router is intentionally
# NOT included in the app in main.py.
router = APIRouter(prefix="/api/reports", tags=["reports"])
