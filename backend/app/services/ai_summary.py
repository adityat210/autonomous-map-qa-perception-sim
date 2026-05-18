from __future__ import annotations

from app.core.config import settings
from app.models.schemas import MapIssue


def local_summary(issues: list[MapIssue]) -> str:
    high = [issue for issue in issues if issue.severity == "high"]
    common_types: dict[str, int] = {}
    for issue in issues:
        common_types[issue.issue_type] = common_types.get(issue.issue_type, 0) + 1
    dominant = sorted(common_types.items(), key=lambda item: item[1], reverse=True)[:3]
    if not issues:
        return "no map qa issues were found in the latest validation run."
    impact = "high-severity issues can affect route connectivity, simulation coverage, or map-matching reliability."
    actions = "start with disconnected components and invalid geometries, then review duplicate edges and metadata gaps."
    return f"{len(issues)} issues were found; {len(high)} are high severity. common issue types: {dominant}. {impact} {actions}"


def summarize_with_optional_llm(issues: list[MapIssue]) -> str:
    if not settings.openai_api_key:
        return local_summary(issues)
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        issue_lines = "\n".join(f"- {i.severity}: {i.issue_type}: {i.explanation}" for i in issues[:25])
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=(
                "summarize these map qa validation issues for an autonomous systems engineer. "
                "focus on impact and next actions.\n"
                f"{issue_lines}"
            ),
        )
        return response.output_text
    except Exception:
        return local_summary(issues)
