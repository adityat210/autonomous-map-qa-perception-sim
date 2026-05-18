from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import MotionEstimate


def _fallback_estimates(image_paths: list[Path]) -> list[MotionEstimate]:
    return [
        MotionEstimate(
            from_frame=image_paths[i].stem,
            to_frame=image_paths[i + 1].stem,
            match_count=0,
            inlier_count=0,
            dx=0.0,
            dy=0.0,
            dz=0.0,
        )
        for i in range(max(0, len(image_paths) - 1))
    ]


def run_visual_odometry(dataset_path: str) -> tuple[list[MotionEstimate], list[str]]:
    root = Path(dataset_path)
    image_paths = sorted((root / "images").glob("*.png")) + sorted((root / "images").glob("*.jpg")) + sorted((root / "images").glob("*.ppm"))
    limitations = [
        "this module estimates frame-to-frame motion for qa and simulation inspection only.",
        "it is not a full slam system and does not perform loop closure or map optimization.",
    ]
    if len(image_paths) < 2:
        return [], limitations + ["at least two frames are required."]
    try:
        import cv2
        import numpy as np
    except Exception:
        return _fallback_estimates(image_paths), limitations + ["opencv is unavailable, so zero-motion placeholders were returned."]
    calibration_path = root / "calibration.json"
    intrinsics = None
    if calibration_path.exists():
        calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
        intrinsics = np.array(
            [
                [float(calibration.get("fx", 0)), 0, float(calibration.get("cx", 0))],
                [0, float(calibration.get("fy", 0)), float(calibration.get("cy", 0))],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )
    orb = cv2.ORB_create(nfeatures=1200)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    estimates: list[MotionEstimate] = []
    for left_path, right_path in zip(image_paths, image_paths[1:]):
        left = cv2.imread(str(left_path), cv2.IMREAD_GRAYSCALE)
        right = cv2.imread(str(right_path), cv2.IMREAD_GRAYSCALE)
        if left is None or right is None:
            continue
        kp1, des1 = orb.detectAndCompute(left, None)
        kp2, des2 = orb.detectAndCompute(right, None)
        if des1 is None or des2 is None:
            estimates.append(MotionEstimate(from_frame=left_path.stem, to_frame=right_path.stem, match_count=0, inlier_count=0, dx=0, dy=0, dz=0))
            continue
        matches = sorted(matcher.match(des1, des2), key=lambda match: match.distance)[:200]
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
        dx = dy = dz = 0.0
        inliers = 0
        if len(matches) >= 8 and intrinsics is not None and intrinsics[0, 0] > 0:
            essential, mask = cv2.findEssentialMat(pts1, pts2, intrinsics, method=cv2.RANSAC, prob=0.999, threshold=1.0)
            if essential is not None:
                _, _, translation, pose_mask = cv2.recoverPose(essential, pts1, pts2, intrinsics)
                dx, dy, dz = [float(value) for value in translation.ravel()]
                inliers = int(pose_mask.sum() / 255) if pose_mask is not None else 0
        elif len(matches) >= 4:
            _, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)
            inliers = int(mask.sum()) if mask is not None else 0
            if len(pts1) and len(pts2):
                delta = pts2.mean(axis=0) - pts1.mean(axis=0)
                dx, dy = float(delta[0]), float(delta[1])
        estimates.append(
            MotionEstimate(
                from_frame=left_path.stem,
                to_frame=right_path.stem,
                match_count=len(matches),
                inlier_count=inliers,
                dx=round(dx, 4),
                dy=round(dy, 4),
                dz=round(dz, 4),
            )
        )
    return estimates, limitations
