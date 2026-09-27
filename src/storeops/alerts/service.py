from __future__ import annotations

from typing import Any
from uuid import uuid4

from storeops.alerts.repository import AlertRepository, repository
from storeops.alerts.types import AlertType, Notification
from storeops.programmes.service import service as programmes_service
from storeops.shared.errors import NotFoundError
from storeops.shared.events import EventBus, EventName


class AlertService:
    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    def get_alerts_for_user(self, user_id: str) -> list[Notification]:
        return self._repo.list_for_user(user_id)

    def register_event_handlers(self, bus: EventBus) -> None:
        bus.subscribe(EventName.SLA_BREACH, self._on_sla_breach)
        bus.subscribe(EventName.SLA_ESCALATION, self._on_sla_escalation)

    def _on_sla_breach(self, payload: Any) -> None:
        if not payload:
            return
        recipient_id = self._resolve_department_lead(payload.get("programme_id"))
        if recipient_id is None:
            recipient_id = payload.get("assignee_id")
        if recipient_id is None:
            return

        notification = Notification(
            id=str(uuid4()),
            user_id=recipient_id,
            alert_type=AlertType.SLA_BREACH,
            message=f"Task {payload.get('task_id')} breached its SLA",
        )
        self._repo.create(notification)

    def _on_sla_escalation(self, payload: Any) -> None:
        if not payload:
            return
        recipient_id = self._resolve_store_manager(payload.get("programme_id"))
        if recipient_id is None:
            return

        notification = Notification(
            id=str(uuid4()),
            user_id=recipient_id,
            alert_type=AlertType.ESCALATION,
            message=f"Task {payload.get('task_id')} escalated after grace period",
        )
        self._repo.create(notification)

    def _resolve_department_lead(self, programme_id: str | None) -> str | None:
        if programme_id is None:
            return None
        try:
            leads = programmes_service.list_department_leads(programme_id)
        except NotFoundError:
            return None
        return leads[0].user_id if leads else None

    def _resolve_store_manager(self, programme_id: str | None) -> str | None:
        if programme_id is None:
            return None
        try:
            managers = programmes_service.list_store_managers(programme_id)
        except NotFoundError:
            return None
        return managers[0].user_id if managers else None


service = AlertService(repository)
