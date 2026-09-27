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


def test_bulk_status_route_updates_valid_tasks_and_reports_failures(client):
    app = client.app
    original = app.dependency_overrides.get(__import__("storeops.shared.deps", fromlist=["get_current_user"]).get_current_user)
    app.dependency_overrides[__import__("storeops.shared.deps", fromlist=["get_current_user"]).get_current_user] = lambda: __import__("storeops.shared.deps", fromlist=["UserContext"]).UserContext(
        user_id="associate-1",
        store_id="store-1",
        role=__import__("storeops.shared.entities", fromlist=["StaffRole"]).StaffRole.ASSOCIATE,
    )

    try:
        owned = client.post("/api/activities", json={"title": "Restock freezer", "assignee_id": "associate-1"}).json()
        blocked = client.post("/api/activities", json={"title": "Audit sign-off", "assignee_id": "other-user"}).json()

        response = client.patch(
            "/api/activities/bulk-status",
            json={
                "updates": [
                    {"task_id": owned["id"], "status": "DONE", "note": "Completed"},
                    {"task_id": blocked["id"], "status": "BLOCKED", "note": "Waiting on supplier"},
                ]
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert [task["id"] for task in payload["updated"]] == [owned["id"]]
        assert payload["failed"][0]["task_id"] == blocked["id"]
        assert payload["failed"][0]["code"] == "FORBIDDEN"
    finally:
        if original is None:
            app.dependency_overrides.clear()
        else:
            app.dependency_overrides[__import__("storeops.shared.deps", fromlist=["get_current_user"]).get_current_user] = original
