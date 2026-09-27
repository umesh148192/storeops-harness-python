from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from storeops.activities import router as activities_router
from storeops.activities.service import service as activities_service
from storeops.alerts import router as alerts_router
from storeops.alerts.service import service as alerts_service
from storeops.programmes import router as programmes_router
from storeops.reports import router as reports_router
from storeops.reports.service import service as reports_service
from storeops.shared.errors import AppError
from storeops.shared.events import event_bus

app = FastAPI(title="StoreOps")


# Deployment health check (Section#6) — no auth, no downstream dependencies.
# Deliberately outside the Section#3 API surface.
@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


# activities/programmes/alerts/reports are all live in this phase.
app.include_router(activities_router)
app.include_router(programmes_router)
app.include_router(alerts_router)
app.include_router(reports_router)

# Cross-module side effects are wired here via the event bus, never through
# direct service-to-service imports from activities/programmes.
alerts_service.register_event_handlers(event_bus)
reports_service.register_event_handlers(event_bus)
activities_service.register_event_handlers(event_bus)
