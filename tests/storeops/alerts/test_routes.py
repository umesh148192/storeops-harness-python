from __future__ import annotations

from storeops.shared.events import EventName, event_bus


def test_list_alerts_empty_by_default(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_list_alerts_returns_notifications_from_sla_breach_event(client):
    event_bus.emit(EventName.SLA_BREACH, {"task_id": "t1", "assignee_id": "stub-user-1"})

    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert len(response.json()) == 1
