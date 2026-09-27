from __future__ import annotations

from storeops.alerts.service import service
from storeops.alerts.types import AlertType
from storeops.programmes.service import service as programmes_service
from storeops.programmes.types import ProjectCreate, ProjectMemberCreate, ProjectRole
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


def test_sla_breach_notifies_department_lead_when_resolvable():
    project = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    programmes_service.add_member(
        project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.DEPARTMENT_LEAD)
    )
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(
        EventName.SLA_BREACH,
        {"task_id": "t1", "assignee_id": "someone-else", "programme_id": project.id},
    )

    lead_alerts = service.get_alerts_for_user("stub-user-1")
    assert len(lead_alerts) == 1
    assert lead_alerts[0].alert_type == AlertType.SLA_BREACH
    assert service.get_alerts_for_user("someone-else") == []


def test_sla_breach_falls_back_to_assignee_when_no_department_lead_resolvable():
    project = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(
        EventName.SLA_BREACH,
        {"task_id": "t1", "assignee_id": "user-1", "programme_id": project.id},
    )

    alerts = service.get_alerts_for_user("user-1")
    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.SLA_BREACH


def test_sla_escalation_notifies_store_manager_when_resolvable():
    project = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    programmes_service.add_member(
        project.id, ProjectMemberCreate(user_id="stub-user-1", role=ProjectRole.STORE_MANAGER)
    )
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(
        EventName.SLA_ESCALATION,
        {"task_id": "t1", "assignee_id": "someone-else", "programme_id": project.id},
    )

    manager_alerts = service.get_alerts_for_user("stub-user-1")
    assert len(manager_alerts) == 1
    assert manager_alerts[0].alert_type == AlertType.ESCALATION


def test_sla_escalation_is_noop_when_no_store_manager_resolvable():
    project = programmes_service.create_programme(ProjectCreate(name="Refit"), store_id="store-1")
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(
        EventName.SLA_ESCALATION,
        {"task_id": "t1", "assignee_id": "user-1", "programme_id": project.id},
    )

    assert service.get_alerts_for_user("user-1") == []


def test_sla_escalation_is_noop_when_programme_missing():
    bus = EventBus()
    service.register_event_handlers(bus)

    bus.emit(
        EventName.SLA_ESCALATION,
        {"task_id": "t1", "assignee_id": "user-1", "programme_id": "missing"},
    )

    assert service.get_alerts_for_user("user-1") == []
