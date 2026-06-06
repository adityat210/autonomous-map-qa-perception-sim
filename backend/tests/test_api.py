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


def test_perception_api_loads_committed_sample_data():
    client = TestClient(app)
    response = client.post("/perception/load-sample", json={"dataset_path": "data/sample/perception"})
    assert response.status_code == 200
    assert response.json()["frame_count"] == 4
