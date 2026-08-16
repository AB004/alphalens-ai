from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal

from backend.services.sentiment import (
    sentiment_service,
)

from backend.services.sentiment.exceptions import (
    EmptyNewsContentError,
    InvalidSentimentResultError,
    NewsNotFoundError,
    SentimentProcessingError,
)


router = APIRouter(
    tags=["Sentiment"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# ARTICLE SENTIMENT
# ============================================================


@router.get(
    "/news/{news_id}",
)
def get_news_sentiment(
    news_id: int,
    db: Session = Depends(get_db),
):
    """
    Return stored sentiment for a news article.
    """

    result = sentiment_service.get_article_sentiment(
        db,
        news_id,
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Sentiment for news "
                f"'{news_id}' not found."
            ),
        )

    return result


@router.post(
    "/news/{news_id}",
)
def analyze_news_sentiment(
    news_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    """
    Analyze and store sentiment for a news article.
    """

    try:

        result = sentiment_service.analyze_article(
            db=db,
            news_id=news_id,
            force=force,
        )

        return result

    except NewsNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except EmptyNewsContentError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except InvalidSentimentResultError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except SentimentProcessingError as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# ============================================================
# COMPANY SENTIMENT
# ============================================================


@router.get(
    "/company/{symbol}",
)
def get_company_sentiment(
    symbol: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    """
    Return aggregated sentiment for a company.

    Uses stored article-level sentiment results.
    """

    try:

        result = (
            sentiment_service
            .get_company_sentiment_by_symbol(
                db=db,
                symbol=symbol,
                limit=limit,
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