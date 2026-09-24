from __future__ import annotations

from fastapi import APIRouter, Depends

from storeops.alerts.service import service
from storeops.alerts.types import Notification
from storeops.shared.deps import UserContext, get_current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[Notification])
async def list_alerts(ctx: UserContext = Depends(get_current_user)) -> list[Notification]:
    return service.get_alerts_for_user(ctx.user_id)
