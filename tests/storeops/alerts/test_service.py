from __future__ import annotations

from storeops.alerts.service import service
from storeops.alerts.types import AlertType
from storeops.shared.events import EventBus, EventName


def test_get_alerts_for_user_empty_by_default():
    assert service.get_alerts_for_user("user-1") == []


def test_sla_breach_event_creates_notification_for_assignee():
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(EventName.SLA_BREACH, {"task_id": "t1", "assignee_id": "user-1"})

    alerts = service.get_alerts_for_user("user-1")
    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.SLA_BREACH


def test_sla_breach_event_without_assignee_is_ignored():
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(EventName.SLA_BREACH, {"task_id": "t1", "assignee_id": None})

    assert service.get_alerts_for_user("user-1") == []
