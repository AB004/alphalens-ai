from fastapi import HTTPException, status

from backend.database.session import SessionLocal

from backend.repositories.report_repository import (
    get_report,
)

from backend.repositories.recommendation_repository import (
    get_recommendation,
    create_recommendation,
    update_recommendation,
)

from backend.services.llm.gemini_service import (
    gemini_service,
)

from backend.services.recommendation.financial_score import (
    FinancialScorer,
)

from backend.utils.prompt_loader import (
    load_prompt,
)


def _serialize_recommendation(recommendation):
    return {
        "document_id": recommendation.document_id,
        "score": recommendation.score,
        "recommendation": recommendation.recommendation,
        "confidence": recommendation.confidence,
        "reasoning": recommendation.reasoning,
    }


def generate_recommendation(document_id: int):
    db = SessionLocal()

    try:

        report = get_report(
            db,
            document_id,
        )

        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document analysis not found. Generate analysis first.",
            )

        report_data = {
            "executive_summary": report.executive_summary,
            "financial_metrics": report.financial_metrics,
            "swot": report.swot,
            "risks": report.risks,
            "opportunities": report.opportunities,
        }

        scorer = FinancialScorer(report_data)

        result = scorer.calculate()

        prompt = load_prompt(
            "recommendation.txt"
        )

        prompt = (
            prompt.replace(
                "{recommendation}",
                result["recommendation"],
            )
            .replace(
                "{score}",
                str(result["score"]),
            )
            .replace(
                "{confidence}",
                str(result["confidence"]),
            )
            .replace(
                "{reasons}",
                "\n".join(result["reasons"]),
            )
        )

        reasoning = gemini_service.generate_text(prompt)

        recommendation = get_recommendation(
            db,
            document_id,
        )

        if recommendation is None:

            recommendation = create_recommendation(
                db,
                document_id=document_id,
                score=result["score"],
                recommendation=result["recommendation"],
                confidence=result["confidence"],
                reasoning=reasoning,
            )

        else:

            recommendation = update_recommendation(
                db,
                recommendation,
                score=result["score"],
                recommendation=result["recommendation"],
                confidence=result["confidence"],
                reasoning=reasoning,
            )

        return _serialize_recommendation(
            recommendation
        )

    finally:
        db.close()


def fetch_recommendation(document_id: int):
    db = SessionLocal()

    try:

        recommendation = get_recommendation(
            db,
            document_id,
        )

        if recommendation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found.",
            )

        return _serialize_recommendation(
            recommendation
        )

    finally:
        db.close()