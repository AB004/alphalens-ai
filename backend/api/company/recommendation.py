from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal

from backend.repositories.company_repository import (
    get_company_by_symbol,
)

from backend.repositories.market_recommendation_repository import (
    list_market_recommendations,
)
from backend.services.recommendation.market.market_recommendation_service import (
    market_recommendation_service,
)
from backend.repositories.market_recommendation_repository import (
    get_latest_market_recommendation,
)

router = APIRouter(
    tags=["Market Recommendation"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# LATEST RECOMMENDATION
# ============================================================


@router.get(
    "/{symbol}/recommendation",
)
def get_company_recommendation(
    symbol: str,
    db: Session = Depends(get_db),
):
    """
    Return the latest market recommendation
    for a company.
    """

    symbol = symbol.strip().upper()

    company = get_company_by_symbol(
        db,
        symbol,
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Company '{symbol}' not found."
            ),
        )

    recommendation = get_latest_market_recommendation(
        db=db,
        company_id=company.id,
    )

    if recommendation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Recommendation for "
                f"company '{symbol}' not found."
            ),
        )

    return _serialize_recommendation(
        recommendation,
        symbol,
    )


# ============================================================
# GENERATE RECOMMENDATION
# ============================================================


@router.post(
    "/{symbol}/recommendation/analyze",
)
def analyze_company_recommendation(
    symbol: str,

    sentiment_limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),

    provider: str | None = Query(
        default=None,
    ),

    force: bool = Query(
        default=False,
    ),

    db: Session = Depends(get_db),
):
    """
    Generate a new market recommendation.

    The recommendation combines:

    - Financial score
    - Sentiment score
    - Confidence
    - Explainable reasoning

    Sentiment can optionally be restricted
    to a specific provider.
    """

    symbol = symbol.strip().upper()

    try:

        result = (
            market_recommendation_service.generate(
                db=db,
                symbol=symbol,
                sentiment_limit=sentiment_limit,
                provider=provider,
                force=force,
            )
        )

        return result

    except ValueError as exc:

        message = str(exc)

        if "not found" in message.lower():

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    except Exception as exc:

        print(
            "MARKET RECOMMENDATION ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ============================================================
# RECOMMENDATION HISTORY
# ============================================================


@router.get(
    "/{symbol}/recommendations",
)
def get_recommendation_history(
    symbol: str,

    skip: int = Query(
        default=0,
        ge=0,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: Session = Depends(get_db),
):
    """
    Return recommendation history for a company.
    """

    symbol = symbol.strip().upper()

    company = get_company_by_symbol(
        db,
        symbol,
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Company '{symbol}' not found."
            ),
        )

    recommendations = list_market_recommendations(
        db=db,
        company_id=company.id,
        skip=skip,
        limit=limit,
    )

    return {
        "symbol": company.symbol,
        "count": len(recommendations),
        "recommendations": [
            _serialize_recommendation(
                recommendation,
                company.symbol,
            )
            for recommendation in recommendations
        ],
    }


# ============================================================
# SERIALIZATION
# ============================================================


def _serialize_recommendation(
    recommendation,
    symbol: str,
):
    return {
        "id": recommendation.id,
        "symbol": symbol,
        "recommendation": (
            recommendation.recommendation
        ),
        "score": recommendation.score,
        "confidence": recommendation.confidence,
        "financial_score": (
            recommendation.financial_score
        ),
        "sentiment_score": (
            recommendation.sentiment_score
        ),
        "financial_reasoning": (
            recommendation.financial_reasoning
        ),
        "sentiment_reasoning": (
            recommendation.sentiment_reasoning
        ),
        "overall_reasoning": (
            recommendation.overall_reasoning
        ),
        "confidence_reasoning": (
            recommendation.confidence_reasoning
        ),
        "model_version": (
            recommendation.model_version
        ),
        "created_at": (
            recommendation.created_at
        ),
        "updated_at": (
            recommendation.updated_at
        ),
    }