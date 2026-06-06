from __future__ import annotations

from app.services.perception_loader import load_perception_sample
from app.services.visual_odometry import run_visual_odometry


def test_perception_sample_loads_from_project_root_path():
    frames, issues = load_perception_sample("data/sample/perception")
    assert len(frames) == 4
    assert issues == []


def test_visual_odometry_reports_actual_frame_count():
    estimates, limitations, frame_count = run_visual_odometry("data/sample/perception")
    assert frame_count == 4
    assert len(estimates) <= 3
    assert any("not a full slam system" in item for item in limitations)
