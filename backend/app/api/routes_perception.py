from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import PerceptionLoadRequest, PerceptionLoadResponse, VisualOdometryRequest, VisualOdometryResponse
from app.services.perception_loader import load_perception_sample
from app.services.visual_odometry import run_visual_odometry

router = APIRouter(prefix="/perception", tags=["perception"])


@router.post("/load-sample", response_model=PerceptionLoadResponse)
def load_sample(request: PerceptionLoadRequest) -> PerceptionLoadResponse:
    frames, issues = load_perception_sample(request.dataset_path)
    return PerceptionLoadResponse(dataset_path=request.dataset_path, frame_count=len(frames), frames=frames, issues=issues)


@router.post("/visual-odometry", response_model=VisualOdometryResponse)
def visual_odometry(request: VisualOdometryRequest) -> VisualOdometryResponse:
    estimates, limitations, frame_count = run_visual_odometry(request.dataset_path)
    return VisualOdometryResponse(frame_count=frame_count, estimates=estimates, limitations=limitations)
