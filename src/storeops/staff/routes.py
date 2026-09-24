from __future__ import annotations

from fastapi import APIRouter

# No routes registered: authentication/CRUD for staff is out of scope for this
# phase. The router exists for structural symmetry with the other modules and
# is intentionally NOT included in the app in main.py.
router = APIRouter(prefix="/api/staff", tags=["staff"])
