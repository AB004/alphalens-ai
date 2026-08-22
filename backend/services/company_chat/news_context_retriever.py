from sqlalchemy.orm import Session

from backend.repositories.news_repository import (
    list_latest_news,
)


class NewsContextRetriever:
    """
    Retrieves company news for Company Chat.

    Module 8 remains the source of truth for news.
    """

    def retrieve(
        self,
        db: Session,
        company_id: int,
        limit: int = 10,
    ) -> dict:
        """
        Retrieve recent news for a company.
        """

        news_items = list_latest_news(
            db=db,
            company_id=company_id,
            limit=limit,
        )

        serialized_news = [
            self._serialize_news(item)
            for item in news_items
        ]

        return {
            "available": bool(serialized_news),
            "items": serialized_news,
        }

    @staticmethod
    def _serialize_news(
        news,
    ) -> dict:
        """
        Convert the Module 8 news model into
        LLM-safe context.
        """

        return {
            "id": news.id,
            "title": news.title,
            "description": getattr(
                news,
                "description",
                None,
            ),
            "source": getattr(
                news,
                "source",
                None,
            ),
            "url": getattr(
                news,
                "url",
                None,
            ),
            "published_at": getattr(
                news,
                "published_at",
                None,
            ),
        }


news_context_retriever = (
    NewsContextRetriever()
)