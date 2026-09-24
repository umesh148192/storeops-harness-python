from __future__ import annotations

from uuid import uuid4

from storeops.alerts.types import Notification


class AlertRepository:
    def __init__(self) -> None:
        self._notifications: dict[str, Notification] = {}

    def reset(self) -> None:
        self._notifications.clear()

    def list_for_user(self, user_id: str) -> list[Notification]:
        return [n for n in self._notifications.values() if n.user_id == user_id]

    def create(self, notification: Notification) -> Notification:
        notification_id = notification.id or str(uuid4())
        stored = notification.model_copy(update={"id": notification_id})
        self._notifications[notification_id] = stored
        return stored


repository = AlertRepository()
