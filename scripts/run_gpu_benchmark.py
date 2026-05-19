from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.gpu_benchmark import run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()
    print(run_benchmark(args.size, args.iterations).model_dump())


if __name__ == "__main__":
    main()
