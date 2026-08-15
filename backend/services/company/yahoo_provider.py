from typing import Any

import pandas as pd
import yfinance as yf

from backend.services.company.provider import CompanyProvider


class YahooFinanceProvider(CompanyProvider):
    """
    Yahoo Finance implementation of CompanyProvider.
    """

    def _resolve_symbol(
        self,
        symbol: str,
    ) -> str:
        """
        Convert an AlphaLens symbol into a Yahoo Finance symbol.

        Examples:
            TCS       -> TCS.NS
            INFY      -> INFY.NS
            RELIANCE  -> RELIANCE.NS
            AAPL      -> AAPL.NS

        Already-qualified symbols are returned unchanged.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Company symbol is required."
            )

        if "." in symbol:
            return symbol

        return f"{symbol}.NS"

    def _ticker(
        self,
        symbol: str,
    ) -> yf.Ticker:
        """
        Return a yfinance ticker instance.
        """

        yahoo_symbol = self._resolve_symbol(
            symbol,
        )

        return yf.Ticker(
            yahoo_symbol,
        )

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
                    "report_date": report_date.strftime(
                        "%Y-%m-%d"
                    ),
                    "data": report,
                }
            )

        return statements

    def _get_company_profile(
        self,
        ticker: yf.Ticker,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Fetch and normalize company profile.
        """

        info = ticker.info

        if not info:

            raise ValueError(
                f"Company information not found "
                f"for '{symbol}'."
            )

        company_name = (
            info.get("longName")
            or info.get("shortName")
        )

        if not company_name:

            raise ValueError(
                f"Company name could not be resolved "
                f"for '{symbol}'."
            )

        return {
            # Keep AlphaLens symbol, not Yahoo symbol.
            "symbol": symbol.upper(),

            "company_name": company_name,

            "sector": info.get(
                "sector",
            ),

            "industry": info.get(
                "industry",
            ),

            "exchange": info.get(
                "exchange",
            ),

            "currency": info.get(
                "currency",
            ),

            "country": info.get(
                "country",
            ),

            "website": info.get(
                "website",
            ),
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

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Company symbol is required."
            )

        ticker = self._ticker(
            symbol,
        )

        return {
            "profile": self._get_company_profile(
                ticker,
                symbol,
            ),

            "income_statements": (
                self._get_income_statements(
                    ticker,
                )
            ),

            "balance_sheets": (
                self._get_balance_sheets(
                    ticker,
                )
            ),

            "cash_flows": (
                self._get_cash_flows(
                    ticker,
                )
            ),
        }