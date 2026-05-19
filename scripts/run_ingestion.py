from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.map_ingestion import ingest_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--place", default="Isla Vista, California")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()
    payload, path = ingest_map(args.place, use_sample=args.sample)
    print({"nodes": len(payload["nodes"]), "edges": len(payload["edges"]), "path": str(path), "source": payload["source"]})


if __name__ == "__main__":
    main()
