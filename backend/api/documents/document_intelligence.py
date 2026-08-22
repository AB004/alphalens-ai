from fastapi import APIRouter

from backend.schemas.report import ReportResponse
from backend.services.document_intelligence.analysis_service import (
    generate_document_report,
    fetch_document_report
)

router = APIRouter()

@router.post(
    "/{document_id}/analysis",
    response_model=ReportResponse,
)
def analyze_document(document_id: int):
    return generate_document_report(document_id)

@router.get(
    "/{document_id}/analysis",
    response_model=ReportResponse,
)
def get_analysis(document_id: int):
    return fetch_document_report(document_id)