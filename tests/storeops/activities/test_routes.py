from __future__ import annotations


def test_create_and_list_activities(client):
    response = client.post("/api/activities", json={"title": "Restock aisle 4"})
    assert response.status_code == 201
    created = response.json()

    response = client.get("/api/activities")
    assert response.status_code == 200
    assert any(task["id"] == created["id"] for task in response.json())


def test_get_activity_by_id(client):
    created = client.post("/api/activities", json={"title": "Planogram reset"}).json()

    response = client.get(f"/api/activities/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Planogram reset"


def test_get_activity_missing_returns_404(client):
    response = client.get("/api/activities/does-not-exist")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_patch_activity_updates_fields(client):
    created = client.post("/api/activities", json={"title": "Compliance check"}).json()

    response = client.patch(f"/api/activities/{created['id']}", json={"status": "IN_PROGRESS"})

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"


def test_delete_activity_by_store_manager(client):
    created = client.post("/api/activities", json={"title": "Audit"}).json()

    response = client.delete(f"/api/activities/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/activities/{created['id']}").status_code == 404
