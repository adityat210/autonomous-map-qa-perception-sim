from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validate_endpoint_returns_issues():
    client = TestClient(app)
    response = client.post("/maps/validate", json={"place_name": "Isla Vista, California"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["issue_count"] > 0
    assert "summary" in payload
