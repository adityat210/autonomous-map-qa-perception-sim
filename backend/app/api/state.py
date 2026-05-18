from __future__ import annotations

from app.models.schemas import MapIssue

LATEST_MAP_PATH: str | None = None
LATEST_ISSUES: list[MapIssue] = []
LATEST_PAYLOAD: dict | None = None
