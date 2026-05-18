from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.models.schemas import MapIssue


def save_validation_results(issues: list[MapIssue]) -> str:
    if settings.database_url:
        try:
            import psycopg

            with psycopg.connect(settings.database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        create table if not exists validation_issues (
                            issue_id text primary key,
                            issue_type text not null,
                            severity text not null,
                            explanation text not null,
                            recommended_action text not null,
                            geometry jsonb
                        )
                        """
                    )
                    for issue in issues:
                        cursor.execute(
                            """
                            insert into validation_issues
                            (issue_id, issue_type, severity, explanation, recommended_action, geometry)
                            values (%s, %s, %s, %s, %s, %s)
                            on conflict (issue_id) do update set
                            issue_type = excluded.issue_type,
                            severity = excluded.severity,
                            explanation = excluded.explanation,
                            recommended_action = excluded.recommended_action,
                            geometry = excluded.geometry
                            """,
                            (
                                issue.issue_id,
                                issue.issue_type,
                                issue.severity,
                                issue.explanation,
                                issue.recommended_action,
                                json.dumps(issue.geometry) if issue.geometry else None,
                            ),
                        )
            return "postgis-compatible-postgres"
        except Exception:
            pass
    output_dir = settings.data_dir / "generated_map"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "validation_results.json"
    path.write_text(json.dumps([issue.model_dump() for issue in issues], indent=2), encoding="utf-8")
    return str(path)
