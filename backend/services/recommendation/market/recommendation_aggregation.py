from dataclasses import dataclass

from backend.services.recommendation.market.score_normalization import (
    NormalizedScores,
)


@dataclass
class RecommendationResult:
    """
    Result produced by the recommendation aggregation engine.
    """

    recommendation: str

    score: float

    financial_score: float
    sentiment_score: float

    financial_weight: float
    sentiment_weight: float

    financial_data_quality: float
    sentiment_data_quality: float

    confidence_cap: float

    reasoning: list[str]


class RecommendationAggregationEngine:
    """
    Convert normalized financial and sentiment scores
    into a deterministic BUY / HOLD / SELL recommendation.

    This class does not:
        - call an LLM
        - run FinBERT
        - fetch market data
        - access the database

    It only performs recommendation aggregation.
    """

    # ---------------------------------------------------------
    # Recommendation thresholds
    # ---------------------------------------------------------

    BUY_THRESHOLD = 40.0

    SELL_THRESHOLD = -40.0

    # ---------------------------------------------------------
    # Data quality thresholds
    # ---------------------------------------------------------

    MIN_FINANCIAL_QUALITY = 40.0

    MIN_SENTIMENT_QUALITY = 30.0

    MIN_OVERALL_QUALITY = 40.0

    # ---------------------------------------------------------
    # Confidence caps
    # ---------------------------------------------------------

    HIGH_QUALITY_CONFIDENCE_CAP = 1.00

    MEDIUM_QUALITY_CONFIDENCE_CAP = 0.80

    LOW_QUALITY_CONFIDENCE_CAP = 0.60

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def aggregate(
        self,
        normalized: NormalizedScores,
    ) -> RecommendationResult:
        """
        Generate a deterministic recommendation.
        """

        overall_quality = self._calculate_overall_quality(
            normalized,
        )

        recommendation = self._determine_recommendation(
            normalized=normalized,
            overall_quality=overall_quality,
        )

        confidence_cap = (
            self._calculate_confidence_cap(
                normalized=normalized,
                overall_quality=overall_quality,
            )
        )

        reasoning = self._build_reasoning(
            normalized=normalized,
            recommendation=recommendation,
            overall_quality=overall_quality,
        )

        return RecommendationResult(
            recommendation=recommendation,
            score=round(
                normalized.combined_score,
                2,
            ),
            financial_score=round(
                normalized.financial_score,
                2,
            ),
            sentiment_score=round(
                normalized.sentiment_score,
                2,
            ),
            financial_weight=round(
                normalized.effective_financial_weight,
                4,
            ),
            sentiment_weight=round(
                normalized.effective_sentiment_weight,
                4,
            ),
            financial_data_quality=round(
                normalized.financial_data_quality,
                2,
            ),
            sentiment_data_quality=round(
                normalized.sentiment_data_quality,
                2,
            ),
            confidence_cap=confidence_cap,
            reasoning=reasoning,
        )

    # ---------------------------------------------------------
    # Recommendation decision
    # ---------------------------------------------------------

    def _determine_recommendation(
        self,
        normalized: NormalizedScores,
        overall_quality: float,
    ) -> str:
        """
        Map combined score to BUY / HOLD / SELL.

        Strong recommendations require sufficient data quality.
        """

        if overall_quality < self.MIN_OVERALL_QUALITY:
            return "HOLD"

        score = normalized.combined_score

        if score >= self.BUY_THRESHOLD:
            return "BUY"

        if score <= self.SELL_THRESHOLD:
            return "SELL"

        return "HOLD"

    # ---------------------------------------------------------
    # Overall data quality
    # ---------------------------------------------------------

    def _calculate_overall_quality(
        self,
        normalized: NormalizedScores,
    ) -> float:
        """
        Calculate the quality of the data supporting
        the recommendation.

        Uses the effective weights calculated in Phase 5.
        """

        quality = (
            normalized.financial_data_quality
            * normalized.effective_financial_weight
            +
            normalized.sentiment_data_quality
            * normalized.effective_sentiment_weight
        )

        return max(
            0.0,
            min(
                100.0,
                quality,
            ),
        )

    # ---------------------------------------------------------
    # Confidence cap
    # ---------------------------------------------------------

    def _calculate_confidence_cap(
        self,
        normalized: NormalizedScores,
        overall_quality: float,
    ) -> float:
        """
        Limit maximum confidence based on data quality.

        This is only a cap.

        Phase 7 will calculate the actual confidence.
        """

        if overall_quality >= 80:
            return self.HIGH_QUALITY_CONFIDENCE_CAP

        if overall_quality >= 60:
            return self.MEDIUM_QUALITY_CONFIDENCE_CAP

        return self.LOW_QUALITY_CONFIDENCE_CAP

    # ---------------------------------------------------------
    # Reasoning
    # ---------------------------------------------------------

    def _build_reasoning(
        self,
        normalized: NormalizedScores,
        recommendation: str,
        overall_quality: float,
    ) -> list[str]:
        """
        Build deterministic reasoning for the decision.
        """

        reasoning: list[str] = []

        # -----------------------------------------------------
        # Overall decision
        # -----------------------------------------------------

        if recommendation == "BUY":

            reasoning.append(
                f"The combined score of "
                f"{normalized.combined_score:.2f} "
                f"crosses the BUY threshold of "
                f"{self.BUY_THRESHOLD:.2f}."
            )

        elif recommendation == "SELL":

            reasoning.append(
                f"The combined score of "
                f"{normalized.combined_score:.2f} "
                f"crosses the SELL threshold of "
                f"{self.SELL_THRESHOLD:.2f}."
            )

        else:

            reasoning.append(
                f"The combined score of "
                f"{normalized.combined_score:.2f} "
                f"falls within the HOLD range."
            )

        # -----------------------------------------------------
        # Financial component
        # -----------------------------------------------------

        reasoning.append(
            f"Financial score: "
            f"{normalized.financial_score:.2f}."
        )

        reasoning.append(
            f"Financial component contributes "
            f"{normalized.effective_financial_weight * 100:.1f}% "
            f"of the combined score."
        )

        # -----------------------------------------------------
        # Sentiment component
        # -----------------------------------------------------

        reasoning.append(
            f"Sentiment score: "
            f"{normalized.sentiment_score:.2f}."
        )

        reasoning.append(
            f"Sentiment component contributes "
            f"{normalized.effective_sentiment_weight * 100:.1f}% "
            f"of the combined score."
        )

        # -----------------------------------------------------
        # Data quality
        # -----------------------------------------------------

        reasoning.append(
            f"Financial data quality: "
            f"{normalized.financial_data_quality:.1f}%."
        )

        reasoning.append(
            f"Sentiment data quality: "
            f"{normalized.sentiment_data_quality:.1f}%."
        )

        reasoning.append(
            f"Overall supporting-data quality: "
            f"{overall_quality:.1f}%."
        )

        if overall_quality < self.MIN_OVERALL_QUALITY:

            reasoning.append(
                "Supporting data quality is below the "
                "minimum threshold, so the recommendation "
                "is restricted to HOLD."
            )

        elif overall_quality < 60:

            reasoning.append(
                "The recommendation is based on "
                "moderate-quality supporting data."
            )

        else:

            reasoning.append(
                "Supporting data quality is sufficient "
                "for the aggregation stage."
            )

        return reasoning


recommendation_aggregation_engine = (
    RecommendationAggregationEngine()
)