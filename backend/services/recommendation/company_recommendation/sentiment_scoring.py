from dataclasses import dataclass

from backend.models.sentiment import Sentiment


@dataclass
class SentimentScore:
    """
    Aggregated sentiment score for a company.

    Score range:

        -100 -> strongly negative
           0 -> neutral
        +100 -> strongly positive
    """

    score: float

    positive_score: float
    negative_score: float
    neutral_score: float

    positive_count: int
    negative_count: int
    neutral_count: int

    article_count: int

    average_confidence: float

    data_quality: float

    reasoning: list[str]


class SentimentScoringEngine:
    """
    Convert stored article-level sentiment into
    one normalized company sentiment score.

    This class does NOT run FinBERT.

    FinBERT inference belongs to Module 9.
    """

    # ---------------------------------------------------------
    # Sentiment base scores
    # ---------------------------------------------------------

    SENTIMENT_SCORES = {
        "positive": 100.0,
        "neutral": 0.0,
        "negative": -100.0,
    }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def calculate(
        self,
        sentiments: list[Sentiment],
    ) -> SentimentScore:
        """
        Calculate an aggregated sentiment score.
        """

        if not sentiments:
            return SentimentScore(
                score=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=0.0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                article_count=0,
                average_confidence=0.0,
                data_quality=0.0,
                reasoning=[
                    "No sentiment data is available."
                ],
            )

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        weighted_score = 0.0
        total_confidence = 0.0

        for result in sentiments:

            sentiment = (
                result.sentiment
                .strip()
                .lower()
            )

            confidence = self._normalize_confidence(
                result.confidence
            )

            if sentiment == "positive":

                positive_count += 1

                weighted_score += (
                    100.0 * confidence
                )

            elif sentiment == "negative":

                negative_count += 1

                weighted_score -= (
                    100.0 * confidence
                )

            elif sentiment == "neutral":

                neutral_count += 1

            else:
                # Unknown sentiment should not
                # influence the final score.
                continue

            total_confidence += confidence

        article_count = (
            positive_count
            + negative_count
            + neutral_count
        )

        if article_count == 0:

            return SentimentScore(
                score=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=0.0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                article_count=0,
                average_confidence=0.0,
                data_quality=0.0,
                reasoning=[
                    "No valid sentiment records were found."
                ],
            )

        # -----------------------------------------------------
        # Normalize weighted score
        # -----------------------------------------------------

        score = (
            weighted_score
            / article_count
        )

        score = max(
            -100.0,
            min(
                100.0,
                score,
            ),
        )

        average_confidence = (
            total_confidence
            / article_count
        )

        # -----------------------------------------------------
        # Distribution scores
        # -----------------------------------------------------

        positive_score = (
            positive_count
            / article_count
            * 100.0
        )

        negative_score = (
            negative_count
            / article_count
            * 100.0
        )

        neutral_score = (
            neutral_count
            / article_count
            * 100.0
        )

        data_quality = (
            self._calculate_data_quality(
                article_count,
                average_confidence,
            )
        )

        reasoning = self._build_reasoning(
            score=score,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            article_count=article_count,
            average_confidence=average_confidence,
        )

        return SentimentScore(
            score=round(
                score,
                2,
            ),
            positive_score=round(
                positive_score,
                2,
            ),
            negative_score=round(
                negative_score,
                2,
            ),
            neutral_score=round(
                neutral_score,
                2,
            ),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            article_count=article_count,
            average_confidence=round(
                average_confidence,
                4,
            ),
            data_quality=round(
                data_quality,
                2,
            ),
            reasoning=reasoning,
        )

    # ---------------------------------------------------------
    # Confidence normalization
    # ---------------------------------------------------------

    def _normalize_confidence(
        self,
        confidence: float | None,
    ) -> float:
        """
        Ensure confidence is within [0, 1].
        """

        if confidence is None:
            return 0.0

        try:
            value = float(confidence)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )

    # ---------------------------------------------------------
    # Data quality
    # ---------------------------------------------------------

    def _calculate_data_quality(
        self,
        article_count: int,
        average_confidence: float,
    ) -> float:
        """
        Estimate sentiment data quality.

        More articles increase reliability, but
        confidence also matters.

        Maximum score = 100.
        """

        if article_count <= 0:
            return 0.0

        # Article coverage reaches maximum at 100 articles.
        article_quality = min(
            article_count / 100.0,
            1.0,
        )

        confidence_quality = (
            average_confidence
        )

        quality = (
            article_quality
            * 0.5
            + confidence_quality
            * 0.5
        )

        return quality * 100.0

    # ---------------------------------------------------------
    # Reasoning
    # ---------------------------------------------------------

    def _build_reasoning(
        self,
        score: float,
        positive_count: int,
        negative_count: int,
        neutral_count: int,
        article_count: int,
        average_confidence: float,
    ) -> list[str]:
        """
        Build deterministic explanation for
        the aggregated sentiment.
        """

        reasoning: list[str] = []

        positive_percentage = (
            positive_count
            / article_count
            * 100.0
        )

        negative_percentage = (
            negative_count
            / article_count
            * 100.0
        )

        neutral_percentage = (
            neutral_count
            / article_count
            * 100.0
        )

        # -----------------------------------------------------
        # Overall sentiment
        # -----------------------------------------------------

        if score >= 60:

            reasoning.append(
                "Overall news sentiment is strongly positive."
            )

        elif score >= 20:

            reasoning.append(
                "Overall news sentiment is moderately positive."
            )

        elif score > -20:

            reasoning.append(
                "Overall news sentiment is broadly neutral."
            )

        elif score > -60:

            reasoning.append(
                "Overall news sentiment is moderately negative."
            )

        else:

            reasoning.append(
                "Overall news sentiment is strongly negative."
            )

        # -----------------------------------------------------
        # Distribution
        # -----------------------------------------------------

        reasoning.append(
            f"{positive_percentage:.1f}% of analyzed "
            f"articles were positive."
        )

        reasoning.append(
            f"{negative_percentage:.1f}% of analyzed "
            f"articles were negative."
        )

        reasoning.append(
            f"{neutral_percentage:.1f}% of analyzed "
            f"articles were neutral."
        )

        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        if average_confidence >= 0.80:

            reasoning.append(
                "FinBERT confidence is high across "
                "the analyzed articles."
            )

        elif average_confidence >= 0.60:

            reasoning.append(
                "FinBERT confidence is moderate across "
                "the analyzed articles."
            )

        else:

            reasoning.append(
                "FinBERT confidence is relatively low; "
                "the sentiment score should be interpreted "
                "with caution."
            )

        reasoning.append(
            f"Sentiment was calculated from "
            f"{article_count} analyzed articles."
        )

        return reasoning


sentiment_scoring_engine = (
    SentimentScoringEngine()
)