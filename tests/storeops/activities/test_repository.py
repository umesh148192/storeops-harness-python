from __future__ import annotations

from storeops.activities.repository import ActivityRepository
from storeops.activities.types import Task, TaskStatus


def test_create_assigns_id_and_get_roundtrips():
    repo = ActivityRepository()
    task = Task(id="", title="Restock aisle 4")

    created = repo.create(task)

    assert created.id
    assert repo.get(created.id) == created


def test_list_filters_by_programme_and_status():
    repo = ActivityRepository()
    repo.create(Task(id="", title="A", programme_id="p1", status=TaskStatus.TODO))
    repo.create(Task(id="", title="B", programme_id="p2", status=TaskStatus.DONE))

    assert len(repo.list(programme_id="p1")) == 1
    assert len(repo.list(status=TaskStatus.DONE)) == 1
    assert len(repo.list()) == 2


def test_update_and_delete():
    repo = ActivityRepository()
    created = repo.create(Task(id="", title="A"))

    updated = repo.update(created.id, status=TaskStatus.IN_PROGRESS)
    assert updated is not None
    assert updated.status == TaskStatus.IN_PROGRESS

    assert repo.delete(created.id) is True
    assert repo.get(created.id) is None
    assert repo.delete(created.id) is False


def test_update_missing_returns_none():
    repo = ActivityRepository()
    assert repo.update("missing", status=TaskStatus.DONE) is None
