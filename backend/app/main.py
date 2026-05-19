from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_benchmarks import router as benchmarks_router
from app.api.routes_maps import router as maps_router
from app.api.routes_perception import router as perception_router
from app.api.routes_validation import router as validation_router
from app.core.config import settings
from app.models.schemas import HealthResponse

app = FastAPI(title=settings.app_name, version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(maps_router)
app.include_router(validation_router)
app.include_router(perception_router)
app.include_router(benchmarks_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version=settings.version)
