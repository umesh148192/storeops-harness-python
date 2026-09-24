from __future__ import annotations

from storeops.alerts.repository import AlertRepository
from storeops.alerts.types import AlertType, Notification


def test_create_and_list_for_user():
    repo = AlertRepository()
    repo.create(Notification(id="", user_id="user-1", alert_type=AlertType.INVENTORY, message="low stock"))
    repo.create(Notification(id="", user_id="user-2", alert_type=AlertType.INVENTORY, message="low stock"))

    assert len(repo.list_for_user("user-1")) == 1
