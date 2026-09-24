from __future__ import annotations

from typing import Any
from uuid import uuid4

from storeops.alerts.repository import AlertRepository, repository
from storeops.alerts.types import AlertType, Notification
from storeops.shared.events import EventBus, EventName


class AlertService:
    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    def get_alerts_for_user(self, user_id: str) -> list[Notification]:
        return self._repo.list_for_user(user_id)

    def register_event_handlers(self, bus: EventBus) -> None:
        bus.subscribe(EventName.SLA_BREACH, self._on_sla_breach)

    def _on_sla_breach(self, payload: Any) -> None:
        assignee_id = payload.get("assignee_id") if payload else None
        if assignee_id is None:
            return
        notification = Notification(
            id=str(uuid4()),
            user_id=assignee_id,
            alert_type=AlertType.SLA_BREACH,
            message=f"Task {payload.get('task_id')} breached its SLA",
        )
        self._repo.create(notification)


service = AlertService(repository)
