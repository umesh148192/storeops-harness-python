from __future__ import annotations


def test_create_and_list_programmes(client):
    response = client.post("/api/programmes", json={"name": "Seasonal rollout"})
    assert response.status_code == 201
    created = response.json()
    assert created["store_id"] == "store-1"

    response = client.get("/api/programmes")
    assert response.status_code == 200
    assert any(p["id"] == created["id"] for p in response.json())


def test_add_member(client):
    project = client.post("/api/programmes", json={"name": "Refit"}).json()

    response = client.post(
        f"/api/programmes/{project['id']}/members",
        json={"user_id": "stub-user-1", "role": "ASSOCIATE"},
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == "stub-user-1"


def test_add_member_unknown_user_returns_404(client):
    project = client.post("/api/programmes", json={"name": "Refit"}).json()

    response = client.post(
        f"/api/programmes/{project['id']}/members",
        json={"user_id": "unknown-user", "role": "ASSOCIATE"},
    )

    assert response.status_code == 404


def test_clone_template_route_returns_201_with_planogram_tasks(client):
    project = client.post("/api/programmes", json={"name": "Refit"}).json()

    response = client.post(f"/api/programmes/{project['id']}/templates")

    assert response.status_code == 201
    created = response.json()
    assert len(created) == 3
    assert all(task["category"] == "PLANOGRAM" for task in created)
    assert all(task["programme_id"] == project["id"] for task in created)


def test_clone_template_route_missing_programme_returns_404(client):
    response = client.post("/api/programmes/does-not-exist/templates")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
