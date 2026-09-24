from __future__ import annotations


def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_not_in_openapi_schema(client):
    schema = client.get("/openapi.json").json()

    assert "/health" not in schema["paths"]
