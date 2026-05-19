from __future__ import annotations

from app.services.gpu_benchmark import run_benchmark


def test_gpu_benchmark_cpu_fallback_runs():
    result = run_benchmark(size=64, iterations=1)
    assert result.cpu_ms >= 0
    assert result.device in {"cpu", "cuda"}
    if result.device == "cpu":
        assert result.gpu_ms is None
