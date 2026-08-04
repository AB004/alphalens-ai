from typing import Any


BUY_THRESHOLD = 75
HOLD_THRESHOLD = 50
MAX_SCORE = 100


class FinancialScorer:

    def __init__(self, report: dict[str, Any]):
        self.report = report
        self.score = 50.0          # Neutral starting score
        self.reasons: list[str] = []

    def calculate(self) -> dict[str, Any]:
        self._score_financial_metrics()
        self._score_swot()
        self._score_risks()
        self._normalize_score()

        recommendation = self._recommendation()
        confidence = self._confidence()

        return {
            "score": self.score,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasons": self.reasons,
        }

    def _score_financial_metrics(self):
        metrics = self.report.get("financial_metrics", [])

        for metric in metrics:

            metric_name = (
                metric.get("metric", "")
                .lower()
                .strip()
            )

            value = (
                str(metric.get("value", ""))
                .lower()
            )

            if "revenue" in metric_name:
                self.score += 8
                self.reasons.append("Revenue information available")

            elif "profit" in metric_name:
                self.score += 10
                self.reasons.append("Profit information available")

            elif "cash" in metric_name:
                self.score += 8
                self.reasons.append("Cash flow identified")

            elif "debt" in metric_name:
                if "high" in value:
                    self.score -= 10
                    self.reasons.append("High debt detected")
                else:
                    self.score += 5
                    self.reasons.append("Debt appears manageable")

    def _score_swot(self):
        swot = self.report.get("swot", {})

        strengths = swot.get("strengths", [])
        weaknesses = swot.get("weaknesses", [])
        opportunities = swot.get("opportunities", [])
        threats = swot.get("threats", [])

        self.score += min(len(strengths) * 2, 10)
        self.score += min(len(opportunities) * 2, 10)

        self.score -= min(len(weaknesses) * 2, 10)
        self.score -= min(len(threats) * 2, 10)

    def _score_risks(self):
        risks = self.report.get("risks", [])

        self.score -= min(len(risks) * 3, 15)

        if risks:
            self.reasons.append(
                f"{len(risks)} major risks identified"
            )

    def _normalize_score(self):
        self.score = max(
            0,
            min(MAX_SCORE, round(self.score, 2))
        )

    def _recommendation(self) -> str:
        if self.score >= BUY_THRESHOLD:
            return "BUY"

        if self.score >= HOLD_THRESHOLD:
            return "HOLD"

        return "SELL"

    def _confidence(self) -> float:
        distance = abs(self.score - 50)

        confidence = 60 + (distance * 0.8)

        return round(min(confidence, 95), 2)