from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "autonomous map qa & perception simulation"
    version: str = "0.1.0"
    data_dir: Path = Path(os.getenv("MAP_QA_DATA_DIR", "data/sample"))
    database_url: str | None = os.getenv("DATABASE_URL")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
