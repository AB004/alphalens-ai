from typing import Any

import pandas as pd
import yfinance as yf

from backend.services.company.provider import CompanyProvider


class YahooFinanceProvider(CompanyProvider):
    """
    Yahoo Finance implementation of CompanyProvider.
    """

    def _ticker(
        self,
        symbol: str,
    ) -> yf.Ticker:
        """
        Return a yfinance ticker instance.
        """

        return yf.Ticker(symbol.upper())


    def _normalize_statement(
        self,
        dataframe: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Convert a Yahoo Finance DataFrame into a
        normalized list of financial statements.
        """

        if dataframe.empty:
            return []

        dataframe = dataframe.transpose()

        statements = []

        for report_date, row in dataframe.iterrows():

            report = {}

            for key, value in row.items():

                if pd.isna(value):
                    report[key] = None

                elif hasattr(value, "item"):
                    report[key] = value.item()

                else:
                    report[key] = value

            statements.append(
                {
                    "fiscal_year": report_date.year,
                    "report_date": report_date.strftime("%Y-%m-%d"),
                    "data": report,
                }
            )

        return statements

    def _get_company_profile(
        self,
        ticker: yf.Ticker,
    ) -> dict[str, Any]:

        info = ticker.info

        if not info:
            raise ValueError(
                "Company information not found."
            )

        return {
            "symbol": info.get("symbol"),
            "company_name": info.get("longName")
            or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "country": info.get("country"),
            "website": info.get("website"),
        }

    def _get_income_statements(
        self,
        ticker: yf.Ticker,
    ) -> list[dict[str, Any]]:

        dataframe = ticker.financials

        if dataframe.empty:
            return []

        return self._normalize_statement(
            dataframe,
        )

    def _get_balance_sheets(
     self,
        ticker: yf.Ticker,
    ) -> list[dict[str, Any]]:

        dataframe = ticker.balance_sheet

        if dataframe.empty:
            return []

        return self._normalize_statement(
            dataframe,
        )

    def _get_cash_flows(
        self,
        ticker: yf.Ticker,
    ) -> list[dict[str, Any]]:

        dataframe = ticker.cash_flow

        if dataframe.empty:
            return []

        return self._normalize_statement(
            dataframe,
        )

    def get_company_data(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Fetch all company data using a single
        Ticker instance.
        """

        ticker = self._ticker(symbol)

        return {
            "profile": self._get_company_profile(
                ticker,
            ),
            "income_statements": self._get_income_statements(
                ticker,
            ),
            "balance_sheets": self._get_balance_sheets(
                ticker,
            ),
            "cash_flows": self._get_cash_flows(
                ticker,
            ),
        }