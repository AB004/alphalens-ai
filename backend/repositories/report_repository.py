from typing import Optional

from sqlalchemy.orm import Session

from backend.models.report import DocumentReport


def get_report(
    db: Session,
    document_id: int,
) -> Optional[DocumentReport]:
    return (
        db.query(DocumentReport)
        .filter(DocumentReport.document_id == document_id)
        .first()
    )


def create_report(
    db: Session,
    *,
    document_id: int,
    executive_summary,
    financial_metrics,
    swot,
    risks,
    opportunities,
) -> DocumentReport:

    report = DocumentReport(
        document_id=document_id,
        executive_summary=executive_summary,
        financial_metrics=financial_metrics,
        swot=swot,
        risks=risks,
        opportunities=opportunities,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def update_report(
    db: Session,
    report: DocumentReport,
    *,
    executive_summary,
    financial_metrics,
    swot,
    risks,
    opportunities,
) -> DocumentReport:

    report.executive_summary = executive_summary
    report.financial_metrics = financial_metrics
    report.swot = swot
    report.risks = risks
    report.opportunities = opportunities

    db.commit()
    db.refresh(report)

    return report


def delete_report(
    db: Session,
    report: DocumentReport,
) -> None:

    db.delete(report)
    db.commit()