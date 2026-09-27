from __future__ import annotations

from datetime import datetime, timedelta, timezone

from storeops.activities.service import service as activities_service
from storeops.activities.types import TaskCategory, TaskCreate
from storeops.main import app
from storeops.programmes.service import service as programmes_service
from storeops.programmes.types import ProjectCreate

PAST = datetime.now(timezone.utc) - timedelta(days=1)


def test_get_regional_rollup_returns_200_with_report_shape(client):
    programme = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    activities_service.create_activity(
        TaskCreate(
            title="Restock overdue",
            programme_id=programme.id,
            category=TaskCategory.RESTOCKING,
            due_date=PAST,
        )
    )

    response = client.get("/api/reports/region/North")

    assert response.status_code == 200
    body = response.json()
    assert body["report_type"] == "REGIONAL_ROLLUP"
    assert body["region"] == "North"
    assert body["data"]["overdue_RESTOCKING"] == 1
    assert body["blocked_tasks"] == []


def test_get_regional_rollup_missing_region_returns_404_app_error_json(client):
    response = client.get("/api/reports/region/Nonexistent")

    assert response.status_code == 404
    body = response.json()
    assert "code" in body
    assert "message" in body


def test_reports_router_is_wired_into_app():
    assert "/api/reports/region/{region_id}" in app.openapi()["paths"]
