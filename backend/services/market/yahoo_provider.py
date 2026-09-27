"""
Yahoo Finance implementation of the MarketDataProvider protocol.
Fetches real-time and historical quotes for market indices and stocks.
"""

import logging
from typing import Any, List
import yfinance as yf

from backend.services.market.provider import MarketDataProvider

logger = logging.getLogger(__name__)


class YahooMarketDataProvider(MarketDataProvider):
    """Fetches market indices and stock quotes using yfinance."""

    def _resolve_symbol(self, symbol: str) -> str:
        """
        Normalize symbol for Yahoo Finance:
        - Indices (starting with ^) are kept as-is (e.g., ^NSEI, ^BSESN)
        - Already qualified tickers (with .NS, .BO, .US, etc.) kept as-is
        - Plain Indian stock symbols get appended with '.NS'
        """
        s = symbol.strip().upper()
        if s.startswith("^") or "." in s:
            return s
        return f"{s}.NS"

    def fetch_index_quotes(self, indices: List[str]) -> List[dict[str, Any]]:
        """Fetch quotes for major market indices."""
        results = []
        for symbol in indices:
            yahoo_symbol = self._resolve_symbol(symbol)
            try:
                ticker = yf.Ticker(yahoo_symbol)
                fast = getattr(ticker, "fast_info", None)
                if not fast:
                    continue

                last_price = float(getattr(fast, "last_price", 0.0) or 0.0)
                prev_close = float(getattr(fast, "previous_close", 0.0) or 0.0)
                if last_price <= 0:
                    continue

                change = round(last_price - prev_close, 2) if prev_close else 0.0
                pct_change = round((change / prev_close) * 100.0, 2) if prev_close else 0.0

                results.append({
                    "symbol": symbol.upper().strip(),
                    "current_value": round(last_price, 2),
                    "change": change,
                    "percent_change": pct_change,
                    "open_value": round(float(getattr(fast, "open", 0.0) or last_price), 2),
                    "high_value": round(float(getattr(fast, "day_high", 0.0) or last_price), 2),
                    "low_value": round(float(getattr(fast, "day_low", 0.0) or last_price), 2),
                    "previous_close": round(prev_close, 2),
                })
            except Exception as exc:
                logger.warning("Failed to fetch index %s: %s", symbol, exc)
                continue
        return results

    def fetch_stock_quotes(self, symbols: List[str]) -> List[dict[str, Any]]:
        """Fetch quotes for stock symbols."""
        results = []
        for symbol in symbols:
            yahoo_symbol = self._resolve_symbol(symbol)
            try:
                ticker = yf.Ticker(yahoo_symbol)
                fast = getattr(ticker, "fast_info", None)
                if not fast:
                    continue

                last_price = float(getattr(fast, "last_price", 0.0) or 0.0)
                prev_close = float(getattr(fast, "previous_close", 0.0) or 0.0)
                if last_price <= 0:
                    continue

                change = round(last_price - prev_close, 2) if prev_close else 0.0
                pct_change = round((change / prev_close) * 100.0, 2) if prev_close else 0.0

                day_high = round(float(getattr(fast, "day_high", 0.0) or last_price), 2)
                day_low = round(float(getattr(fast, "day_low", 0.0) or last_price), 2)
                day_open = round(float(getattr(fast, "open", 0.0) or last_price), 2)
                vol = int(getattr(fast, "last_volume", 0) or 0)
                avg_vol = int(getattr(fast, "ten_day_average_volume", 0) or 0)
                surge = round(vol / avg_vol, 2) if avg_vol > 0 else 1.0

                results.append({
                    "symbol": symbol.upper().strip(),
                    "current_price": round(last_price, 2),
                    "change": change,
                    "percent_change": pct_change,
                    "open_price": day_open,
                    "high_price": day_high,
                    "low_price": day_low,
                    "previous_close": round(prev_close, 2),
                    "volume": vol,
                    "avg_volume_10d": avg_vol,
                    "volume_surge_ratio": surge,
                    "high_52w": round(float(getattr(fast, "year_high", 0.0) or 0.0), 2),
                    "low_52w": round(float(getattr(fast, "year_low", 0.0) or 0.0), 2),
                    "market_cap": getattr(fast, "market_cap", None),
                })
            except Exception as exc:
                logger.warning("Failed to fetch stock quote %s: %s", symbol, exc)
                continue
        return results

    def fetch_ipo_details(self) -> List[dict[str, Any]]:
        """
        Fetch IPO metadata.
        Yahoo Finance does not expose a dedicated IPO calendar API,
        so the service layer relies on curated seed data in the database.
        This method is provided for protocol compliance and future extension.
        Fetch official IPO metadata directly from NSE / BSE exchange APIs.
        Strictly connects only to official exchange endpoints.
        If unavailable, returns empty list so the service layer keeps existing data as-is.
        """
        logger.info("fetch_ipo_details: yfinance has no native IPO calendar; returning empty list (seed data used).")
        return []
        try:
            from backend.services.market.nse_ipo_provider import nse_bse_ipo_provider
            return nse_bse_ipo_provider.fetch_all_ipos()
        except Exception as exc:
            logger.warning("fetch_ipo_details: official NSE/BSE query failed: %s", exc)
            return []

    def fetch_ipo_daily_performance(self, symbol: str) -> List[dict[str, Any]]:
        """
        Fetch daily OHLCV performance for a recently listed IPO using yfinance history.
        Falls back gracefully if the symbol is not yet tradeable.
        """
        yahoo_symbol = self._resolve_symbol(symbol)
        try:
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="1mo")
            if hist.empty:
                logger.info("No trading history available for IPO symbol %s", symbol)
                return []

            results = []
            for trade_date, row in hist.iterrows():
                results.append({
                    "trade_date": trade_date.to_pydatetime(),
                    "open_price": round(float(row.get("Open", 0.0)), 2),
                    "close_price": round(float(row.get("Close", 0.0)), 2),
                    "high_price": round(float(row.get("High", 0.0)), 2),
                    "low_price": round(float(row.get("Low", 0.0)), 2),
                    "volume": int(row.get("Volume", 0)),
                    "pct_change": round(
                        ((float(row.get("Close", 0)) - float(row.get("Open", 0))) / float(row.get("Open", 1))) * 100, 2
                    ) if float(row.get("Open", 0)) > 0 else 0.0,
                })
            return results
        except Exception as exc:
            logger.warning("Failed to fetch IPO performance for %s: %s", symbol, exc)
            return []
