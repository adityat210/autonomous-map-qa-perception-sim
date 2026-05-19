from __future__ import annotations

from app.services.map_ingestion import generate_sample_map
from app.services.map_validation import validate_map_payload


def test_disconnected_graph_detection():
    issues = validate_map_payload(generate_sample_map())
    issue_types = {issue.issue_type for issue in issues}
    assert "disconnected_components" in issue_types


def test_duplicate_edge_detection():
    issues = validate_map_payload(generate_sample_map())
    duplicates = [issue for issue in issues if issue.issue_type == "duplicate_edge"]
    assert duplicates
    assert duplicates[0].severity == "medium"


def test_geometry_and_metadata_validation():
    payload = {
        "nodes": [{"id": "a", "lat": 0, "lon": 0}, {"id": "b", "lat": 0, "lon": 0.00001}],
        "edges": [{"u": "a", "v": "b", "key": 0, "length": 1, "geometry": None, "highway": "", "maxspeed": ""}],
    }
    issues = validate_map_payload(payload)
    types = {issue.issue_type for issue in issues}
    assert "invalid_geometry" in types
    assert "missing_road_classification" in types
    assert "missing_speed_metadata" in types
    assert any(issue.severity == "high" for issue in issues)
