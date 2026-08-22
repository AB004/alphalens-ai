from dataclasses import dataclass
from typing import Any

from backend.models.financial_statement import FinancialStatement


@dataclass
class FinancialFeatures:
    """
    Normalized financial features used by
    the Module 10 recommendation engine.
    """

    revenue_growth: float | None = None
    profit_growth: float | None = None
    eps_growth: float | None = None

    operating_margin: float | None = None
    net_margin: float | None = None

    roe: float | None = None
    roce: float | None = None

    debt: float | None = None
    cash_flow: float | None = None

    fiscal_year: int | None = None

    data_quality: float = 0.0


class FinancialFeatureExtractor:
    """
    Extract normalized financial features from
    Module 7 financial statements.

    Input:
        FinancialStatement rows

    Output:
        FinancialFeatures
    """

    # ---------------------------------------------------------
    # Metric aliases
    # ---------------------------------------------------------

    REVENUE_KEYS = (
        "Total Revenue",
        "Operating Revenue",
        "Revenue",
        "TotalRevenue",
        "OperatingRevenue",
    )

    NET_INCOME_KEYS = (
        "Net Income",
        "NetIncome",
        "Net Income Common Stockholders",
        "NetIncomeCommonStockholders",
    )

    EPS_KEYS = (
        "Diluted EPS",
        "Basic EPS",
        "DilutedEPS",
        "BasicEPS",
    )

    OPERATING_INCOME_KEYS = (
        "Operating Income",
        "OperatingIncome",
    )

    NET_MARGIN_KEYS = (
        "Net Margin",
        "NetMargin",
    )

    ROE_KEYS = (
        "Return on Equity",
        "ReturnOnEquity",
        "ROE",
    )

    ROCE_KEYS = (
        "Return on Capital Employed",
        "ReturnOnCapitalEmployed",
        "ROCE",
    )

    DEBT_KEYS = (
        "Total Debt",
        "TotalDebt",
        "Long Term Debt",
        "LongTermDebt",
        "Long Term Debt And Capital Lease Obligation",
        "LongTermDebtAndCapitalLeaseObligation",
    )

    CASH_FLOW_KEYS = (
        "Operating Cash Flow",
        "OperatingCashFlow",
        "Total Cash From Operating Activities",
        "TotalCashFromOperatingActivities",
        "Free Cash Flow",
        "FreeCashFlow",
    )

    ASSET_KEYS = (
        "Total Assets",
        "TotalAssets",
    )

    EQUITY_KEYS = (
        "Stockholders Equity",
        "StockholdersEquity",
        "Total Equity Gross Minority Interest",
        "TotalEquityGrossMinorityInterest",
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def extract(
        self,
        statements: list[FinancialStatement],
    ) -> FinancialFeatures:
        """
        Extract normalized financial features.

        Statements are expected to come from Module 7's
        get_latest_financials() repository method.
        """

        if not statements:
            return FinancialFeatures()

        grouped = self._group_statements(
            statements,
        )

        income_statements = grouped.get(
            "income_statement",
            [],
        )

        balance_sheets = grouped.get(
            "balance_sheet",
            [],
        )

        cash_flows = grouped.get(
            "cash_flow",
            [],
        )

        latest_income = self._latest(
            income_statements,
        )

        previous_income = self._previous(
            income_statements,
        )

        latest_balance = self._latest(
            balance_sheets,
        )

        latest_cash_flow = self._latest(
            cash_flows,
        )

        revenue = self._get_value(
            latest_income,
            self.REVENUE_KEYS,
        )

        previous_revenue = self._get_value(
            previous_income,
            self.REVENUE_KEYS,
        )

        net_income = self._get_value(
            latest_income,
            self.NET_INCOME_KEYS,
        )

        previous_net_income = self._get_value(
            previous_income,
            self.NET_INCOME_KEYS,
        )

        eps = self._get_value(
            latest_income,
            self.EPS_KEYS,
        )

        previous_eps = self._get_value(
            previous_income,
            self.EPS_KEYS,
        )

        operating_income = self._get_value(
            latest_income,
            self.OPERATING_INCOME_KEYS,
        )

        equity = self._get_value(
            latest_balance,
            self.EQUITY_KEYS,
        )

        assets = self._get_value(
            latest_balance,
            self.ASSET_KEYS,
        )

        debt = self._get_value(
            latest_balance,
            self.DEBT_KEYS,
        )

        cash_flow = self._get_value(
            latest_cash_flow,
            self.CASH_FLOW_KEYS,
        )

        operating_margin = self._calculate_ratio(
            operating_income,
            revenue,
        )

        net_margin = self._calculate_ratio(
            net_income,
            revenue,
        )

        roe = self._get_value(
            latest_income,
            self.ROE_KEYS,
        )

        if roe is None:
            roe = self._calculate_ratio(
                net_income,
                equity,
            )

        roce = self._get_value(
            latest_income,
            self.ROCE_KEYS,
        )

        if roce is None:
            roce = self._calculate_roce(
                operating_income,
                debt,
                equity,
            )

        revenue_growth = self._calculate_growth(
            revenue,
            previous_revenue,
        )

        profit_growth = self._calculate_growth(
            net_income,
            previous_net_income,
        )

        eps_growth = self._calculate_growth(
            eps,
            previous_eps,
        )

        data_quality = self._calculate_data_quality(
            revenue=revenue,
            profit_growth=profit_growth,
            operating_margin=operating_margin,
            net_margin=net_margin,
            roe=roe,
            roce=roce,
            debt=debt,
            cash_flow=cash_flow,
        )

        latest_year = self._get_latest_year(
            statements,
        )

        return FinancialFeatures(
            revenue_growth=revenue_growth,
            profit_growth=profit_growth,
            eps_growth=eps_growth,
            operating_margin=operating_margin,
            net_margin=net_margin,
            roe=roe,
            roce=roce,
            debt=debt,
            cash_flow=cash_flow,
            fiscal_year=latest_year,
            data_quality=data_quality,
        )

    # ---------------------------------------------------------
    # Group statements
    # ---------------------------------------------------------

    def _group_statements(
        self,
        statements: list[FinancialStatement],
    ) -> dict[str, list[FinancialStatement]]:
        """
        Group statements by statement type.
        """

        grouped: dict[
            str,
            list[FinancialStatement],
        ] = {}

        for statement in statements:

            statement_type = (
                statement.statement_type
            )

            grouped.setdefault(
                statement_type,
                [],
            ).append(statement)

        return grouped

    # ---------------------------------------------------------
    # Latest / previous
    # ---------------------------------------------------------

    def _latest(
        self,
        statements: list[FinancialStatement],
    ) -> FinancialStatement | None:
        """
        Return the latest financial statement.
        """

        if not statements:
            return None

        return max(
            statements,
            key=lambda statement: (
                statement.report_date
                or ""
            ),
        )

    def _previous(
        self,
        statements: list[FinancialStatement],
    ) -> FinancialStatement | None:
        """
        Return the previous financial statement.
        """

        if len(statements) < 2:
            return None

        ordered = sorted(
            statements,
            key=lambda statement: (
                statement.report_date
                or ""
            ),
            reverse=True,
        )

        return ordered[1]

    # ---------------------------------------------------------
    # Value extraction
    # ---------------------------------------------------------

    def _get_value(
        self,
        statement: FinancialStatement | None,
        keys: tuple[str, ...],
    ) -> float | None:
        """
        Find a metric using known aliases.
        """

        if statement is None:
            return None

        data = statement.data

        if not isinstance(data, dict):
            return None

        # Exact aliases first
        for key in keys:

            if key not in data:
                continue

            value = self._to_float(
                data[key],
            )

            if value is not None:
                return value

        # Case-insensitive fallback
        normalized_data = {
            self._normalize_key(key): value
            for key, value in data.items()
        }

        for key in keys:

            normalized_key = self._normalize_key(
                key,
            )

            if normalized_key not in normalized_data:
                continue

            value = self._to_float(
                normalized_data[normalized_key],
            )

            if value is not None:
                return value

        return None

    # ---------------------------------------------------------
    # Numeric conversion
    # ---------------------------------------------------------

    def _to_float(
        self,
        value: Any,
    ) -> float | None:
        """
        Safely convert a value to float.
        """

        if value is None:
            return None

        try:

            if hasattr(value, "item"):
                value = value.item()

            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # ---------------------------------------------------------
    # Key normalization
    # ---------------------------------------------------------

    def _normalize_key(
        self,
        key: str,
    ) -> str:
        """
        Normalize financial metric names.

        Example:

        'Total Revenue'
            ->
        'totalrevenue'
        """

        return (
            str(key)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

    # ---------------------------------------------------------
    # Growth
    # ---------------------------------------------------------

    def _calculate_growth(
        self,
        current: float | None,
        previous: float | None,
    ) -> float | None:
        """
        Calculate year-over-year growth percentage.
        """

        if current is None:
            return None

        if previous is None:
            return None

        if previous == 0:
            return None

        return (
            (current - previous)
            / abs(previous)
        ) * 100

    # ---------------------------------------------------------
    # Ratio
    # ---------------------------------------------------------

    def _calculate_ratio(
        self,
        numerator: float | None,
        denominator: float | None,
    ) -> float | None:
        """
        Calculate percentage ratio.
        """

        if numerator is None:
            return None

        if denominator is None:
            return None

        if denominator == 0:
            return None

        return (
            numerator
            / denominator
        ) * 100

    # ---------------------------------------------------------
    # ROCE
    # ---------------------------------------------------------

    def _calculate_roce(
        self,
        operating_income: float | None,
        debt: float | None,
        equity: float | None,
    ) -> float | None:
        """
        Calculate approximate ROCE.

        Capital employed =
            Debt + Equity
        """

        if operating_income is None:
            return None

        if debt is None:
            debt = 0

        if equity is None:
            return None

        capital_employed = (
            debt + equity
        )

        if capital_employed == 0:
            return None

        return (
            operating_income
            / capital_employed
        ) * 100

    # ---------------------------------------------------------
    # Data quality
    # ---------------------------------------------------------

    def _calculate_data_quality(
        self,
        **features: Any,
    ) -> float:
        """
        Calculate financial data completeness.

        Returns:
            0 → no usable data
            100 → all required features available
        """

        if not features:
            return 0.0

        available = sum(
            value is not None
            for value in features.values()
        )

        return (
            available
            / len(features)
        ) * 100

    # ---------------------------------------------------------
    # Latest year
    # ---------------------------------------------------------

    def _get_latest_year(
        self,
        statements: list[FinancialStatement],
    ) -> int | None:
        """
        Return latest fiscal year.
        """

        years = [
            statement.fiscal_year
            for statement in statements
            if statement.fiscal_year is not None
        ]

        if not years:
            return None

        return max(years)


financial_feature_extractor = (
    FinancialFeatureExtractor()
)