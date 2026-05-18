from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.api import state
from app.models.schemas import SummaryResponse, ValidationRequest, ValidationResponse
from app.services.ai_summary import summarize_with_optional_llm
from app.services.graph_builder import load_graph_payload
from app.services.map_ingestion import ingest_map
from app.services.map_validation import summarize_issues, validate_map_payload
from app.services.result_store import save_validation_results

router = APIRouter(prefix="/maps", tags=["validation"])


@router.post("/validate", response_model=ValidationResponse)
def validate(request: ValidationRequest) -> ValidationResponse:
    if request.map_path:
        payload = load_graph_payload(request.map_path)
    elif state.LATEST_PAYLOAD is not None:
        payload = state.LATEST_PAYLOAD
    else:
        payload, path = ingest_map(request.place_name or "Isla Vista, California", use_sample=True)
        state.LATEST_MAP_PATH = str(path)
    state.LATEST_PAYLOAD = payload
    issues = validate_map_payload(payload)
    state.LATEST_ISSUES = issues
    save_validation_results(issues)
    return ValidationResponse(generated_at=datetime.now(timezone.utc), issue_count=len(issues), issues=issues, summary=summarize_issues(issues))


@router.get("/issues")
def get_issues():
    return {"issues": state.LATEST_ISSUES, "issue_count": len(state.LATEST_ISSUES)}


@router.get("/summary", response_model=SummaryResponse)
def get_summary() -> SummaryResponse:
    issues = state.LATEST_ISSUES
    text = summarize_with_optional_llm(issues)
    return SummaryResponse(
        text=text,
        issue_count=len(issues),
        high_severity_count=sum(1 for issue in issues if issue.severity == "high"),
    )
