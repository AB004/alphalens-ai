from typing import Any, Protocol


class CompanyProvider(Protocol):
    """
    Interface for external company data providers.
    """

    def get_company_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        ...

    def get_income_statements(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:
        ...

    def get_balance_sheets(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:
        ...

    def get_cash_flows(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:
        ...

    def get_company_data(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        ...