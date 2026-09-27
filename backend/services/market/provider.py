"""
Interface for Market Data Providers.
Follows Interface Segregation Principle (ISP) and Dependency Inversion Principle (DIP).
"""

from typing import Any, Protocol


class MarketDataProvider(Protocol):
    """Protocol for fetching market indices and stock quotes from external APIs."""

    def fetch_index_quotes(
        self,
        indices: list[str],
    ) -> list[dict[str, Any]]:
        """Fetch quotes for a list of market index symbols."""
        ...

    def fetch_ipo_details(self) -> list[dict[str, Any]]:
        """Fetch IPO metadata for both mainboard and SME exchanges."""
        ...

    def fetch_ipo_daily_performance(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch daily OHLCV performance for a listed IPO symbol."""
        ...

    def fetch_market_news(self, limit: int = 20) -> list[dict[str, Any]]:
        """Fetch latest market news items."""
        ...

    def fetch_macro_indicators(self) -> list[dict[str, Any]]:
        """Fetch current macro economic indicators."""
        ...

    def fetch_currency_rates(self) -> list[dict[str, Any]]:
        """Fetch current currency exchange rates."""
        ...

