from __future__ import annotations

from storeops.shared.events import EventBus, EventName


def test_emit_calls_subscribed_handler_with_payload():
    bus = EventBus()
    received = []
    bus.subscribe(EventName.SLA_BREACH, received.append)

    bus.emit(EventName.SLA_BREACH, {"task_id": "t1"})

    assert received == [{"task_id": "t1"}]


def test_emit_with_no_subscribers_does_not_raise():
    bus = EventBus()
    bus.emit(EventName.PROGRAMME_CLOSED, {"store_id": "store-1"})


def test_multiple_handlers_all_receive_the_event():
    bus = EventBus()
    calls: list[str] = []
    bus.subscribe(EventName.SLA_BREACH, lambda _payload: calls.append("first"))
    bus.subscribe(EventName.SLA_BREACH, lambda _payload: calls.append("second"))

    bus.emit(EventName.SLA_BREACH, None)

    assert calls == ["first", "second"]


def test_regional_rollup_generated_event_name_value():
    assert EventName.REGIONAL_ROLLUP_GENERATED == "REGIONAL_ROLLUP_GENERATED"
