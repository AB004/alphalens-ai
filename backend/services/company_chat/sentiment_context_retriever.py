from sqlalchemy.orm import Session

from backend.services.sentiment.sentiment_service import (
    sentiment_service,
)


class SentimentContextRetriever:
    """
    Retrieve existing company sentiment data
    produced by Module 9.

    This service does not run FinBERT directly.
    It only exposes Module 9 sentiment data
    to Company Chat.
    """

    def retrieve(
        self,
        db: Session,
        company_id: int,
        limit: int = 100,
        provider: str | None = None,
    ) -> dict | None:

        result = sentiment_service.get_company_sentiment(
            db=db,
            company_id=company_id,
            limit=limit,
            provider=provider,
        )

        if not result:
            return None

        return result


sentiment_context_retriever = (
    SentimentContextRetriever()
)