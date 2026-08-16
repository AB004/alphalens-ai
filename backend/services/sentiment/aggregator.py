from typing import Any


class SentimentAggregator:
    """
    Aggregates article-level sentiment into a
    company-level sentiment score.
    """

    SENTIMENT_VALUES = {
        "positive": 1.0,
        "neutral": 0.0,
        "negative": -1.0,
    }

    def aggregate(
        self,
        sentiments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Aggregate article-level sentiment results.

        Each item must contain:

        {
            "sentiment": "positive",
            "confidence": 0.94
        }
        """

        if not sentiments:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "article_count": 0,
            }

        weighted_sum = 0.0
        total_weight = 0.0

        for item in sentiments:

            sentiment = item["sentiment"]
            confidence = float(
                item["confidence"]
            )

            value = self.SENTIMENT_VALUES[
                sentiment
            ]

            weighted_sum += (
                value * confidence
            )

            total_weight += confidence

        if total_weight == 0:
            score = 0.0
        else:
            score = (
                weighted_sum
                / total_weight
            )

        score = max(
            -1.0,
            min(1.0, score),
        )

        label = self._score_to_label(
            score,
        )

        confidence = self._calculate_confidence(
            sentiments,
            score,
        )

        return {
            "sentiment": label,
            "score": score,
            "confidence": confidence,
            "article_count": len(sentiments),
        }

    @staticmethod
    def _score_to_label(
        score: float,
    ) -> str:
        """
        Convert normalized score into a sentiment label.
        """

        if score > 0.15:
            return "positive"

        if score < -0.15:
            return "negative"

        return "neutral"

    @staticmethod
    def _calculate_confidence(
        sentiments: list[dict[str, Any]],
        score: float,
    ) -> float:
        """
        Calculate company-level confidence.

        This combines:
        - article confidence
        - agreement between articles
        """

        if not sentiments:
            return 0.0

        average_confidence = sum(
            float(item["confidence"])
            for item in sentiments
        ) / len(sentiments)

        if abs(score) >= 0.75:
            agreement_factor = 1.0

        elif abs(score) >= 0.50:
            agreement_factor = 0.9

        elif abs(score) >= 0.25:
            agreement_factor = 0.75

        else:
            agreement_factor = 0.60

        confidence = (
            average_confidence
            * agreement_factor
        )

        return max(
            0.0,
            min(1.0, confidence),
        )