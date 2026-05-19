from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.graph_builder import load_graph_payload
from app.services.map_ingestion import ingest_map
from app.services.map_validation import summarize_issues, validate_map_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-path")
    args = parser.parse_args()
    payload = load_graph_payload(args.map_path) if args.map_path else ingest_map("Isla Vista, California", use_sample=True)[0]
    issues = validate_map_payload(payload)
    print({"issue_count": len(issues), "summary": summarize_issues(issues)})
    for issue in issues:
        print(issue.model_dump())


if __name__ == "__main__":
    main()
