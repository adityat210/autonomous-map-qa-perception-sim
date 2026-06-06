from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


class Settings(BaseModel):
    app_name: str = "autonomous map qa & perception simulation"
    version: str = "0.1.0"
    data_dir: Path = _resolve_project_path(os.getenv("MAP_QA_DATA_DIR", "data/sample"))
    database_url: str | None = os.getenv("DATABASE_URL")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()


def resolve_project_path(value: str | Path) -> Path:
    return _resolve_project_path(value)
