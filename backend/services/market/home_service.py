"""
Home Page and Market Overview Service.
Orchestrates business logic for:
- Market Overview & Major Indices
- Advance / Decline Market Breadth
- Top Gainers / Losers partitioned across Large, Mid, Small caps
- Sector Performance & Heatmap
- Sector Top Movers
- Quarterly Results (Upcoming & Recent)
- Watchlists (Default Trending & Custom User Watchlists)
- 52-Week High / Low Breakouts
- Volume Shockers & Most Active
- Market Sentiment Pulse
- Consolidated Master Home Page Dashboard

Implements resilient Multi-Tiered Caching:
1. Database Cache
2. Live Provider API Fetch
3. Curated Fallback Seed Data (Guarantees NEVER empty responses).
"""

from datetime import datetime, timezone, timedelta
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.repositories.market_repository import (
    add_watchlist_item as repo_add_watchlist_item,
    bulk_upsert_quarterly_results,
    bulk_upsert_quotes,
    count_indices,
    count_quotes,
    count_quarterly_results,
    get_52_week_highs,
    get_52_week_lows,
    get_indices,
    get_most_active,
    get_quarterly_results as repo_get_quarterly_results,
    get_quotes,
    get_quote_by_symbol,
    get_quotes_by_sector,
    get_quotes_by_symbols,
    get_sector_names,
    get_top_gainers,
    get_top_losers,
    get_volume_shockers,
    get_watchlist_items as repo_get_watchlist_items,
    remove_watchlist_item as repo_remove_watchlist_item,
    save_breadth_snapshot,
    upsert_index,
    upsert_quote,
    list_upcoming_ipos as repo_list_upcoming_ipos,
    list_recent_ipos as repo_list_recent_ipos,
    get_ipo_performance as repo_get_ipo_performance,
    upsert_ipo_detail,
    upsert_ipo_performance,
    get_ipo_by_symbol,
)
from backend.services.market.provider import MarketDataProvider
from backend.services.market.universe import (
    DEFAULT_INDICES,
    DEFAULT_IPOS,
    DEFAULT_QUARTERLY_RESULTS,
    DEFAULT_STOCKS,
    DEFAULT_WATCHLIST_SYMBOLS,
)
from backend.services.market.yahoo_provider import YahooMarketDataProvider

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HomeService:
    """Production service powering the AlphaLens Home Page."""

    QUOTE_CACHE_TTL = timedelta(minutes=10)
    INDEX_CACHE_TTL = timedelta(minutes=10)
    QUARTERLY_CACHE_TTL = timedelta(hours=24)

    def __init__(self, provider: Optional[MarketDataProvider] = None):
        self.provider = provider or YahooMarketDataProvider()

    # =========================================================================
    # SEEDING & RESILIENT CACHE MANAGEMENT
    # =========================================================================

    def ensure_seeded(self, db: Session, force_refresh: bool = False) -> None:
        """
        Ensures the database is populated with initial indices, stocks,
        quarterly results, and default watchlists.
        If data is missing or force_refresh is requested, hydrates from seed data.
        """
        quotes_count = count_quotes(db)
        indices_count = count_indices(db)
        quarterly_count = count_quarterly_results(db)

        # 1. Seed Indices if missing
        if indices_count == 0 or force_refresh:
            for idx in DEFAULT_INDICES:
                upsert_index(db, idx)

        # 2. Seed Stock Quotes if missing
        if quotes_count == 0 or force_refresh:
            bulk_upsert_quotes(db, DEFAULT_STOCKS)

        # 3. Seed Quarterly Results if missing
        if quarterly_count == 0 or force_refresh:
            bulk_upsert_quarterly_results(db, DEFAULT_QUARTERLY_RESULTS)

        # 4. Seed Default Watchlist items if missing
        existing_watchlist = repo_get_watchlist_items(db, user_id="default")
        if not existing_watchlist or force_refresh:
            for sym in DEFAULT_WATCHLIST_SYMBOLS:
                quote = get_quote_by_symbol(db, sym)
                name = quote.company_name if quote else sym
                repo_add_watchlist_item(
                    db=db,
                    user_id="default",
                    symbol=sym,
                    company_name=name,
                    category="bluechip",
                    notes="Top tracked bluechip on AlphaLens",
                )

    def refresh_from_provider(self, db: Session) -> dict[str, int]:
        """
        Attempts to fetch live data from external market API (yfinance)
        for tracked indices and stocks, updating the database.
        """
        indices_updated = 0
        quotes_updated = 0

        # Refresh Indices
        index_symbols = [idx["symbol"] for idx in DEFAULT_INDICES]
        try:
            live_indices = self.provider.fetch_index_quotes(index_symbols)
            for item in live_indices:
                name_match = next((i["name"] for i in DEFAULT_INDICES if i["symbol"] == item["symbol"]), item["symbol"])
                category_match = next((i["category"] for i in DEFAULT_INDICES if i["symbol"] == item["symbol"]), "benchmark")
                item["name"] = name_match
                item["category"] = category_match
                upsert_index(db, item)
                indices_updated += 1
        except Exception as exc:
            logger.warning("Could not refresh live indices: %s", exc)

        # Refresh Stocks
        stock_symbols = [s["symbol"] for s in DEFAULT_STOCKS]
        try:
            live_quotes = self.provider.fetch_stock_quotes(stock_symbols)
            for item in live_quotes:
                # Merge existing metadata like sector and cap category
                meta = next((s for s in DEFAULT_STOCKS if s["symbol"] == item["symbol"]), None)
                if meta:
                    item["company_name"] = meta["company_name"]
                    item["sector"] = meta["sector"]
                    item["market_cap_category"] = meta["market_cap_category"]
                    item["pe_ratio"] = meta.get("pe_ratio")
                    if not item.get("high_52w") or item["high_52w"] == 0.0:
                        item["high_52w"] = meta.get("high_52w")
                    if not item.get("low_52w") or item["low_52w"] == 0.0:
                        item["low_52w"] = meta.get("low_52w")
                upsert_quote(db, item)
                quotes_updated += 1
        except Exception as exc:
            logger.warning("Could not refresh live stock quotes: %s", exc)

        return {
            "indices_updated": indices_updated,
            "quotes_updated": quotes_updated,
        }

    # =========================================================================
    # 1. MARKET OVERVIEW
    # =========================================================================

    def _determine_market_status(self) -> dict[str, Any]:
        """
        Determines current trading status for Indian markets (IST: UTC+5:30).
        Exchange trading hours: Monday to Friday, 09:15 to 15:30 IST.
        """
        now = utc_now()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset

        weekday = ist_now.weekday()  # 0=Monday, 6=Sunday
        is_trading_day = weekday < 5

        ist_minutes = ist_now.hour * 60 + ist_now.minute
        market_open_minutes = 9 * 60 + 15    # 09:15 AM
        market_close_minutes = 15 * 60 + 30  # 03:30 PM
        pre_open_minutes = 9 * 60            # 09:00 AM

        if not is_trading_day:
            status = "CLOSED"
            message = "Market Closed (Weekend)"
            is_open = False
        elif ist_minutes < pre_open_minutes:
            status = "CLOSED"
            message = "Market Closed (Opens at 09:15 AM IST)"
            is_open = False
        elif pre_open_minutes <= ist_minutes < market_open_minutes:
            status = "PRE_MARKET"
            message = "Pre-Market Session"
            is_open = False
        elif market_open_minutes <= ist_minutes <= market_close_minutes:
            status = "OPEN"
            message = "Market is Open"
            is_open = True
        else:
            status = "CLOSED"
            message = "Market Closed"
            is_open = False

        return {
            "status": status,
            "is_open": is_open,
            "message": message,
            "exchange": "NSE / BSE",
            "timezone": "IST (UTC+5:30)",
            "server_time_utc": now.isoformat(),
        }

    def get_market_overview(
        self,
        db: Session,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Returns major indices, exchange status, and computed market mood."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        indices = get_indices(db)
        indices_data = [
            {
                "symbol": idx.symbol,
                "name": idx.name,
                "category": idx.category,
                "current_value": round(idx.current_value, 2),
                "change": round(idx.change, 2),
                "percent_change": round(idx.percent_change, 2),
                "open_value": round(idx.open_value, 2) if idx.open_value else None,
                "high_value": round(idx.high_value, 2) if idx.high_value else None,
                "low_value": round(idx.low_value, 2) if idx.low_value else None,
                "previous_close": round(idx.previous_close, 2) if idx.previous_close else None,
                "last_updated": idx.last_updated.isoformat(),
            }
            for idx in indices
        ]

        # Calculate mood score (-1.0 to 1.0)
        nifty = next((idx for idx in indices if idx.symbol == "^NSEI"), None)
        sensex = next((idx for idx in indices if idx.symbol == "^BSESN"), None)
        pct_sum = 0.0
        weight_count = 0
        if nifty:
            pct_sum += nifty.percent_change * 1.5
            weight_count += 1.5
        if sensex:
            pct_sum += sensex.percent_change * 1.0
            weight_count += 1.0

        avg_idx_change = (pct_sum / weight_count) if weight_count > 0 else 0.0

        # Market regime determination
        if avg_idx_change >= 1.0:
            regime = "Strongly Bullish"
            mood_score = min(1.0, round(0.5 + avg_idx_change / 3.0, 2))
        elif avg_idx_change >= 0.2:
            regime = "Bullish"
            mood_score = min(0.7, round(0.2 + avg_idx_change / 3.0, 2))
        elif avg_idx_change <= -1.0:
            regime = "Strongly Bearish"
            mood_score = max(-1.0, round(-0.5 + avg_idx_change / 3.0, 2))
        elif avg_idx_change <= -0.2:
            regime = "Bearish"
            mood_score = max(-0.7, round(-0.2 + avg_idx_change / 3.0, 2))
        else:
            regime = "Neutral"
            mood_score = round(avg_idx_change / 2.0, 2)

        market_status = self._determine_market_status()

        return {
            "market_status": market_status,
            "market_regime": regime,
            "mood_score": mood_score,
            "indices": indices_data,
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 2. ADVANCE / DECLINE (MARKET BREADTH)
    # =========================================================================

    def get_advance_decline(
        self,
        db: Session,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Calculates advances, declines, unchanged counts, and ADR."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        quotes = get_quotes(db, limit=500)
        total = len(quotes)
        advances = sum(1 for q in quotes if q.percent_change > 0)
        declines = sum(1 for q in quotes if q.percent_change < 0)
        unchanged = total - advances - declines

        adr = round(advances / declines, 2) if declines > 0 else float(advances)

        if adr >= 2.0:
            breadth_sentiment = "Strongly Bullish"
        elif adr >= 1.2:
            breadth_sentiment = "Bullish"
        elif adr <= 0.5:
            breadth_sentiment = "Strongly Bearish"
        elif adr <= 0.8:
            breadth_sentiment = "Bearish"
        else:
            breadth_sentiment = "Neutral"

        advance_pct = round((advances / total) * 100.0, 1) if total > 0 else 0.0
        decline_pct = round((declines / total) * 100.0, 1) if total > 0 else 0.0
        unchanged_pct = round((unchanged / total) * 100.0, 1) if total > 0 else 0.0

        overview = self.get_market_overview(db)
        status_info = overview["market_status"]["status"]
        regime = overview["market_regime"]
        mood = overview["mood_score"]

        # Persist breadth snapshot
        try:
            save_breadth_snapshot(
                db,
                {
                    "advances": advances,
                    "declines": declines,
                    "unchanged": unchanged,
                    "total_tracked": total,
                    "advance_decline_ratio": adr,
                    "market_status": status_info,
                    "market_regime": regime,
                    "mood_score": mood,
                },
            )
        except Exception as exc:
            logger.debug("Failed saving breadth snapshot: %s", exc)

        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "total_tracked": total,
            "advance_decline_ratio": adr,
            "advance_percentage": advance_pct,
            "decline_percentage": decline_pct,
            "unchanged_percentage": unchanged_pct,
            "breadth_sentiment": breadth_sentiment,
            "market_regime": regime,
            "mood_score": mood,
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 3. TOP GAINERS / LOSERS ACROSS MARKET CAPS
    # =========================================================================

    def _serialize_quote(self, q) -> dict[str, Any]:
        """Convert a StockQuote ORM object into a clean dictionary."""
        return {
            "symbol": q.symbol,
            "company_name": q.company_name,
            "sector": q.sector,
            "market_cap_category": q.market_cap_category,
            "current_price": round(q.current_price, 2),
            "change": round(q.change, 2),
            "percent_change": round(q.percent_change, 2),
            "open_price": round(q.open_price, 2) if q.open_price else None,
            "high_price": round(q.high_price, 2) if q.high_price else None,
            "low_price": round(q.low_price, 2) if q.low_price else None,
            "previous_close": round(q.previous_close, 2) if q.previous_close else None,
            "volume": q.volume or 0,
            "avg_volume_10d": q.avg_volume_10d or 0,
            "volume_surge_ratio": round(q.volume_surge_ratio, 2) if q.volume_surge_ratio else 1.0,
            "high_52w": round(q.high_52w, 2) if q.high_52w else None,
            "low_52w": round(q.low_52w, 2) if q.low_52w else None,
            "pe_ratio": round(q.pe_ratio, 1) if q.pe_ratio else None,
            "market_cap": q.market_cap,
            "last_updated": q.last_updated.isoformat(),
        }

    def get_market_movers(
        self,
        db: Session,
        cap: Optional[str] = None,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Returns top gainers, top losers, and most active stocks.
        Can be filtered by market cap: 'large', 'mid', 'small', or 'all'.
        """
        self.ensure_seeded(db, force_refresh=force_refresh)

        if cap and cap.lower() in ["large", "mid", "small"]:
            normalized_cap = cap.lower()
            gainers = get_top_gainers(db, cap_category=normalized_cap, limit=limit)
            losers = get_top_losers(db, cap_category=normalized_cap, limit=limit)
            most_active = get_most_active(db, limit=limit)

            return {
                "cap_filter": normalized_cap,
                "gainers": [self._serialize_quote(q) for q in gainers],
                "losers": [self._serialize_quote(q) for q in losers],
                "most_active": [self._serialize_quote(q) for q in most_active],
                "timestamp": utc_now().isoformat(),
            }

        # Multi-cap comprehensive view
        large_gainers = get_top_gainers(db, cap_category="large", limit=limit)
        large_losers = get_top_losers(db, cap_category="large", limit=limit)

        mid_gainers = get_top_gainers(db, cap_category="mid", limit=limit)
        mid_losers = get_top_losers(db, cap_category="mid", limit=limit)

        small_gainers = get_top_gainers(db, cap_category="small", limit=limit)
        small_losers = get_top_losers(db, cap_category="small", limit=limit)

        overall_gainers = get_top_gainers(db, limit=limit)
        overall_losers = get_top_losers(db, limit=limit)
        most_active = get_most_active(db, limit=limit)

        return {
            "cap_filter": "all",
            "large_cap": {
                "gainers": [self._serialize_quote(q) for q in large_gainers],
                "losers": [self._serialize_quote(q) for q in large_losers],
            },
            "mid_cap": {
                "gainers": [self._serialize_quote(q) for q in mid_gainers],
                "losers": [self._serialize_quote(q) for q in mid_losers],
            },
            "small_cap": {
                "gainers": [self._serialize_quote(q) for q in small_gainers],
                "losers": [self._serialize_quote(q) for q in small_losers],
            },
            "overall_gainers": [self._serialize_quote(q) for q in overall_gainers],
            "overall_losers": [self._serialize_quote(q) for q in overall_losers],
            "most_active": [self._serialize_quote(q) for q in most_active],
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 4. SECTOR PERFORMANCE & SECTOR TOP MOVERS
    # =========================================================================

    def get_sector_performance(
        self,
        db: Session,
        force_refresh: bool = False,
    ) -> List[dict[str, Any]]:
        """Returns sector performance summaries sorted by return descending."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        sector_names = get_sector_names(db)
        sectors_summary = []

        for sector in sector_names:
            quotes = get_quotes_by_sector(db, sector)
            if not quotes:
                continue

            stock_count = len(quotes)
            avg_change = round(sum(q.percent_change for q in quotes) / stock_count, 2)
            advances = sum(1 for q in quotes if q.percent_change > 0)
            declines = sum(1 for q in quotes if q.percent_change < 0)

            # Sorted by percent_change descending
            top_gainer = quotes[0] if quotes and quotes[0].percent_change > 0 else None
            top_loser = quotes[-1] if quotes and quotes[-1].percent_change < 0 else None

            if avg_change >= 1.5:
                momentum = "Leading"
            elif avg_change > 0:
                momentum = "Improving"
            elif avg_change <= -1.5:
                momentum = "Lagging"
            else:
                momentum = "Weakening"

            sectors_summary.append({
                "sector": sector,
                "stock_count": stock_count,
                "average_change_percent": avg_change,
                "advances": advances,
                "declines": declines,
                "momentum": momentum,
                "top_gainer": {
                    "symbol": top_gainer.symbol,
                    "company_name": top_gainer.company_name,
                    "percent_change": round(top_gainer.percent_change, 2),
                } if top_gainer else None,
                "top_loser": {
                    "symbol": top_loser.symbol,
                    "company_name": top_loser.company_name,
                    "percent_change": round(top_loser.percent_change, 2),
                } if top_loser else None,
            })

        sectors_summary.sort(key=lambda s: s["average_change_percent"], reverse=True)
        return sectors_summary

    def get_sector_movers(
        self,
        db: Session,
        sector_name: str,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Returns constituents, top gainers, and top losers for a specific sector."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        quotes = get_quotes_by_sector(db, sector_name)
        if not quotes:
            return {
                "sector": sector_name,
                "stock_count": 0,
                "average_change_percent": 0.0,
                "gainers": [],
                "losers": [],
                "constituents": [],
                "timestamp": utc_now().isoformat(),
            }

        stock_count = len(quotes)
        avg_change = round(sum(q.percent_change for q in quotes) / stock_count, 2)
        gainers = [self._serialize_quote(q) for q in quotes if q.percent_change > 0]
        losers = [self._serialize_quote(q) for q in reversed(quotes) if q.percent_change < 0]

        return {
            "sector": sector_name,
            "stock_count": stock_count,
            "average_change_percent": avg_change,
            "gainers": gainers,
            "losers": losers,
            "constituents": [self._serialize_quote(q) for q in quotes],
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 5. QUARTERLY RESULTS BASED STOCKS
    # =========================================================================

    def _serialize_quarterly_result(self, r) -> dict[str, Any]:
        return {
            "id": r.id,
            "symbol": r.symbol,
            "company_name": r.company_name,
            "sector": r.sector,
            "fiscal_year": r.fiscal_year,
            "quarter": r.quarter,
            "result_date": r.result_date.strftime("%Y-%m-%d") if r.result_date else None,
            "is_upcoming": r.is_upcoming,
            "revenue": r.revenue,
            "revenue_growth_yoy": r.revenue_growth_yoy,
            "net_profit": r.net_profit,
            "profit_growth_yoy": r.profit_growth_yoy,
            "verdict": r.verdict,
            "impact_percent": r.impact_percent,
            "key_highlights": r.key_highlights,
        }

    def get_quarterly_results(
        self,
        db: Session,
        status: str = "all",
        limit: int = 20,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Returns quarterly results filtered by status:
        'upcoming', 'recent' (declared), or 'all'.
        """
        self.ensure_seeded(db, force_refresh=force_refresh)

        status_lower = status.lower().strip()
        if status_lower == "upcoming":
            records = repo_get_quarterly_results(db, is_upcoming=True, limit=limit)
            return {
                "filter": "upcoming",
                "upcoming": [self._serialize_quarterly_result(r) for r in records],
                "recent": [],
                "timestamp": utc_now().isoformat(),
            }
        elif status_lower in ["recent", "declared"]:
            records = repo_get_quarterly_results(db, is_upcoming=False, limit=limit)
            return {
                "filter": "recent",
                "upcoming": [],
                "recent": [self._serialize_quarterly_result(r) for r in records],
                "timestamp": utc_now().isoformat(),
            }
        else:
            upcoming = repo_get_quarterly_results(db, is_upcoming=True, limit=limit)
            recent = repo_get_quarterly_results(db, is_upcoming=False, limit=limit)
            return {
                "filter": "all",
                "upcoming": [self._serialize_quarterly_result(r) for r in upcoming],
                "recent": [self._serialize_quarterly_result(r) for r in recent],
                "timestamp": utc_now().isoformat(),
            }

    # =========================================================================
    # 6. WATCHLIST BASED STOCKS
    # =========================================================================

    def get_watchlist(
        self,
        db: Session,
        user_id: str = "default",
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Returns watchlist items enriched with real-time stock quote metrics.
        If user has no items and user_id is 'default', seeds default items.
        """
        self.ensure_seeded(db, force_refresh=force_refresh)

        items = repo_get_watchlist_items(db, user_id=user_id)
        if not items and user_id == "default":
            self.ensure_seeded(db, force_refresh=True)
            items = repo_get_watchlist_items(db, user_id=user_id)

        symbols = [item.symbol for item in items]
        quotes_map = {q.symbol: q for q in get_quotes_by_symbols(db, symbols)}

        enriched_items = []
        for item in items:
            q = quotes_map.get(item.symbol)
            enriched_items.append({
                "id": item.id,
                "user_id": item.user_id,
                "symbol": item.symbol,
                "company_name": item.company_name or (q.company_name if q else item.symbol),
                "category": item.category,
                "notes": item.notes,
                "added_at": item.added_at.isoformat(),
                "quote": self._serialize_quote(q) if q else None,
            })

        # Summary calculations
        valid_quotes = [q for q in (quotes_map.get(i.symbol) for i in items) if q]
        avg_ret = round(sum(q.percent_change for q in valid_quotes) / len(valid_quotes), 2) if valid_quotes else 0.0

        return {
            "user_id": user_id,
            "total_items": len(enriched_items),
            "average_return": avg_ret,
            "items": enriched_items,
            "timestamp": utc_now().isoformat(),
        }

    def add_to_watchlist(
        self,
        db: Session,
        symbol: str,
        user_id: str = "default",
        category: str = "custom",
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add a stock to user watchlist, fetching quote if not yet present."""
        symbol = symbol.strip().upper()
        quote = get_quote_by_symbol(db, symbol)

        if quote is None:
            # Try fetching quote from provider
            try:
                fetched = self.provider.fetch_stock_quotes([symbol])
                if fetched:
                    item_data = fetched[0]
                    item_data["company_name"] = symbol
                    item_data["sector"] = "Other"
                    item_data["market_cap_category"] = "mid"
                    quote = upsert_quote(db, item_data)
            except Exception as exc:
                logger.warning("Could not fetch new stock quote for %s: %s", symbol, exc)

        company_name = quote.company_name if quote else symbol
        record = repo_add_watchlist_item(
            db=db,
            user_id=user_id,
            symbol=symbol,
            company_name=company_name,
            category=category,
            notes=notes,
        )

        return {
            "message": f"'{symbol}' added to watchlist successfully.",
            "item": {
                "id": record.id,
                "user_id": record.user_id,
                "symbol": record.symbol,
                "company_name": record.company_name,
                "category": record.category,
                "notes": record.notes,
                "added_at": record.added_at.isoformat(),
                "quote": self._serialize_quote(quote) if quote else None,
            },
        }

    def remove_from_watchlist(
        self,
        db: Session,
        symbol: str,
        user_id: str = "default",
    ) -> dict[str, Any]:
        """Remove a stock from user watchlist."""
        symbol = symbol.strip().upper()
        removed = repo_remove_watchlist_item(db, user_id=user_id, symbol=symbol)
        return {
            "symbol": symbol,
            "user_id": user_id,
            "removed": removed,
            "message": f"'{symbol}' removed from watchlist." if removed else f"'{symbol}' not found in watchlist.",
        }

    # =========================================================================
    # 7. 52-WEEK HIGH / LOW BREAKOUTS
    # =========================================================================

    def get_52_week_high_low(
        self,
        db: Session,
        threshold_pct: float = 3.5,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Returns stocks trading close to their 52-week highs and 52-week lows."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        highs = get_52_week_highs(db, threshold_pct=threshold_pct, limit=limit)
        lows = get_52_week_lows(db, threshold_pct=threshold_pct, limit=limit)

        return {
            "threshold_percentage": threshold_pct,
            "near_52w_high": [self._serialize_quote(q) for q in highs],
            "near_52w_low": [self._serialize_quote(q) for q in lows],
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 8. VOLUME SHOCKERS & MOST ACTIVE
    # =========================================================================

    def get_volume_shockers(
        self,
        db: Session,
        min_ratio: float = 1.5,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> List[dict[str, Any]]:
        """Returns stocks experiencing abnormal trading volume surges."""
        self.ensure_seeded(db, force_refresh=force_refresh)

        shockers = get_volume_shockers(db, min_ratio=min_ratio, limit=limit)
        return [self._serialize_quote(q) for q in shockers]

    # =========================================================================
    # 9. MARKET SENTIMENT PULSE
    # =========================================================================

    def get_market_sentiment_pulse(
        self,
        db: Session,
    ) -> dict[str, Any]:
        """
        Calculates aggregated sentiment across the market using stored
        news sentiment or heuristic market momentum.
        """
        # Read from Sentiment table if records exist
        from backend.models.sentiment import Sentiment
        try:
            total_sentiments = db.query(Sentiment).count()
            if total_sentiments > 0:
                positive = db.query(Sentiment).filter(Sentiment.label == "positive").count()
                neutral = db.query(Sentiment).filter(Sentiment.label == "neutral").count()
                negative = db.query(Sentiment).filter(Sentiment.label == "negative").count()

                pos_pct = round((positive / total_sentiments) * 100.0, 1)
                neu_pct = round((neutral / total_sentiments) * 100.0, 1)
                neg_pct = round((negative / total_sentiments) * 100.0, 1)
                score = round((positive - negative) / total_sentiments, 2)

                overall_label = "Bullish" if score > 0.15 else ("Bearish" if score < -0.15 else "Neutral")

                return {
                    "overall_sentiment": overall_label,
                    "sentiment_score": score,
                    "positive_percentage": pos_pct,
                    "neutral_percentage": neu_pct,
                    "negative_percentage": neg_pct,
                    "total_articles_analyzed": total_sentiments,
                    "timestamp": utc_now().isoformat(),
                }
        except Exception as exc:
            logger.debug("Sentiment table query exception: %s", exc)

        # Fallback heuristic based on advance/decline breadth
        breadth = self.get_advance_decline(db)
        adr = breadth["advance_decline_ratio"]
        score = round((breadth["advances"] - breadth["declines"]) / max(1, breadth["total_tracked"]), 2)

        return {
            "overall_sentiment": breadth["market_regime"],
            "sentiment_score": score,
            "positive_percentage": breadth["advance_percentage"],
            "neutral_percentage": breadth["unchanged_percentage"],
            "negative_percentage": breadth["decline_percentage"],
            "total_articles_analyzed": 50,
            "timestamp": utc_now().isoformat(),
        }

    # =========================================================================
    # 10. IPO – UPCOMING, RECENT & PERFORMANCE
    # =========================================================================

    IPO_CACHE_TTL = timedelta(hours=6)
    _ipo_last_refreshed: Optional[datetime] = None

    def _ensure_ipos_seeded(self, db: Session, force_refresh: bool = False) -> None:
        """Seed the ipo_details table from curated fallback data if it is empty."""
        from backend.repositories.market_repository import get_ipo_by_symbol as _ipo_exists
        if force_refresh or not repo_list_upcoming_ipos(db, limit=1) and not repo_list_recent_ipos(db, days=90):
            has_upcoming = bool(repo_list_upcoming_ipos(db, limit=1))
            has_recent = bool(repo_list_recent_ipos(db, days=90))
            if force_refresh or (not has_upcoming and not has_recent):
                for ipo_data in DEFAULT_IPOS:
                    try:
                        upsert_ipo_detail(db, ipo_data)
                    except Exception as exc:
                        logger.debug("Failed seeding IPO %s: %s", ipo_data.get("symbol"), exc)

    def _serialize_ipo_detail(self, ipo) -> dict[str, Any]:
        """Convert an IpoDetail ORM object into a clean dictionary."""
        return {
            "id": ipo.id,
            "company_name": ipo.company_name,
            "symbol": ipo.symbol,
            "exchange": ipo.exchange,
            "issue_date": ipo.issue_date.strftime("%Y-%m-%d") if ipo.issue_date else None,
            "price_range_low": round(ipo.price_range_low, 2) if ipo.price_range_low else None,
            "price_range_high": round(ipo.price_range_high, 2) if ipo.price_range_high else None,
            "total_shares": ipo.total_shares,
            "listing_price": round(ipo.listing_price, 2) if ipo.listing_price else None,
            "underwriters": ipo.underwriters,
            "status": ipo.status,
            "created_at": ipo.created_at.isoformat() if ipo.created_at else None,
            "updated_at": ipo.updated_at.isoformat() if ipo.updated_at else None,
        }

    def _serialize_ipo_performance(self, perf) -> dict[str, Any]:
        """Convert an IpoPerformance ORM object into a clean dictionary."""
        return {
            "id": perf.id,
            "ipo_id": perf.ipo_id,
            "trade_date": perf.trade_date.strftime("%Y-%m-%d") if perf.trade_date else None,
            "open_price": round(perf.open_price, 2) if perf.open_price else None,
            "close_price": round(perf.close_price, 2) if perf.close_price else None,
            "high_price": round(perf.high_price, 2) if perf.high_price else None,
            "low_price": round(perf.low_price, 2) if perf.low_price else None,
            "volume": perf.volume,
            "pct_change": round(perf.pct_change, 2) if perf.pct_change else None,
        }

    def get_upcoming_ipos(
        self,
        db: Session,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Returns upcoming IPOs (status='upcoming').
        Multi-Tier Strategy:
        1. Ensure DB is seeded with curated fallback data.
        2. Try fetching from live provider and upserting.
        3. Return from database.
        1. Ensure DB has baseline data.
        2. Attempt live official NSE/BSE fetch if force_refresh or cache is stale.
        3. If official fetch fails / unavailable, keep existing data as-is.
        4. Return from database.
        """
        self._ensure_ipos_seeded(db, force_refresh=force_refresh)

        # Attempt live provider refresh
        # if force_refresh:
        should_fetch = (
            force_refresh
            or (self._ipo_last_refreshed is None)
            or ((utc_now() - self._ipo_last_refreshed) > self.IPO_CACHE_TTL)
        )
        if should_fetch:
            try:
                live_ipos = self.provider.fetch_ipo_details()
                for item in live_ipos:
                    if item.get("status") == "upcoming":
                        if live_ipos:
                            for item in live_ipos:
                                upsert_ipo_detail(db, item)
                            self._ipo_last_refreshed = utc_now()
            except Exception as exc:
                logger.warning("Could not refresh live IPO details: %s", exc)
                logger.warning("Could not refresh live IPO details from NSE/BSE: %s", exc)

        records = repo_list_upcoming_ipos(db, limit=50)
        return [self._serialize_ipo_detail(r) for r in records]

    def get_recent_ipos(
        self,
        db: Session,
        days: int = 30,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Returns recently listed IPOs (status='listed', within last *days* days).
        Strictly queries official exchange or existing database data.
        """
        self._ensure_ipos_seeded(db, force_refresh=force_refresh)

        # if force_refresh:
        should_fetch = (
            force_refresh
            or (self._ipo_last_refreshed is None)
            or ((utc_now() - self._ipo_last_refreshed) > self.IPO_CACHE_TTL)
        )
            # )
        if should_fetch:
            try:
                live_ipos = self.provider.fetch_ipo_details()
                for item in live_ipos:
                    if item.get("status") == "listed":
                        if live_ipos:
                            for item in live_ipos:
                                upsert_ipo_detail(db, item)
                            self._ipo_last_refreshed = utc_now()
            except Exception as exc:
                logger.warning("Could not refresh live IPO details: %s", exc)
                logger.warning("Could not refresh live IPO details from NSE/BSE: %s", exc)

        records = repo_list_recent_ipos(db, days=days)
        return [self._serialize_ipo_detail(r) for r in records]

    def get_ipo_performance(
        self,
        db: Session,
        symbol: str,
        limit: int = 30,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Returns daily post-listing performance for a specific IPO symbol.
        Fetches from yfinance if DB has no records or force_refresh is set.
        """
        self._ensure_ipos_seeded(db, force_refresh=False)

        ipo_record = get_ipo_by_symbol(db, symbol)
        if not ipo_record:
            return []

        # Try fetching live performance data if DB is empty or refresh requested
        existing = repo_get_ipo_performance(db, symbol, limit=1)
        if not existing or force_refresh:
            try:
                live_perf = self.provider.fetch_ipo_daily_performance(symbol)
                for day_data in live_perf:
                    upsert_ipo_performance(db, ipo_id=ipo_record.id, data=day_data)
            except Exception as exc:
                logger.warning("Could not fetch live IPO performance for %s: %s", symbol, exc)

        records = repo_get_ipo_performance(db, symbol, limit=limit)
        return [self._serialize_ipo_performance(r) for r in records]

    # =========================================================================
    # 11. CONSOLIDATED MASTER HOME PAGE DASHBOARD
    # =========================================================================

    def get_home_dashboard(
        self,
        db: Session,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Returns a complete, consolidated dashboard payload for the Home Page
        in a single call. Eliminates waterfall network requests in frontend.
        """
        overview = self.get_market_overview(db, force_refresh=force_refresh)
        breadth = self.get_advance_decline(db, force_refresh=force_refresh)
        movers = self.get_market_movers(db, cap="all", limit=6, force_refresh=force_refresh)
        sectors = self.get_sector_performance(db, force_refresh=force_refresh)
        quarterly = self.get_quarterly_results(db, status="all", limit=6, force_refresh=force_refresh)
        watchlist = self.get_watchlist(db, user_id="default", force_refresh=force_refresh)
        breakouts = self.get_52_week_high_low(db, threshold_pct=3.5, limit=5, force_refresh=force_refresh)
        shockers = self.get_volume_shockers(db, min_ratio=1.5, limit=5, force_refresh=force_refresh)
        sentiment_pulse = self.get_market_sentiment_pulse(db)

        return {
            "status": "success",
            "market_overview": overview,
            "advance_decline": breadth,
            "market_movers": movers,
            "sector_performance": sectors[:8],
            "quarterly_results": quarterly,
            "watchlist": watchlist,
            "breakouts_52w": breakouts,
            "volume_shockers": shockers,
            "market_sentiment": sentiment_pulse,
            "data_source": "hybrid_db_provider",
            "timestamp": utc_now().isoformat(),
        }


home_service = HomeService()
