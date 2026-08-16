from dataclasses import dataclass

from backend.services.recommendation.market.recommendation_aggregation import (
    RecommendationResult,
)

from backend.services.recommendation.market.confidence_calculator import (
    ConfidenceResult,
)


@dataclass
class RecommendationReasoning:
    """
    Explainable reasoning for a market recommendation.
    """

    financial_reasoning: str

    sentiment_reasoning: str

    overall_reasoning: str

    confidence_reasoning: str


class ExplainableReasoningEngine:
    """
    Generate deterministic explanations for a market
    recommendation.

    This engine does not decide BUY / HOLD / SELL.

    The recommendation has already been decided by
    RecommendationAggregationEngine.
    """

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def generate(
        self,
        recommendation: RecommendationResult,
        confidence: ConfidenceResult,
    ) -> RecommendationReasoning:
        """
        Generate all recommendation explanations.
        """

        financial_reasoning = (
            self._financial_reasoning(
                recommendation,
            )
        )

        sentiment_reasoning = (
            self._sentiment_reasoning(
                recommendation,
            )
        )

        overall_reasoning = (
            self._overall_reasoning(
                recommendation,
                confidence,
            )
        )

        confidence_reasoning = (
            self._confidence_reasoning(
                confidence,
            )
        )

        return RecommendationReasoning(
            financial_reasoning=financial_reasoning,
            sentiment_reasoning=sentiment_reasoning,
            overall_reasoning=overall_reasoning,
            confidence_reasoning=confidence_reasoning,
        )

    # ---------------------------------------------------------
    # Financial reasoning
    # ---------------------------------------------------------

    def _financial_reasoning(
        self,
        recommendation: RecommendationResult,
    ) -> str:
        score = recommendation.financial_score

        if score >= 60:

            direction = (
                "strongly positive"
            )

        elif score >= 20:

            direction = (
                "moderately positive"
            )

        elif score <= -60:

            direction = (
                "strongly negative"
            )

        elif score <= -20:

            direction = (
                "moderately negative"
            )

        else:

            direction = (
                "relatively neutral"
            )

        return (
            f"The financial component is "
            f"{direction}, with a financial score "
            f"of {score:.2f}. "
            f"Financial data contributes "
            f"{recommendation.financial_weight * 100:.1f}% "
            f"to the combined recommendation score. "
            f"Financial data quality is "
            f"{recommendation.financial_data_quality:.1f}%."
        )

    # ---------------------------------------------------------
    # Sentiment reasoning
    # ---------------------------------------------------------

    def _sentiment_reasoning(
        self,
        recommendation: RecommendationResult,
    ) -> str:
        score = recommendation.sentiment_score

        if score >= 60:

            direction = (
                "strongly positive"
            )

        elif score >= 20:

            direction = (
                "moderately positive"
            )

        elif score <= -60:

            direction = (
                "strongly negative"
            )

        elif score <= -20:

            direction = (
                "moderately negative"
            )

        else:

            direction = (
                "relatively neutral"
            )

        return (
            f"Market sentiment is "
            f"{direction}, with a sentiment score "
            f"of {score:.2f}. "
            f"Sentiment contributes "
            f"{recommendation.sentiment_weight * 100:.1f}% "
            f"to the combined recommendation score. "
            f"Sentiment data quality is "
            f"{recommendation.sentiment_data_quality:.1f}%."
        )

    # ---------------------------------------------------------
    # Overall reasoning
    # ---------------------------------------------------------

    def _overall_reasoning(
        self,
        recommendation: RecommendationResult,
        confidence: ConfidenceResult,
    ) -> str:
        score = recommendation.score

        if recommendation.recommendation == "BUY":

            decision = (
                "The available financial and sentiment "
                "signals support a BUY recommendation."
            )

        elif recommendation.recommendation == "SELL":

            decision = (
                "The available financial and sentiment "
                "signals support a SELL recommendation."
            )

        else:

            decision = (
                "The available financial and sentiment "
                "signals do not provide sufficient "
                "direction for a BUY or SELL recommendation, "
                "so the system recommends HOLD."
            )

        return (
            f"{decision} "
            f"The combined score is {score:.2f}. "
            f"The resulting confidence is "
            f"{confidence.confidence * 100:.1f}%."
        )

    # ---------------------------------------------------------
    # Confidence reasoning
    # ---------------------------------------------------------

    def _confidence_reasoning(
        self,
        confidence: ConfidenceResult,
    ) -> str:
        return (
            f"Confidence is based on score strength "
            f"({confidence.score_strength * 100:.1f}%), "
            f"supporting-data quality "
            f"({confidence.data_quality * 100:.1f}%), "
            f"and financial/sentiment agreement "
            f"({confidence.agreement_score * 100:.1f}%). "
            f"The final confidence is "
            f"{confidence.confidence * 100:.1f}%."
        )


explainable_reasoning_engine = (
    ExplainableReasoningEngine()
)