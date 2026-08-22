from dataclasses import dataclass


@dataclass
class NormalizedScores:
    """
    Normalized inputs used by the recommendation
    aggregation phase.

    All component scores remain in the range:

        -100 -> strongly negative
           0 -> neutral
        +100 -> strongly positive
    """

    financial_score: float
    sentiment_score: float

    financial_weight: float
    sentiment_weight: float

    financial_data_quality: float
    sentiment_data_quality: float

    effective_financial_weight: float
    effective_sentiment_weight: float

    combined_score: float


class ScoreNormalizer:
    """
    Normalize and align financial and sentiment scores.

    Both Phase 3 and Phase 4 already produce scores
    between -100 and +100.

    Therefore this class does not arbitrarily rescale
    those scores.

    Instead, it:
        1. validates the ranges
        2. clamps invalid values
        3. normalizes configured weights
        4. adjusts weights using data quality
        5. calculates a preliminary weighted score

    It does NOT generate BUY/HOLD/SELL.
    """

    DEFAULT_FINANCIAL_WEIGHT = 0.70
    DEFAULT_SENTIMENT_WEIGHT = 0.30

    def normalize(
        self,
        financial_score: float,
        sentiment_score: float,
        financial_data_quality: float = 100.0,
        sentiment_data_quality: float = 100.0,
        financial_weight: float = DEFAULT_FINANCIAL_WEIGHT,
        sentiment_weight: float = DEFAULT_SENTIMENT_WEIGHT,
    ) -> NormalizedScores:
        """
        Normalize financial and sentiment inputs.
        """

        financial_score = self._clamp_score(
            financial_score
        )

        sentiment_score = self._clamp_score(
            sentiment_score
        )

        financial_data_quality = (
            self._clamp_quality(
                financial_data_quality
            )
        )

        sentiment_data_quality = (
            self._clamp_quality(
                sentiment_data_quality
            )
        )

        (
            financial_weight,
            sentiment_weight,
        ) = self._normalize_weights(
            financial_weight,
            sentiment_weight,
        )

        (
            effective_financial_weight,
            effective_sentiment_weight,
        ) = self._calculate_effective_weights(
            financial_weight=financial_weight,
            sentiment_weight=sentiment_weight,
            financial_data_quality=financial_data_quality,
            sentiment_data_quality=sentiment_data_quality,
        )

        combined_score = (
            financial_score
            * effective_financial_weight
            +
            sentiment_score
            * effective_sentiment_weight
        )

        combined_score = self._clamp_score(
            combined_score
        )

        return NormalizedScores(
            financial_score=round(
                financial_score,
                2,
            ),
            sentiment_score=round(
                sentiment_score,
                2,
            ),
            financial_weight=round(
                financial_weight,
                4,
            ),
            sentiment_weight=round(
                sentiment_weight,
                4,
            ),
            financial_data_quality=round(
                financial_data_quality,
                2,
            ),
            sentiment_data_quality=round(
                sentiment_data_quality,
                2,
            ),
            effective_financial_weight=round(
                effective_financial_weight,
                4,
            ),
            effective_sentiment_weight=round(
                effective_sentiment_weight,
                4,
            ),
            combined_score=round(
                combined_score,
                2,
            ),
        )

    # ---------------------------------------------------------
    # Score validation
    # ---------------------------------------------------------

    def _clamp_score(
        self,
        value: float,
    ) -> float:
        """
        Keep score within [-100, 100].
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            -100.0,
            min(
                100.0,
                value,
            ),
        )

    # ---------------------------------------------------------
    # Quality validation
    # ---------------------------------------------------------

    def _clamp_quality(
        self,
        value: float,
    ) -> float:
        """
        Keep data quality within [0, 100].
        """

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )

    # ---------------------------------------------------------
    # Weight normalization
    # ---------------------------------------------------------

    def _normalize_weights(
        self,
        financial_weight: float,
        sentiment_weight: float,
    ) -> tuple[float, float]:
        """
        Normalize weights so that:

            financial_weight + sentiment_weight = 1
        """

        try:
            financial_weight = float(
                financial_weight
            )
        except (
            TypeError,
            ValueError,
        ):
            financial_weight = 0.0

        try:
            sentiment_weight = float(
                sentiment_weight
            )
        except (
            TypeError,
            ValueError,
        ):
            sentiment_weight = 0.0

        financial_weight = max(
            0.0,
            financial_weight,
        )

        sentiment_weight = max(
            0.0,
            sentiment_weight,
        )

        total = (
            financial_weight
            + sentiment_weight
        )

        if total <= 0:

            return (
                self.DEFAULT_FINANCIAL_WEIGHT,
                self.DEFAULT_SENTIMENT_WEIGHT,
            )

        return (
            financial_weight / total,
            sentiment_weight / total,
        )

    # ---------------------------------------------------------
    # Data-quality adjusted weights
    # ---------------------------------------------------------

    def _calculate_effective_weights(
        self,
        financial_weight: float,
        sentiment_weight: float,
        financial_data_quality: float,
        sentiment_data_quality: float,
    ) -> tuple[float, float]:
        """
        Adjust configured weights according to
        data quality.

        Example:

            configured:
                financial = 70%
                sentiment = 30%

            financial quality = 90
            sentiment quality = 50

        The financial component receives more
        effective influence because its underlying
        data is stronger.

        The resulting weights always sum to 1.
        """

        financial_effective = (
            financial_weight
            * (
                financial_data_quality
                / 100.0
            )
        )

        sentiment_effective = (
            sentiment_weight
            * (
                sentiment_data_quality
                / 100.0
            )
        )

        total = (
            financial_effective
            + sentiment_effective
        )

        if total <= 0:

            return (
                0.0,
                0.0,
            )

        return (
            financial_effective / total,
            sentiment_effective / total,
        )


score_normalizer = ScoreNormalizer()