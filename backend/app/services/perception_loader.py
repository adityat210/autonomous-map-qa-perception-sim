from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import MapIssue, PerceptionFrame
from app.services.map_validation import _issue


def load_perception_sample(dataset_path: str) -> tuple[list[PerceptionFrame], list[MapIssue]]:
    root = Path(dataset_path)
    image_dir = root / "images"
    pc_dir = root / "pointcloud"
    timestamps_path = root / "timestamps.txt"
    calibration_path = root / "calibration.json"
    issues: list[MapIssue] = []
    timestamps: list[float] = []
    if timestamps_path.exists():
        for line in timestamps_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                timestamps.append(float(line.strip()))
    images = sorted(image_dir.glob("*.png")) + sorted(image_dir.glob("*.jpg")) + sorted(image_dir.glob("*.ppm"))
    frames: list[PerceptionFrame] = []
    for index, image_path in enumerate(images):
        pc_path = pc_dir / f"{image_path.stem}.bin"
        if not pc_path.exists():
            issues.append(
                _issue(
                    "missing_point_cloud",
                    "low",
                    f"point cloud is missing for frame {image_path.stem}",
                    "regenerate the sample point cloud or mark the frame as image-only",
                    node_id=image_path.stem,
                )
            )
        elif pc_path.stat().st_size == 0:
            issues.append(
                _issue(
                    "empty_point_cloud",
                    "medium",
                    f"point cloud file is empty for frame {image_path.stem}",
                    "drop the frame or rerun the point-cloud export step",
                    node_id=image_path.stem,
                )
            )
        frames.append(
            PerceptionFrame(
                frame_id=image_path.stem,
                image_path=str(image_path),
                timestamp=timestamps[index] if index < len(timestamps) else None,
                point_cloud_path=str(pc_path) if pc_path.exists() else None,
            )
        )
    if not images:
        issues.append(_issue("missing_frames", "high", "no image frames were found", "generate or download a sample driving sequence"))
    if timestamps and len(timestamps) != len(images):
        issues.append(
            _issue(
                "inconsistent_timestamps",
                "medium",
                "timestamp count does not match image frame count",
                "align image export and timestamp generation before running visual odometry",
            )
        )
    if calibration_path.exists():
        calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
        for field in ["fx", "fy", "cx", "cy"]:
            if field not in calibration or float(calibration[field]) <= 0:
                issues.append(
                    _issue(
                        "invalid_calibration",
                        "high",
                        f"calibration field {field} is missing or invalid",
                        "provide positive pinhole camera intrinsics before pose recovery",
                    )
                )
    return frames, issues
