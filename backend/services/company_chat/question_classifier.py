from enum import Enum


class CompanyQuestionType(str, Enum):
    FINANCIAL = "financial"
    NEWS = "news"
    SENTIMENT = "sentiment"
    RECOMMENDATION = "recommendation"
    HYBRID = "hybrid"
    GENERAL = "general"


class CompanyQuestionClassifier:
    """
    Classify company questions.

    Phase 1 uses a lightweight deterministic classifier.
    More advanced classification can be introduced later.
    """

    FINANCIAL_KEYWORDS = {
        "revenue",
        "profit",
        "income",
        "earnings",
        "ebitda",
        "eps",
        "cash flow",
        "cashflow",
        "assets",
        "liabilities",
        "debt",
        "equity",
        "margin",
        "ratio",
        "financial",
        "balance sheet",
        "income statement",
    }

    NEWS_KEYWORDS = {
        "news",
        "announcement",
        "announcements",
        "event",
        "events",
        "headline",
        "headlines",
    }

    SENTIMENT_KEYWORDS = {
        "sentiment",
        "positive",
        "negative",
        "neutral",
        "market mood",
        "investor sentiment",
    }

    RECOMMENDATION_KEYWORDS = {
        "buy",
        "sell",
        "hold",
        "recommendation",
        "recommend",
        "rating",
        "score",
        "should i buy",
        "should i sell",
    }

    def classify(
        self,
        question: str,
    ) -> CompanyQuestionType:

        if not isinstance(question, str):
            return CompanyQuestionType.GENERAL

        text = question.strip().lower()

        if not text:
            return CompanyQuestionType.GENERAL

        financial = self._contains_any(
            text,
            self.FINANCIAL_KEYWORDS,
        )

        news = self._contains_any(
            text,
            self.NEWS_KEYWORDS,
        )

        sentiment = self._contains_any(
            text,
            self.SENTIMENT_KEYWORDS,
        )

        recommendation = self._contains_any(
            text,
            self.RECOMMENDATION_KEYWORDS,
        )

        matches = sum(
            [
                financial,
                news,
                sentiment,
                recommendation,
            ]
        )

        if matches > 1:
            return CompanyQuestionType.HYBRID

        if financial:
            return CompanyQuestionType.FINANCIAL

        if news:
            return CompanyQuestionType.NEWS

        if sentiment:
            return CompanyQuestionType.SENTIMENT

        if recommendation:
            return CompanyQuestionType.RECOMMENDATION

        return CompanyQuestionType.GENERAL

    @staticmethod
    def _contains_any(
        text: str,
        keywords: set[str],
    ) -> bool:

        return any(
            keyword in text
            for keyword in keywords
        )


question_classifier = CompanyQuestionClassifier()