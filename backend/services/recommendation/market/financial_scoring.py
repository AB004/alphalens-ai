from dataclasses import dataclass

from backend.services.recommendation.market.financial_feature_extractor import (
    FinancialFeatures,
)


@dataclass
class FinancialScore:
    """
    Result of financial scoring.

    Score range:
        -100 -> very weak
         0   -> neutral
        +100 -> very strong
    """

    score: float

    revenue_growth_score: float
    profit_growth_score: float
    eps_growth_score: float

    operating_margin_score: float
    net_margin_score: float

    roe_score: float
    roce_score: float

    debt_score: float
    cash_flow_score: float

    data_quality: float

    reasoning: list[str]


class FinancialScoringEngine:
    """
    Convert normalized FinancialFeatures into
    a deterministic financial score.

    This class does not use:
        - News
        - Sentiment
        - Market prices
        - AI/LLM

    It only evaluates company fundamentals.
    """

    # ---------------------------------------------------------
    # Feature weights
    # ---------------------------------------------------------

    WEIGHTS = {
        "revenue_growth": 0.15,
        "profit_growth": 0.20,
        "eps_growth": 0.10,
        "operating_margin": 0.10,
        "net_margin": 0.10,
        "roe": 0.10,
        "roce": 0.10,
        "debt": 0.05,
        "cash_flow": 0.10,
    }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def calculate(
        self,
        features: FinancialFeatures,
    ) -> FinancialScore:
        """
        Calculate the overall financial score.
        """

        revenue_growth_score = (
            self._score_growth(
                features.revenue_growth,
            )
        )

        profit_growth_score = (
            self._score_growth(
                features.profit_growth,
            )
        )

        eps_growth_score = (
            self._score_growth(
                features.eps_growth,
            )
        )

        operating_margin_score = (
            self._score_margin(
                features.operating_margin,
            )
        )

        net_margin_score = (
            self._score_margin(
                features.net_margin,
            )
        )

        roe_score = (
            self._score_return(
                features.roe,
            )
        )

        roce_score = (
            self._score_return(
                features.roce,
            )
        )

        debt_score = (
            self._score_debt(
                features.debt,
            )
        )

        cash_flow_score = (
            self._score_cash_flow(
                features.cash_flow,
            )
        )

        scores = {
            "revenue_growth": revenue_growth_score,
            "profit_growth": profit_growth_score,
            "eps_growth": eps_growth_score,
            "operating_margin": operating_margin_score,
            "net_margin": net_margin_score,
            "roe": roe_score,
            "roce": roce_score,
            "debt": debt_score,
            "cash_flow": cash_flow_score,
        }

        overall_score = self._weighted_score(
            scores,
            features,
        )

        reasoning = self._build_reasoning(
            features,
            scores,
        )

        return FinancialScore(
            score=round(
                overall_score,
                2,
            ),
            revenue_growth_score=round(
                revenue_growth_score,
                2,
            ),
            profit_growth_score=round(
                profit_growth_score,
                2,
            ),
            eps_growth_score=round(
                eps_growth_score,
                2,
            ),
            operating_margin_score=round(
                operating_margin_score,
                2,
            ),
            net_margin_score=round(
                net_margin_score,
                2,
            ),
            roe_score=round(
                roe_score,
                2,
            ),
            roce_score=round(
                roce_score,
                2,
            ),
            debt_score=round(
                debt_score,
                2,
            ),
            cash_flow_score=round(
                cash_flow_score,
                2,
            ),
            data_quality=round(
                features.data_quality,
                2,
            ),
            reasoning=reasoning,
        )

    # ---------------------------------------------------------
    # Growth scoring
    # ---------------------------------------------------------

    def _score_growth(
        self,
        value: float | None,
    ) -> float:
        """
        Score growth percentages.

        Approximate scale:

            >= 25%  -> +100
            15%     -> +70
            10%     -> +50
             5%     -> +25
             0%     -> 0
            -5%     -> -25
           -10%     -> -50
           -15%     -> -70
           <= -25% -> -100
        """

        if value is None:
            return 0.0

        if value >= 25:
            return 100.0

        if value >= 15:
            return 70.0

        if value >= 10:
            return 50.0

        if value >= 5:
            return 25.0

        if value >= 0:
            return 0.0

        if value >= -5:
            return -25.0

        if value >= -10:
            return -50.0

        if value >= -15:
            return -70.0

        if value >= -25:
            return -85.0

        return -100.0

    # ---------------------------------------------------------
    # Margin scoring
    # ---------------------------------------------------------

    def _score_margin(
        self,
        value: float | None,
    ) -> float:
        """
        Score operating/net margins.

        This is intentionally generic because
        acceptable margins vary significantly
        between industries.
        """

        if value is None:
            return 0.0

        if value >= 30:
            return 100.0

        if value >= 20:
            return 80.0

        if value >= 15:
            return 60.0

        if value >= 10:
            return 40.0

        if value >= 5:
            return 20.0

        if value >= 0:
            return 0.0

        if value >= -5:
            return -30.0

        if value >= -10:
            return -60.0

        return -100.0

    # ---------------------------------------------------------
    # ROE / ROCE scoring
    # ---------------------------------------------------------

    def _score_return(
        self,
        value: float | None,
    ) -> float:
        """
        Score ROE / ROCE.

        Approximate scale:

            >= 25% -> +100
            >= 20% -> +80
            >= 15% -> +60
            >= 10% -> +35
            >=  5% -> +15
               0%  -> 0
            <  0%  -> negative
        """

        if value is None:
            return 0.0

        if value >= 25:
            return 100.0

        if value >= 20:
            return 80.0

        if value >= 15:
            return 60.0

        if value >= 10:
            return 35.0

        if value >= 5:
            return 15.0

        if value >= 0:
            return 0.0

        if value >= -10:
            return -50.0

        return -100.0

    # ---------------------------------------------------------
    # Debt scoring
    # ---------------------------------------------------------

    def _score_debt(
        self,
        value: float | None,
    ) -> float:
        """
        Score absolute debt.

        Debt cannot be evaluated reliably in isolation
        without knowing company size.

        Therefore this is intentionally conservative.

        Phase 3 treats:
            no debt -> positive
            zero/low -> neutral/positive
            high absolute debt -> mildly negative

        A future version can use:
            Debt / Equity
            Debt / EBITDA
            Debt / Assets
        instead.
        """

        if value is None:
            return 0.0

        if value == 0:
            return 80.0

        if value < 0:
            return 0.0

        # Absolute debt alone isn't enough to determine
        # whether debt is dangerous.
        return -10.0

    # ---------------------------------------------------------
    # Cash flow scoring
    # ---------------------------------------------------------

    def _score_cash_flow(
        self,
        value: float | None,
    ) -> float:
        """
        Score operating/free cash flow.

        Positive cash flow is considered supportive.
        Negative cash flow is considered negative.
        """

        if value is None:
            return 0.0

        if value > 0:
            return 70.0

        if value == 0:
            return 0.0

        return -70.0

    # ---------------------------------------------------------
    # Weighted score
    # ---------------------------------------------------------

    def _weighted_score(
        self,
        scores: dict[str, float],
        features: FinancialFeatures,
    ) -> float:
        """
        Calculate weighted financial score.

        Missing metrics contribute zero, but the final
        score is adjusted for data completeness.
        """

        weighted_sum = 0.0
        available_weight = 0.0

        feature_values = {
            "revenue_growth": features.revenue_growth,
            "profit_growth": features.profit_growth,
            "eps_growth": features.eps_growth,
            "operating_margin": features.operating_margin,
            "net_margin": features.net_margin,
            "roe": features.roe,
            "roce": features.roce,
            "debt": features.debt,
            "cash_flow": features.cash_flow,
        }

        for name, weight in self.WEIGHTS.items():

            value = feature_values[name]

            if value is None:
                continue

            weighted_sum += (
                scores[name] * weight
            )

            available_weight += weight

        if available_weight == 0:
            return 0.0

        # Normalize based on the metrics actually available.
        normalized_score = (
            weighted_sum
            / available_weight
        )

        return max(
            -100.0,
            min(
                100.0,
                normalized_score,
            ),
        )

    # ---------------------------------------------------------
    # Reasoning
    # ---------------------------------------------------------

    def _build_reasoning(
        self,
        features: FinancialFeatures,
        scores: dict[str, float],
    ) -> list[str]:
        """
        Generate deterministic financial reasoning.

        This is NOT an LLM explanation.
        """

        reasoning: list[str] = []

        self._add_growth_reason(
            reasoning,
            "Revenue growth",
            features.revenue_growth,
        )

        self._add_growth_reason(
            reasoning,
            "Profit growth",
            features.profit_growth,
        )

        self._add_growth_reason(
            reasoning,
            "EPS growth",
            features.eps_growth,
        )

        self._add_margin_reason(
            reasoning,
            "Operating margin",
            features.operating_margin,
        )

        self._add_margin_reason(
            reasoning,
            "Net margin",
            features.net_margin,
        )

        self._add_return_reason(
            reasoning,
            "ROE",
            features.roe,
        )

        self._add_return_reason(
            reasoning,
            "ROCE",
            features.roce,
        )

        if features.debt is not None:

            if features.debt == 0:
                reasoning.append(
                    "The company has no reported debt."
                )

            else:
                reasoning.append(
                    "The company has reported debt; "
                    "its significance should be evaluated "
                    "relative to company size."
                )

        if features.cash_flow is not None:

            if features.cash_flow > 0:
                reasoning.append(
                    "Cash flow is positive."
                )

            elif features.cash_flow < 0:
                reasoning.append(
                    "Cash flow is negative."
                )

            else:
                reasoning.append(
                    "Cash flow is approximately zero."
                )

        if features.data_quality < 50:

            reasoning.append(
                "Financial data coverage is limited, "
                "so the financial score should be "
                "interpreted cautiously."
            )

        elif features.data_quality < 75:

            reasoning.append(
                "Some financial metrics are unavailable; "
                "the financial score is based on partial data."
            )

        else:

            reasoning.append(
                "Most required financial metrics are available."
            )

        return reasoning

    # ---------------------------------------------------------
    # Reason helpers
    # ---------------------------------------------------------

    def _add_growth_reason(
        self,
        reasoning: list[str],
        name: str,
        value: float | None,
    ):
        if value is None:
            return

        if value > 10:

            reasoning.append(
                f"{name} is strong at "
                f"{value:.2f}%."
            )

        elif value > 0:

            reasoning.append(
                f"{name} is positive at "
                f"{value:.2f}%."
            )

        elif value == 0:

            reasoning.append(
                f"{name} is flat."
            )

        else:

            reasoning.append(
                f"{name} is negative at "
                f"{value:.2f}%."
            )

    def _add_margin_reason(
        self,
        reasoning: list[str],
        name: str,
        value: float | None,
    ):
        if value is None:
            return

        if value >= 15:

            reasoning.append(
                f"{name} is strong at "
                f"{value:.2f}%."
            )

        elif value >= 5:

            reasoning.append(
                f"{name} is positive at "
                f"{value:.2f}%."
            )

        elif value >= 0:

            reasoning.append(
                f"{name} is low at "
                f"{value:.2f}%."
            )

        else:

            reasoning.append(
                f"{name} is negative at "
                f"{value:.2f}%."
            )

    def _add_return_reason(
        self,
        reasoning: list[str],
        name: str,
        value: float | None,
    ):
        if value is None:
            return

        if value >= 15:

            reasoning.append(
                f"{name} is strong at "
                f"{value:.2f}%."
            )

        elif value >= 10:

            reasoning.append(
                f"{name} is healthy at "
                f"{value:.2f}%."
            )

        elif value >= 0:

            reasoning.append(
                f"{name} is positive but modest at "
                f"{value:.2f}%."
            )

        else:

            reasoning.append(
                f"{name} is negative at "
                f"{value:.2f}%."
            )


financial_scoring_engine = (
    FinancialScoringEngine()
)