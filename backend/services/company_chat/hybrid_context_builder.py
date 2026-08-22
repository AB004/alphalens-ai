from dataclasses import asdict
from typing import Any

from backend.services.company_chat.context_builder import (
    CompanyChatContext,
)


class HybridContextBuilder:
    """
    Builds the complete context used by Company Chat.

    Combines:

    - Company identity
    - Financial data
    - News
    - Sentiment
    - Recommendation
    - Conversation history

    This class does not:
        - call an LLM
        - fetch data
        - modify the database
        - make recommendations

    It only assembles already retrieved information.
    """

    def build(
        self,
        context: CompanyChatContext,
    ) -> dict[str, Any]:

        return {
            "company": self._build_company_context(
                context,
            ),

            "question": context.question,

            "resolved_question": context.resolved_question,

            "question_type": context.question_type.value,

            "conversation": self._build_conversation_context(
                context,
            ),

            "financial": self._build_financial_context(
                context.financial,
            ),

            "news": self._build_news_context(
                context.news,
            ),

            "sentiment": self._build_sentiment_context(
                context.sentiment,
            ),

            "recommendation": (
                self._build_recommendation_context(
                    context.recommendation,
                )
            ),
        }
   
    # =========================================================
    # COMPANY
    # =========================================================

    def _build_company_context(
        self,
        context: CompanyChatContext,
    ) -> dict[str, Any]:
        """
        Serialize canonical company identity.
        """

        company = context.company

        return {
            "company_id": company.company_id,
            "symbol": company.symbol,
            "company_name": company.company_name,
            "sector": company.sector,
            "industry": company.industry,
            "exchange": company.exchange,
            "currency": company.currency,
            "country": company.country,
        }

    # =========================================================
    # CONVERSATION
    # =========================================================

    def _build_conversation_context(
        self,
        context: CompanyChatContext,
    ) -> list[dict[str, Any]]:
        """
        Normalize conversation history.
        """

        if not context.conversation:
            return []

        result = []

        for message in context.conversation:

            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get(
                "message",
                message.get("content"),
            )

            if not role or not content:
                continue

            result.append(
                {
                    "role": role,
                    "message": str(content),
                }
            )

        return result

    # =========================================================
    # FINANCIAL
    # =========================================================

    def _build_financial_context(
        self,
        financial: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize financial context.

        Financial data is produced by Module 7.
        """

        if financial is None:
            return None

        if isinstance(financial, dict):

            return {
                "available": financial.get(
                    "available",
                    True,
                ),
                "data": financial.get(
                    "data",
                    financial,
                ),
            }

        return {
            "available": True,
            "data": financial,
        }

    # =========================================================
    # NEWS
    # =========================================================

    def _build_news_context(
        self,
        news: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize news context.

        News data is produced by Module 8.
        """

        if news is None:
            return None

        if isinstance(news, dict):

            items = news.get(
                "items",
                [],
            )

            return {
                "available": bool(
                    news.get(
                        "available",
                        bool(items),
                    )
                ),
                "items": [
                    self._serialize_news_item(
                        item,
                    )
                    for item in items
                ],
            }

        if isinstance(news, list):

            return {
                "available": bool(news),
                "items": [
                    self._serialize_news_item(
                        item,
                    )
                    for item in news
                ],
            }

        return {
            "available": True,
            "items": [],
        }

    @staticmethod
    def _serialize_news_item(
        item: Any,
    ) -> dict[str, Any]:
        """
        Normalize one news item.
        """

        if isinstance(item, dict):
            return {
                "id": item.get("id"),
                "title": item.get("title"),
                "description": item.get(
                    "description",
                ),
                "source": item.get(
                    "source",
                ),
                "url": item.get(
                    "url",
                ),
                "published_at": item.get(
                    "published_at",
                ),
            }

        return {
            "id": getattr(
                item,
                "id",
                None,
            ),
            "title": getattr(
                item,
                "title",
                None,
            ),
            "description": getattr(
                item,
                "description",
                None,
            ),
            "source": getattr(
                item,
                "source",
                None,
            ),
            "url": getattr(
                item,
                "url",
                None,
            ),
            "published_at": getattr(
                item,
                "published_at",
                None,
            ),
        }

    # =========================================================
    # SENTIMENT
    # =========================================================

    def _build_sentiment_context(
        self,
        sentiment: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize sentiment context.

        Sentiment data is produced by Module 9.
        """

        if sentiment is None:
            return None

        if isinstance(sentiment, dict):

            return {
                "available": sentiment.get(
                    "available",
                    True,
                ),
                "data": sentiment.get(
                    "data",
                    sentiment,
                ),
            }

        return {
            "available": True,
            "data": sentiment,
        }

    # =========================================================
    # RECOMMENDATION
    # =========================================================

    def _build_recommendation_context(
        self,
        recommendation: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize market recommendation context.

        Recommendation data is produced by Module 10.
        """

        if recommendation is None:
            return None

        if isinstance(recommendation, dict):

            return {
                "available": recommendation.get(
                    "available",
                    True,
                ),
                "data": recommendation.get(
                    "data",
                    recommendation,
                ),
            }

        return {
            "available": True,
            "data": recommendation,
        }


hybrid_context_builder = HybridContextBuilder()