from __future__ import annotations

from fastapi import APIRouter

from app.api import state
from app.models.schemas import GraphStats, MapIngestRequest, MapIngestResponse
from app.services.graph_builder import graph_stats
from app.services.map_ingestion import ingest_map

router = APIRouter(prefix="/maps", tags=["maps"])


@router.post("/ingest", response_model=MapIngestResponse)
def ingest(request: MapIngestRequest) -> MapIngestResponse:
    payload, path = ingest_map(request.place_name, request.network_type, request.use_sample)
    state.LATEST_PAYLOAD = payload
    state.LATEST_MAP_PATH = str(path)
    return MapIngestResponse(
        place_name=payload["place_name"],
        source=payload["source"],
        node_count=len(payload["nodes"]),
        edge_count=len(payload["edges"]),
        output_path=str(path),
    )


@router.get("/graph-stats", response_model=GraphStats)
def get_graph_stats() -> GraphStats:
    payload = state.LATEST_PAYLOAD
    if payload is None:
        payload, path = ingest_map("Isla Vista, California", use_sample=True)
        state.LATEST_PAYLOAD = payload
        state.LATEST_MAP_PATH = str(path)
    return GraphStats(**graph_stats(payload))
