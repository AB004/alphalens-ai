from dataclasses import dataclass

from backend.services.recommendation.market.recommendation_aggregation import (
    RecommendationResult,
)


@dataclass
class ConfidenceResult:
    """
    Result produced by the confidence calculation engine.
    """

    confidence: float

    score_strength: float

    data_quality: float

    agreement_score: float

    confidence_cap: float

    reasoning: list[str]


class ConfidenceCalculator:
    """
    Calculate confidence for a market recommendation.

    Confidence is independent from the recommendation itself.

    Recommendation:
        BUY / HOLD / SELL

    Confidence:
        0.0 ... 1.0
    """

    # ---------------------------------------------------------
    # Component weights
    # ---------------------------------------------------------

    SCORE_STRENGTH_WEIGHT = 0.40

    DATA_QUALITY_WEIGHT = 0.35

    AGREEMENT_WEIGHT = 0.25

    # ---------------------------------------------------------
    # Score normalization
    # ---------------------------------------------------------

    MAX_SCORE = 100.0

    # ---------------------------------------------------------
    # Minimum confidence
    # ---------------------------------------------------------

    MIN_CONFIDENCE = 0.05

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def calculate(
        self,
        result: RecommendationResult,
    ) -> ConfidenceResult:
        """
        Calculate recommendation confidence.
        """

        score_strength = (
            self._calculate_score_strength(
                result.score,
            )
        )

        data_quality = (
            self._calculate_data_quality(
                result,
            )
        )

        agreement_score = (
            self._calculate_agreement(
                result.financial_score,
                result.sentiment_score,
            )
        )

        raw_confidence = (
            score_strength
            * self.SCORE_STRENGTH_WEIGHT
            +
            data_quality
            * self.DATA_QUALITY_WEIGHT
            +
            agreement_score
            * self.AGREEMENT_WEIGHT
        )

        confidence = min(
            raw_confidence,
            result.confidence_cap,
        )

        confidence = max(
            self.MIN_CONFIDENCE,
            min(
                1.0,
                confidence,
            ),
        )

        reasoning = self._build_reasoning(
            result=result,
            score_strength=score_strength,
            data_quality=data_quality,
            agreement_score=agreement_score,
            raw_confidence=raw_confidence,
            confidence=confidence,
        )

        return ConfidenceResult(
            confidence=round(
                confidence,
                4,
            ),
            score_strength=round(
                score_strength,
                4,
            ),
            data_quality=round(
                data_quality,
                4,
            ),
            agreement_score=round(
                agreement_score,
                4,
            ),
            confidence_cap=round(
                result.confidence_cap,
                4,
            ),
            reasoning=reasoning,
        )

    # ---------------------------------------------------------
    # Score strength
    # ---------------------------------------------------------

    def _calculate_score_strength(
        self,
        score: float,
    ) -> float:
        """
        Convert the absolute combined score into
        a 0...1 strength value.

        Examples:

            score = 0
                -> 0.0

            score = 50
                -> 0.5

            score = 100
                -> 1.0
        """

        strength = (
            abs(score)
            / self.MAX_SCORE
        )

        return max(
            0.0,
            min(
                1.0,
                strength,
            ),
        )

    # ---------------------------------------------------------
    # Data quality
    # ---------------------------------------------------------

    def _calculate_data_quality(
        self,
        result: RecommendationResult,
    ) -> float:
        """
        Combine financial and sentiment data quality.

        The effective weights from Phase 5 are used.
        """

        quality = (
            result.financial_data_quality
            * result.financial_weight
            +
            result.sentiment_data_quality
            * result.sentiment_weight
        )

        quality = max(
            0.0,
            min(
                100.0,
                quality,
            ),
        )

        return quality / 100.0

    # ---------------------------------------------------------
    # Financial / sentiment agreement
    # ---------------------------------------------------------

    def _calculate_agreement(
        self,
        financial_score: float,
        sentiment_score: float,
    ) -> float:
        """
        Measure whether financials and sentiment
        point in the same direction.

        Returns:

            1.0 -> strong agreement
            0.5 -> neutral / weak information
            0.0 -> strong disagreement
        """

        financial_direction = self._direction(
            financial_score,
        )

        sentiment_direction = self._direction(
            sentiment_score,
        )

        # Both positive
        if (
            financial_direction > 0
            and sentiment_direction > 0
        ):
            return self._direction_strength(
                financial_score,
                sentiment_score,
            )

        # Both negative
        if (
            financial_direction < 0
            and sentiment_direction < 0
        ):
            return self._direction_strength(
                financial_score,
                sentiment_score,
            )

        # One or both are neutral
        if (
            financial_direction == 0
            or sentiment_direction == 0
        ):
            return 0.5

        # Opposite directions
        return self._disagreement_strength(
            financial_score,
            sentiment_score,
        )

    # ---------------------------------------------------------
    # Direction
    # ---------------------------------------------------------

    def _direction(
        self,
        score: float,
    ) -> int:
        """
        Convert score to direction.
        """

        if score > 10:
            return 1

        if score < -10:
            return -1

        return 0

    # ---------------------------------------------------------
    # Agreement strength
    # ---------------------------------------------------------

    def _direction_strength(
        self,
        financial_score: float,
        sentiment_score: float,
    ) -> float:
        """
        Calculate strength when both signals
        point in the same direction.
        """

        financial_strength = (
            abs(financial_score)
            / self.MAX_SCORE
        )

        sentiment_strength = (
            abs(sentiment_score)
            / self.MAX_SCORE
        )

        strength = (
            financial_strength
            + sentiment_strength
        ) / 2.0

        # Even weak agreement should not become zero.
        return max(
            0.5,
            min(
                1.0,
                strength,
            ),
        )

    # ---------------------------------------------------------
    # Disagreement strength
    # ---------------------------------------------------------

    def _disagreement_strength(
        self,
        financial_score: float,
        sentiment_score: float,
    ) -> float:
        """
        Calculate agreement when financials and
        sentiment point in opposite directions.

        Strong disagreement produces a low score.
        """

        financial_strength = (
            abs(financial_score)
            / self.MAX_SCORE
        )

        sentiment_strength = (
            abs(sentiment_score)
            / self.MAX_SCORE
        )

        disagreement = (
            financial_strength
            + sentiment_strength
        ) / 2.0

        return max(
            0.0,
            min(
                0.5,
                0.5 - disagreement / 2.0,
            ),
        )

    # ---------------------------------------------------------
    # Reasoning
    # ---------------------------------------------------------

    def _build_reasoning(
        self,
        result: RecommendationResult,
        score_strength: float,
        data_quality: float,
        agreement_score: float,
        raw_confidence: float,
        confidence: float,
    ) -> list[str]:
        """
        Build deterministic confidence explanation.
        """

        reasoning: list[str] = []

        reasoning.append(
            f"Combined score strength: "
            f"{score_strength * 100:.1f}%."
        )

        reasoning.append(
            f"Supporting data quality: "
            f"{data_quality * 100:.1f}%."
        )

        reasoning.append(
            f"Financial/sentiment agreement: "
            f"{agreement_score * 100:.1f}%."
        )

        reasoning.append(
            f"Raw confidence before cap: "
            f"{raw_confidence * 100:.1f}%."
        )

        if raw_confidence > result.confidence_cap:

            reasoning.append(
                f"Confidence was capped at "
                f"{result.confidence_cap * 100:.1f}% "
                f"because of supporting-data quality."
            )

        reasoning.append(
            f"Final confidence: "
            f"{confidence * 100:.1f}%."
        )

        return reasoning


confidence_calculator = ConfidenceCalculator()