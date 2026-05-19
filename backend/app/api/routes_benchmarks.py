from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import BenchmarkRequest, BenchmarkResult
from app.services.gpu_benchmark import latest_benchmark, run_benchmark

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/gpu", response_model=BenchmarkResult)
def gpu_benchmark(request: BenchmarkRequest) -> BenchmarkResult:
    return run_benchmark(request.size, request.iterations)


@router.get("/latest")
def latest():
    result = latest_benchmark()
    return result or {"message": "no benchmark has been run yet"}
