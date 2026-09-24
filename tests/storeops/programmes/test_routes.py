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
