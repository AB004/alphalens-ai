from sqlalchemy.orm import Session

from backend.models.market_recommendation import (
    MarketRecommendation,
)


def create_market_recommendation(
    db: Session,
    company_id: int,
    recommendation: str,
    score: float,
    confidence: float,
    financial_score: float,
    sentiment_score: float,
    financial_reasoning: str | None = None,
    sentiment_reasoning: str | None = None,
    overall_reasoning: str | None = None,
    confidence_reasoning: str | None = None,
    sentiment_limit: int = 100,
    sentiment_provider: str | None = None,
    model_version: str = "v1",
):
    """
    Create a market recommendation for a company.
    """

    result = MarketRecommendation(
        company_id=company_id,
        recommendation=recommendation,
        score=score,
        confidence=confidence,
        financial_score=financial_score,
        sentiment_score=sentiment_score,
        financial_reasoning=financial_reasoning,
        sentiment_reasoning=sentiment_reasoning,
        overall_reasoning=overall_reasoning,
        confidence_reasoning=confidence_reasoning,
        model_version=model_version,
        sentiment_limit=sentiment_limit,
        sentiment_provider=sentiment_provider,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result


def get_market_recommendation_by_id(
    db: Session,
    recommendation_id: int,
):
    """
    Retrieve a market recommendation by ID.
    """

    return (
        db.query(MarketRecommendation)
        .filter(
            MarketRecommendation.id
            == recommendation_id,
        )
        .first()
    )


def get_latest_market_recommendation(
    db: Session,
    company_id: int,
):
    """
    Return the latest market recommendation
    for a company.
    """

    return (
        db.query(MarketRecommendation)
        .filter(
            MarketRecommendation.company_id
            == company_id,
        )
        .order_by(
            MarketRecommendation.created_at.desc(),
        )
        .first()
    )


def list_market_recommendations(
    db: Session,
    company_id: int,
    skip: int = 0,
    limit: int = 20,
):
    """
    Return market recommendation history
    for a company.
    """

    return (
        db.query(MarketRecommendation)
        .filter(
            MarketRecommendation.company_id
            == company_id,
        )
        .order_by(
            MarketRecommendation.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_market_recommendation(
    db: Session,
    recommendation: MarketRecommendation,
    recommendation_value: str,
    score: float,
    confidence: float,
    financial_score: float,
    sentiment_score: float,
    financial_reasoning: str | None = None,
    sentiment_reasoning: str | None = None,
    overall_reasoning: str | None = None,
    confidence_reasoning: str | None = None,
    sentiment_limit: int = 100,
    sentiment_provider: str | None = None,
    model_version: str = "v1",
):
    """
    Update an existing market recommendation.
    """

    recommendation.recommendation = (
        recommendation_value
    )

    recommendation.score = score
    recommendation.confidence = confidence

    recommendation.financial_score = (
        financial_score
    )

    recommendation.sentiment_score = (
        sentiment_score
    )

    recommendation.financial_reasoning = (
        financial_reasoning
    )

    recommendation.sentiment_reasoning = (
        sentiment_reasoning
    )

    recommendation.overall_reasoning = (
        overall_reasoning
    )

    recommendation.confidence_reasoning = (
        confidence_reasoning
    )

    recommendation.model_version = (
        model_version
    )
    recommendation.sentiment_limit = sentiment_limit
    recommendation.sentiment_provider = sentiment_provider

    db.commit()
    db.refresh(recommendation)

    return recommendation


def delete_market_recommendation(
    db: Session,
    recommendation_id: int,
):
    """
    Delete a market recommendation by ID.
    """

    recommendation = (
        get_market_recommendation_by_id(
            db,
            recommendation_id,
        )
    )

    if recommendation is None:
        return False

    db.delete(recommendation)
    db.commit()

    return True


def upsert_latest_market_recommendation(
    db: Session,
    company_id: int,
    recommendation: str,
    score: float,
    confidence: float,
    financial_score: float,
    sentiment_score: float,
    financial_reasoning: str | None = None,
    sentiment_reasoning: str | None = None,
    overall_reasoning: str | None = None,
    confidence_reasoning: str | None = None,
    sentiment_limit: int = 100,
    sentiment_provider: str | None = None,
    model_version: str = "v1",
):
    """
    Create a market recommendation if one does not
    exist. Otherwise update the latest recommendation.
    """

    existing = get_latest_market_recommendation(
        db,
        company_id,
    )

    if existing is None:

        return create_market_recommendation(
            db=db,
            company_id=company_id,
            recommendation=recommendation,
            score=score,
            confidence=confidence,
            financial_score=financial_score,
            sentiment_score=sentiment_score,
            financial_reasoning=financial_reasoning,
            sentiment_reasoning=sentiment_reasoning,
            overall_reasoning=overall_reasoning,
            confidence_reasoning=confidence_reasoning,
            model_version=model_version,
        )

    return create_market_recommendation(
        db=db,
        company_id=company_id,
        recommendation=recommendation,
        score=score,
        confidence=confidence,
        financial_score=financial_score,
        sentiment_score=sentiment_score,
        financial_reasoning=financial_reasoning,
        sentiment_reasoning=sentiment_reasoning,
        overall_reasoning=overall_reasoning,
        confidence_reasoning=confidence_reasoning,
        sentiment_limit=sentiment_limit,
        sentiment_provider=sentiment_provider,
        model_version=model_version,
    )