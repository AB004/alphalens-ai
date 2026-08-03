from fastapi import HTTPException, status

from backend.database.session import SessionLocal
from backend.repositories.document_repository import get_document
from backend.repositories.report_repository import (
    create_report,
    get_report,
    update_report,
)
from backend.services.llm.gemini_service import gemini_service
from backend.utils.prompt_loader import load_prompt

def generate_document_report(
    document_id: int,
):
    db = SessionLocal()

    try:
        document = get_document(
            db,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        
        if document.status != "indexed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document must be indexed before analysis.",
            )

        if not document.clean_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Document contains no extracted text.",
            )

        MAX_ANALYSIS_CHARACTERS = 120000
        document_text = document.clean_text[:MAX_ANALYSIS_CHARACTERS]
        prompt = (
            load_prompt("document_analysis.txt")
            + "\n\nDOCUMENT:\n\n"
            + document_text
        )
          
        try:
            response = gemini_service.generate_json(prompt)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI analysis failed: {exc}",
            )
        report = get_report(db,document_id,)

        if report is None:
            report = create_report(
                db,
                document_id=document_id,
                executive_summary=response["executive_summary"],
                financial_metrics=response["financial_metrics"],
                swot=response["swot"],
                risks=response["risks"],
                opportunities=response["opportunities"],
            )
        else:
            report = update_report(
                db,
                report,
                executive_summary=response["executive_summary"],
                financial_metrics=response["financial_metrics"],
                swot=response["swot"],
                risks=response["risks"],
                opportunities=response["opportunities"],
            )
        return {
            "document_id": document_id,

            "executive_summary": report.executive_summary,

            "financial_metrics": report.financial_metrics,

            "swot": report.swot,

            "risks": report.risks,

            "opportunities": report.opportunities,
        }

    finally:
        db.close()

def fetch_document_report(document_id: int):
    db = SessionLocal()

    try:
        report = get_report(
            db=db,
            document_id=document_id,
        )

        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis report not found. Generate the report first.",
            )

        return {
            "document_id": report.document_id,
            "executive_summary": report.executive_summary,
            "financial_metrics": report.financial_metrics,
            "swot": report.swot,
            "risks": report.risks,
            "opportunities": report.opportunities,
        }

    finally:
        db.close()