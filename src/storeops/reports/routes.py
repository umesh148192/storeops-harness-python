from __future__ import annotations

from fastapi import APIRouter

from storeops.reports.service import service
from storeops.reports.types import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/region/{region_id}", response_model=Report)
async def get_regional_rollup(region_id: str) -> Report:
    return service.generate_regional_rollup(region_id)
