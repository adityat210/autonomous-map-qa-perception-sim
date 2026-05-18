from __future__ import annotations

import time
from datetime import datetime, timezone

from app.models.schemas import BenchmarkResult

LATEST_BENCHMARK: BenchmarkResult | None = None


def _cpu_fallback(size: int, iterations: int) -> float:
    start = time.perf_counter()
    data = [[float((row * col) % 255) for col in range(32)] for row in range(32)]
    for _ in range(iterations):
        total = 0.0
        for row in data:
            for value in row:
                total += (value / 255.0) ** 2
        if total < 0:
            raise RuntimeError("unreachable benchmark guard")
    return (time.perf_counter() - start) * 1000


def run_benchmark(size: int = 512, iterations: int = 10) -> BenchmarkResult:
    global LATEST_BENCHMARK
    try:
        import torch
    except Exception:
        result = BenchmarkResult(
            device="cpu",
            workload="python fallback tensor-style normalization",
            size=size,
            iterations=iterations,
            cpu_ms=round(_cpu_fallback(size, iterations), 3),
            created_at=datetime.now(timezone.utc),
        )
        LATEST_BENCHMARK = result
        return result
    cpu_tensor = torch.rand((size, size), device="cpu")
    start = time.perf_counter()
    for _ in range(iterations):
        centered = cpu_tensor - cpu_tensor.mean()
        _ = torch.sqrt(centered.square() + 1e-6).mean().item()
    cpu_ms = (time.perf_counter() - start) * 1000
    gpu_ms = None
    speedup = None
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
        cuda_tensor = cpu_tensor.to("cuda")
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(iterations):
            centered = cuda_tensor - cuda_tensor.mean()
            _ = torch.sqrt(centered.square() + 1e-6).mean()
        torch.cuda.synchronize()
        gpu_ms = (time.perf_counter() - start) * 1000
        speedup = cpu_ms / gpu_ms if gpu_ms and gpu_ms > 0 else None
    result = BenchmarkResult(
        device=device,
        workload="image tensor normalization and distance-style reduction",
        size=size,
        iterations=iterations,
        cpu_ms=round(cpu_ms, 3),
        gpu_ms=round(gpu_ms, 3) if gpu_ms is not None else None,
        speedup=round(speedup, 3) if speedup is not None else None,
        created_at=datetime.now(timezone.utc),
    )
    LATEST_BENCHMARK = result
    return result


def latest_benchmark() -> BenchmarkResult | None:
    return LATEST_BENCHMARK
