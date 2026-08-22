from typing import Optional

from sqlalchemy.orm import Session

from backend.models.recommendation import Recommendation


def get_recommendation(
    db: Session,
    document_id: int,
) -> Optional[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.document_id == document_id
        )
        .first()
    )


def create_recommendation(
    db: Session,
    *,
    document_id: int,
    score: float,
    recommendation: str,
    confidence: float,
    reasoning: str,
) -> Recommendation:
    recommendation_record = Recommendation(
        document_id=document_id,
        score=score,
        recommendation=recommendation,
        confidence=confidence,
        reasoning=reasoning,
    )

    db.add(recommendation_record)
    db.commit()
    db.refresh(recommendation_record)

    return recommendation_record


def update_recommendation(
    db: Session,
    recommendation_record: Recommendation,
    *,
    score: float,
    recommendation: str,
    confidence: float,
    reasoning: str,
) -> Recommendation:
    recommendation_record.score = score
    recommendation_record.recommendation = recommendation
    recommendation_record.confidence = confidence
    recommendation_record.reasoning = reasoning

    db.commit()
    db.refresh(recommendation_record)

    return recommendation_record


def delete_recommendation(
    db: Session,
    recommendation_record: Recommendation,
) -> None:
    db.delete(recommendation_record)
    db.commit()

def recommendation_exists(
    db: Session,
    document_id: int,
) -> bool:
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.document_id == document_id
        )
        .first()
        is not None
    )