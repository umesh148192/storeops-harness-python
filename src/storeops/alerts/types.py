from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"


class NotificationStatus(str, Enum):
    UNREAD = "UNREAD"
    READ = "READ"


class AlertType(str, Enum):
    INVENTORY = "INVENTORY"
    SLA_BREACH = "SLA_BREACH"
    SHIFT_HANDOVER = "SHIFT_HANDOVER"
    ESCALATION = "ESCALATION"


class Notification(BaseModel):
    id: str
    user_id: str
    alert_type: AlertType
    channel: NotificationChannel = NotificationChannel.IN_APP
    status: NotificationStatus = NotificationStatus.UNREAD
    message: str
