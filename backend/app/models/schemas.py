from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high"]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class MapIngestRequest(BaseModel):
    place_name: str = Field(default="Isla Vista, California")
    network_type: str = Field(default="drive")
    use_sample: bool = Field(default=False)


class MapIngestResponse(BaseModel):
    place_name: str
    source: str
    node_count: int
    edge_count: int
    output_path: str


class ValidationRequest(BaseModel):
    map_path: str | None = None
    place_name: str | None = None


class MapIssue(BaseModel):
    issue_id: str
    issue_type: str
    severity: Severity
    explanation: str
    recommended_action: str
    node_id: str | None = None
    edge_id: str | None = None
    geometry: dict[str, Any] | None = None


class ValidationResponse(BaseModel):
    generated_at: datetime
    issue_count: int
    issues: list[MapIssue]
    summary: dict[str, Any]


class GraphStats(BaseModel):
    node_count: int
    edge_count: int
    connected_components: int
    dead_end_count: int
    average_degree: float


class PerceptionLoadRequest(BaseModel):
    dataset_path: str = Field(default="data/sample/perception")


class PerceptionFrame(BaseModel):
    frame_id: str
    image_path: str
    timestamp: float | None = None
    point_cloud_path: str | None = None


class PerceptionLoadResponse(BaseModel):
    dataset_path: str
    frame_count: int
    frames: list[PerceptionFrame]
    issues: list[MapIssue]


class VisualOdometryRequest(BaseModel):
    dataset_path: str = Field(default="data/sample/perception")


class MotionEstimate(BaseModel):
    from_frame: str
    to_frame: str
    match_count: int
    inlier_count: int
    dx: float
    dy: float
    dz: float


class VisualOdometryResponse(BaseModel):
    frame_count: int
    estimates: list[MotionEstimate]
    limitations: list[str]


class BenchmarkRequest(BaseModel):
    size: int = Field(default=512, ge=64, le=4096)
    iterations: int = Field(default=10, ge=1, le=200)


class BenchmarkResult(BaseModel):
    device: str
    workload: str
    size: int
    iterations: int
    cpu_ms: float
    gpu_ms: float | None = None
    speedup: float | None = None
    created_at: datetime


class SummaryResponse(BaseModel):
    text: str
    issue_count: int
    high_severity_count: int
