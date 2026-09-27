from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Any, Callable

EventHandler = Callable[[Any], None]


class EventName(str, Enum):
    SLA_BREACH = "SLA_BREACH"
    SLA_ESCALATION = "SLA_ESCALATION"
    PROGRAMME_CLOSED = "PROGRAMME_CLOSED"


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, payload: Any = None) -> None:
        for handler in self._handlers.get(event_name, []):
            handler(payload)


event_bus = EventBus()
