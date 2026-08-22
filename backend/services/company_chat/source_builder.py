from typing import Any


class CompanyChatSourceBuilder:
    """
    Convert retrieved company context into
    source metadata returned by the API.

    Input:
        HybridContextBuilder output (dict)

    Output:
        List of source metadata dictionaries.
    """

    def build(
        self,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:

        sources: list[dict[str, Any]] = []

        self._add_financial_sources(
            sources,
            context.get("financial"),
        )

        self._add_news_sources(
            sources,
            context.get("news"),
        )

        self._add_sentiment_sources(
            sources,
            context.get("sentiment"),
        )

        self._add_recommendation_source(
            sources,
            context.get("recommendation"),
        )

        return self._deduplicate(
            sources,
        )

    # =========================================================
    # FINANCIAL
    # =========================================================

    def _add_financial_sources(
        self,
        sources: list[dict[str, Any]],
        financial: Any,
    ):

        if financial is None:
            return

        if isinstance(financial, dict):

            if not financial.get("available", True):
                return

            data = financial.get(
                "data",
                financial,
            )

            if isinstance(data, list):

                for item in data:

                    sources.append(
                        {
                            "type": "financial",
                            "source": str(item),
                        }
                    )

            else:

                sources.append(
                    {
                        "type": "financial",
                        "source": str(data),
                    }
                )

            return

        if isinstance(financial, list):

            for item in financial:

                sources.append(
                    {
                        "type": "financial",
                        "source": str(item),
                    }
                )

            return

        sources.append(
            {
                "type": "financial",
                "source": str(financial),
            }
        )

    # =========================================================
    # NEWS
    # =========================================================

    def _add_news_sources(
        self,
        sources: list[dict[str, Any]],
        news: Any,
    ):

        if news is None:
            return
        
        if isinstance(news, dict):

            if not news.get("available", True):
                return

            items = news.get(
                "items",
                [],
            )

            for item in items:

                if not isinstance(item, dict):
                    continue

                sources.append(
                    {
                        "type": "news",
                        "source": item.get("url"),
                        "title": item.get("title"),
                        "reference_id": item.get("id"),
                    }
                )

            return

        # Fallback if a raw list is passed

        if isinstance(news, list):

            for item in news:

                if isinstance(item, dict):

                    sources.append(
                        {
                            "type": "news",
                            "source": item.get("url"),
                            "title": item.get("title"),
                            "reference_id": item.get("id"),
                        }
                    )

                else:

                    sources.append(
                        {
                            "type": "news",
                            "source": str(item),
                        }
                    )

    # =========================================================
    # SENTIMENT
    # =========================================================

    def _add_sentiment_sources(
        self,
        sources: list[dict[str, Any]],
        sentiment: Any,
    ):

        if sentiment is None:
            return

        if isinstance(sentiment, dict):

            if not sentiment.get(
                "available",
                True,
            ):
                return

        sources.append(
            {
                "type": "sentiment",
                "source": "Module 9 sentiment analysis",
            }
        )

    # =========================================================
    # RECOMMENDATION
    # =========================================================

    def _add_recommendation_source(
        self,
        sources: list[dict[str, Any]],
        recommendation: Any,
    ):

        if recommendation is None:
            return

        if isinstance(recommendation, dict):

            if not recommendation.get(
                "available",
                True,
            ):
                return

            data = recommendation.get(
                "data",
                recommendation,
            )

            reference_id = None

            if isinstance(data, dict):
                reference_id = data.get(
                    "id"
                )

            sources.append(
                {
                    "type": "recommendation",
                    "source": (
                        "Module 10 market recommendation"
                    ),
                    "reference_id": reference_id,
                }
            )

            return

        sources.append(
            {
                "type": "recommendation",
                "source": (
                    "Module 10 market recommendation"
                ),
            }
        )

    # =========================================================
    # DEDUPLICATION
    # =========================================================

    def _deduplicate(
        self,
        sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        unique: list[dict[str, Any]] = []
        seen: set = set()

        for source in sources:

            key = (
                source.get("type"),
                source.get("reference_id"),
                source.get("source"),
                source.get("title"),
            )

            try:
                hash(key)
            except TypeError:
                key = tuple(
                    str(value)
                    for value in key
                )

            if key in seen:
                continue

            seen.add(key)
            unique.append(source)

        return unique


company_chat_source_builder = (
    CompanyChatSourceBuilder()
)