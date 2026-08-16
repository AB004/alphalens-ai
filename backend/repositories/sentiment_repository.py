from typing import Any

from sqlalchemy.orm import Session

from backend.models.sentiment import Sentiment

from sqlalchemy import select

from backend.models.news import News

def get_sentiment_by_news_id(
    db: Session,
    news_id: int,
):
    """
    Return the sentiment associated with a news article.
    """

    return (
        db.query(Sentiment)
        .filter(
            Sentiment.news_id == news_id,
        )
        .first()
    )

def get_sentiments_by_news_ids(
    db: Session,
    news_ids: list[int],
) -> list[Sentiment]:
    """
    Return sentiment records for the supplied news IDs.
    """

    if not news_ids:
        return []

    return (
        db.query(Sentiment)
        .filter(
            Sentiment.news_id.in_(news_ids),
        )
        .all()
    )

def create_sentiment(
    db: Session,
    news_id: int,
    model: str,
    sentiment: str,
    confidence: float,
):
    """
    Create a sentiment record for a news article.
    """

    result = Sentiment(
        news_id=news_id,
        model=model,
        sentiment=sentiment,
        confidence=confidence,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result


def update_sentiment(
    db: Session,
    sentiment_record: Sentiment,
    model: str,
    sentiment: str,
    confidence: float,
):
    """
    Update an existing sentiment record.
    """

    sentiment_record.model = model
    sentiment_record.sentiment = sentiment
    sentiment_record.confidence = confidence

    db.commit()
    db.refresh(sentiment_record)

    return sentiment_record


def upsert_sentiment(
    db: Session,
    news_id: int,
    model: str,
    sentiment: str,
    confidence: float,
):
    """
    Create a sentiment record if it does not exist,
    otherwise update the existing record.
    """

    existing = get_sentiment_by_news_id(
        db,
        news_id,
    )

    if existing is None:
        return create_sentiment(
            db=db,
            news_id=news_id,
            model=model,
            sentiment=sentiment,
            confidence=confidence,
        )

    return update_sentiment(
        db=db,
        sentiment_record=existing,
        model=model,
        sentiment=sentiment,
        confidence=confidence,
    )


def delete_sentiment(
    db: Session,
    news_id: int,
):
    """
    Delete sentiment associated with a news article.
    """

    sentiment_record = get_sentiment_by_news_id(
        db,
        news_id,
    )

    if sentiment_record is None:
        return False

    db.delete(sentiment_record)
    db.commit()

    return True

def get_company_sentiments(
    db: Session,
    company_id: int,
    limit: int = 100,
    provider: str | None = None,
) -> list[Sentiment]:

    query = (
        db.query(Sentiment)
        .join(
            News,
            News.id == Sentiment.news_id,
        )
        .filter(
            News.company_id == company_id,
        )
    )

    if provider:
        query = query.filter(
            News.provider == provider,
        )

    return (
        query
        .order_by(
            News.published_at.desc(),
            News.created_at.desc(),
        )
        .limit(limit)
        .all()
    )