"""
Market Repository layer for AlphaLens Home Page and Market Overview.
Follows Single Responsibility Principle (SRP) for all database operations
relating to market indices, stock quotes, quarterly results, watchlists,
and breadth snapshots.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from sqlalchemy import desc, asc, func
from sqlalchemy.orm import Session

from backend.models.market_data import (
    MarketBreadthSnapshot,
    MarketIndex,
    QuarterlyResultRecord,
    StockQuote,
    IpoDetail,
    IpoPerformance,
    MarketNews,
    MacroIndicator,
    CurrencyRate,
    WatchlistItemRecord
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =====================================================================
# INDICES REPOSITORY
# =====================================================================

def get_indices(
    db: Session,
    category: Optional[str] = None,
) -> List[MarketIndex]:
    """Retrieve all market indices, optionally filtered by category."""
    query = db.query(MarketIndex)
    if category:
        query = query.filter(MarketIndex.category == category)
    return query.order_by(MarketIndex.id.asc()).all()


def get_index_by_symbol(
    db: Session,
    symbol: str,
) -> Optional[MarketIndex]:
    """Retrieve an index record by its ticker symbol."""
    return (
        db.query(MarketIndex)
        .filter(MarketIndex.symbol == symbol.upper().strip())
        .first()
    )


def upsert_index(
    db: Session,
    index_data: dict[str, Any],
) -> MarketIndex:
    """Create or update a market index entry."""
    symbol = index_data["symbol"].upper().strip()
    record = get_index_by_symbol(db, symbol)

    if record is None:
        record = MarketIndex(
            symbol=symbol,
            name=index_data.get("name", symbol),
            category=index_data.get("category", "benchmark"),
            current_value=float(index_data.get("current_value", 0.0)),
            change=float(index_data.get("change", 0.0)),
            percent_change=float(index_data.get("percent_change", 0.0)),
            open_value=index_data.get("open_value"),
            high_value=index_data.get("high_value"),
            low_value=index_data.get("low_value"),
            previous_close=index_data.get("previous_close"),
            last_updated=utc_now(),
        )
        db.add(record)
    else:
        record.name = index_data.get("name", record.name)
        record.category = index_data.get("category", record.category)
        record.current_value = float(index_data.get("current_value", record.current_value))
        record.change = float(index_data.get("change", record.change))
        record.percent_change = float(index_data.get("percent_change", record.percent_change))
        record.open_value = index_data.get("open_value", record.open_value)
        record.high_value = index_data.get("high_value", record.high_value)
        record.low_value = index_data.get("low_value", record.low_value)
        record.previous_close = index_data.get("previous_close", record.previous_close)
        record.last_updated = utc_now()

    db.commit()
    db.refresh(record)
    return record


# =====================================================================
# STOCK QUOTES REPOSITORY
# =====================================================================

def count_quotes(db: Session) -> int:
    """Return the total number of stock quote records in the DB."""
    return db.query(func.count(StockQuote.id)).scalar() or 0


def get_quotes(
    db: Session,
    cap_category: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = 200,
) -> List[StockQuote]:
    """Return stock quotes filtered by market cap or sector."""
    query = db.query(StockQuote).filter(StockQuote.is_active == True)
    if cap_category:
        query = query.filter(StockQuote.market_cap_category == cap_category.lower().strip())
    if sector:
        query = query.filter(StockQuote.sector == sector.strip())
    return query.limit(limit).all()


def get_quote_by_symbol(
    db: Session,
    symbol: str,
) -> Optional[StockQuote]:
    """Find a single stock quote by symbol."""
    return (
        db.query(StockQuote)
        .filter(StockQuote.symbol == symbol.upper().strip())
        .first()
    )


def get_quotes_by_symbols(
    db: Session,
    symbols: List[str],
) -> List[StockQuote]:
    """Find stock quotes for a list of symbols."""
    if not symbols:
        return []
    normalized = [s.upper().strip() for s in symbols]
    return (
        db.query(StockQuote)
        .filter(StockQuote.symbol.in_(normalized))
        .all()
    )


def upsert_quote(
    db: Session,
    data: dict[str, Any],
) -> StockQuote:
    """Create or update a stock quote."""
    symbol = data["symbol"].upper().strip()
    record = get_quote_by_symbol(db, symbol)

    if record is None:
        record = StockQuote(
            symbol=symbol,
            company_name=data.get("company_name", symbol),
            sector=data.get("sector", "Diversified"),
            market_cap_category=data.get("market_cap_category", "large").lower(),
            current_price=float(data.get("current_price", 0.0)),
            change=float(data.get("change", 0.0)),
            percent_change=float(data.get("percent_change", 0.0)),
            open_price=data.get("open_price"),
            high_price=data.get("high_price"),
            low_price=data.get("low_price"),
            previous_close=data.get("previous_close"),
            volume=int(data.get("volume", 0)),
            avg_volume_10d=int(data.get("avg_volume_10d", 0)),
            volume_surge_ratio=float(data.get("volume_surge_ratio", 1.0)),
            high_52w=data.get("high_52w"),
            low_52w=data.get("low_52w"),
            pe_ratio=data.get("pe_ratio"),
            market_cap=data.get("market_cap"),
            is_active=data.get("is_active", True),
            last_updated=utc_now(),
        )
        db.add(record)
    else:
        record.company_name = data.get("company_name", record.company_name)
        record.sector = data.get("sector", record.sector)
        record.market_cap_category = data.get("market_cap_category", record.market_cap_category).lower()
        record.current_price = float(data.get("current_price", record.current_price))
        record.change = float(data.get("change", record.change))
        record.percent_change = float(data.get("percent_change", record.percent_change))
        record.open_price = data.get("open_price", record.open_price)
        record.high_price = data.get("high_price", record.high_price)
        record.low_price = data.get("low_price", record.low_price)
        record.previous_close = data.get("previous_close", record.previous_close)
        record.volume = int(data.get("volume", record.volume or 0))
        record.avg_volume_10d = int(data.get("avg_volume_10d", record.avg_volume_10d or 0))
        record.volume_surge_ratio = float(data.get("volume_surge_ratio", record.volume_surge_ratio or 1.0))
        record.high_52w = data.get("high_52w", record.high_52w)
        record.low_52w = data.get("low_52w", record.low_52w)
        record.pe_ratio = data.get("pe_ratio", record.pe_ratio)
        record.market_cap = data.get("market_cap", record.market_cap)
        record.is_active = data.get("is_active", record.is_active)
        record.last_updated = utc_now()

    db.commit()
    db.refresh(record)
    return record


def bulk_upsert_quotes(
    db: Session,
    quotes: List[dict[str, Any]],
) -> None:
    """Efficiently upsert multiple stock quotes."""
    for q in quotes:
        upsert_quote(db, q)


def get_top_gainers(
    db: Session,
    cap_category: Optional[str] = None,
    limit: int = 10,
) -> List[StockQuote]:
    """Retrieve top gainers ordered by percentage change descending."""
    query = db.query(StockQuote).filter(StockQuote.is_active == True)
    if cap_category:
        query = query.filter(StockQuote.market_cap_category == cap_category.lower().strip())
    return (
        query.filter(StockQuote.percent_change > 0)
        .order_by(desc(StockQuote.percent_change))
        .limit(limit)
        .all()
    )


def get_top_losers(
    db: Session,
    cap_category: Optional[str] = None,
    limit: int = 10,
) -> List[StockQuote]:
    """Retrieve top losers ordered by percentage change ascending."""
    query = db.query(StockQuote).filter(StockQuote.is_active == True)
    if cap_category:
        query = query.filter(StockQuote.market_cap_category == cap_category.lower().strip())
    return (
        query.filter(StockQuote.percent_change < 0)
        .order_by(asc(StockQuote.percent_change))
        .limit(limit)
        .all()
    )


def get_most_active(
    db: Session,
    limit: int = 10,
) -> List[StockQuote]:
    """Retrieve most active stocks by volume."""
    return (
        db.query(StockQuote)
        .filter(StockQuote.is_active == True)
        .order_by(desc(StockQuote.volume))
        .limit(limit)
        .all()
    )


def get_52_week_highs(
    db: Session,
    threshold_pct: float = 3.5,
    limit: int = 10,
) -> List[StockQuote]:
    """
    Retrieve stocks trading within `threshold_pct` percent of their 52-week high.
    (current_price >= high_52w * (1 - threshold_pct/100))
    """
    quotes = (
        db.query(StockQuote)
        .filter(
            StockQuote.is_active == True,
            StockQuote.high_52w.isnot(None),
            StockQuote.high_52w > 0,
            StockQuote.current_price.isnot(None),
        )
        .all()
    )
    result = []
    for q in quotes:
        if q.high_52w and q.current_price:
            proximity = (q.high_52w - q.current_price) / q.high_52w * 100.0
            if proximity <= threshold_pct and proximity >= -0.5:
                result.append(q)
    result.sort(key=lambda x: (x.high_52w - x.current_price) / x.high_52w)
    return result[:limit]


def get_52_week_lows(
    db: Session,
    threshold_pct: float = 3.5,
    limit: int = 10,
) -> List[StockQuote]:
    """
    Retrieve stocks trading within `threshold_pct` percent of their 52-week low.
    """
    quotes = (
        db.query(StockQuote)
        .filter(
            StockQuote.is_active == True,
            StockQuote.low_52w.isnot(None),
            StockQuote.low_52w > 0,
            StockQuote.current_price.isnot(None),
        )
        .all()
    )
    result = []
    for q in quotes:
        if q.low_52w and q.current_price:
            proximity = (q.current_price - q.low_52w) / q.low_52w * 100.0
            if proximity <= threshold_pct and proximity >= -0.5:
                result.append(q)
    result.sort(key=lambda x: (x.current_price - x.low_52w) / x.low_52w)
    return result[:limit]


def get_volume_shockers(
    db: Session,
    min_ratio: float = 1.5,
    limit: int = 10,
) -> List[StockQuote]:
    """Retrieve stocks with unusually high volume surge."""
    return (
        db.query(StockQuote)
        .filter(
            StockQuote.is_active == True,
            StockQuote.volume_surge_ratio >= min_ratio,
        )
        .order_by(desc(StockQuote.volume_surge_ratio))
        .limit(limit)
        .all()
    )


# =====================================================================
# SECTORS REPOSITORY
# =====================================================================

def get_sector_names(db: Session) -> List[str]:
    """Return distinct sector names available in stock quotes."""
    rows = (
        db.query(StockQuote.sector)
        .filter(StockQuote.is_active == True)
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0]]


def get_quotes_by_sector(
    db: Session,
    sector: str,
) -> List[StockQuote]:
    """Return all stock quotes within a specific sector."""
    return (
        db.query(StockQuote)
        .filter(
            StockQuote.is_active == True,
            func.lower(StockQuote.sector) == sector.lower().strip(),
        )
        .order_by(desc(StockQuote.percent_change))
        .all()
    )


# =====================================================================
# QUARTERLY RESULTS REPOSITORY
# =====================================================================

def count_quarterly_results(db: Session) -> int:
    """Return count of quarterly result records."""
    return db.query(func.count(QuarterlyResultRecord.id)).scalar() or 0


def get_quarterly_results(
    db: Session,
    is_upcoming: Optional[bool] = None,
    symbol: Optional[str] = None,
    limit: int = 20,
) -> List[QuarterlyResultRecord]:
    """Retrieve quarterly results, filterable by upcoming status or symbol."""
    query = db.query(QuarterlyResultRecord)
    if is_upcoming is not None:
        query = query.filter(QuarterlyResultRecord.is_upcoming == is_upcoming)
    if symbol:
        query = query.filter(QuarterlyResultRecord.symbol == symbol.upper().strip())

    if is_upcoming is True:
        # Upcoming ordered ascending by date (next result earliest)
        query = query.order_by(asc(QuarterlyResultRecord.result_date))
    else:
        # Declared results ordered descending by date (most recent first)
        query = query.order_by(desc(QuarterlyResultRecord.result_date))

    return query.limit(limit).all()


def upsert_quarterly_result(
    db: Session,
    data: dict[str, Any],
) -> QuarterlyResultRecord:
    """Insert or update a quarterly result record."""
    symbol = data["symbol"].upper().strip()
    fiscal_year = data.get("fiscal_year", "FY25")
    quarter = data.get("quarter", "Q1")

    record = (
        db.query(QuarterlyResultRecord)
        .filter(
            QuarterlyResultRecord.symbol == symbol,
            QuarterlyResultRecord.fiscal_year == fiscal_year,
            QuarterlyResultRecord.quarter == quarter,
        )
        .first()
    )

    result_date = data["result_date"]
    if isinstance(result_date, str):
        try:
            result_date = datetime.fromisoformat(result_date)
        except Exception:
            result_date = utc_now()

    if record is None:
        record = QuarterlyResultRecord(
            symbol=symbol,
            company_name=data.get("company_name", symbol),
            sector=data.get("sector"),
            fiscal_year=fiscal_year,
            quarter=quarter,
            result_date=result_date,
            is_upcoming=data.get("is_upcoming", False),
            revenue=data.get("revenue"),
            revenue_growth_yoy=data.get("revenue_growth_yoy"),
            net_profit=data.get("net_profit"),
            profit_growth_yoy=data.get("profit_growth_yoy"),
            verdict=data.get("verdict"),
            impact_percent=data.get("impact_percent"),
            key_highlights=data.get("key_highlights"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(record)
    else:
        record.company_name = data.get("company_name", record.company_name)
        record.sector = data.get("sector", record.sector)
        record.result_date = result_date
        record.is_upcoming = data.get("is_upcoming", record.is_upcoming)
        record.revenue = data.get("revenue", record.revenue)
        record.revenue_growth_yoy = data.get("revenue_growth_yoy", record.revenue_growth_yoy)
        record.net_profit = data.get("net_profit", record.net_profit)
        record.profit_growth_yoy = data.get("profit_growth_yoy", record.profit_growth_yoy)
        record.verdict = data.get("verdict", record.verdict)
        record.impact_percent = data.get("impact_percent", record.impact_percent)
        record.key_highlights = data.get("key_highlights", record.key_highlights)
        record.updated_at = utc_now()

    db.commit()
    db.refresh(record)
    return record


def bulk_upsert_quarterly_results(
    db: Session,
    results: List[dict[str, Any]],
) -> None:
    """Bulk upsert quarterly results."""
    for item in results:
        upsert_quarterly_result(db, item)


# =====================================================================
# WATCHLIST REPOSITORY
# =====================================================================

def get_watchlist_items(
    db: Session,
    user_id: str = "default",
) -> List[WatchlistItemRecord]:
    """Retrieve all watchlist items for a given user."""
    return (
        db.query(WatchlistItemRecord)
        .filter(WatchlistItemRecord.user_id == user_id)
        .order_by(WatchlistItemRecord.added_at.desc())
        .all()
    )


def add_watchlist_item(
    db: Session,
    user_id: str,
    symbol: str,
    company_name: Optional[str] = None,
    category: str = "custom",
    notes: Optional[str] = None,
) -> WatchlistItemRecord:
    """Add a symbol to the user's watchlist if not already present."""
    symbol = symbol.upper().strip()
    record = (
        db.query(WatchlistItemRecord)
        .filter(
            WatchlistItemRecord.user_id == user_id,
            WatchlistItemRecord.symbol == symbol,
        )
        .first()
    )
    if record is None:
        record = WatchlistItemRecord(
            user_id=user_id,
            symbol=symbol,
            company_name=company_name or symbol,
            category=category,
            notes=notes,
            added_at=utc_now(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


def remove_watchlist_item(
    db: Session,
    user_id: str,
    symbol: str,
) -> bool:
    """Remove a symbol from the user's watchlist."""
    symbol = symbol.upper().strip()
    record = (
        db.query(WatchlistItemRecord)
        .filter(
            WatchlistItemRecord.user_id == user_id,
            WatchlistItemRecord.symbol == symbol,
        )
        .first()
    )
    if record:
        db.delete(record)
        db.commit()
        return True
    return False


# =====================================================================
# MARKET BREADTH SNAPSHOT REPOSITORY
# =====================================================================

def save_breadth_snapshot(
    db: Session,
    snapshot_data: dict[str, Any],
) -> MarketBreadthSnapshot:
    """Record an advance/decline market breadth snapshot."""
    snapshot = MarketBreadthSnapshot(
        snapshot_time=utc_now(),
        advances=int(snapshot_data.get("advances", 0)),
        declines=int(snapshot_data.get("declines", 0)),
        unchanged=int(snapshot_data.get("unchanged", 0)),
        total_tracked=int(snapshot_data.get("total_tracked", 0)),
        advance_decline_ratio=float(snapshot_data.get("advance_decline_ratio", 1.0)),
        market_status=snapshot_data.get("market_status", "CLOSED"),
        market_regime=snapshot_data.get("market_regime", "Neutral"),
        mood_score=float(snapshot_data.get("mood_score", 0.0)),
        raw_metadata=snapshot_data.get("raw_metadata"),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_breadth_snapshot(
    db: Session,
) -> Optional[MarketBreadthSnapshot]:
    """Retrieve the most recent breadth snapshot."""
    return (
        db.query(MarketBreadthSnapshot)
        .order_by(desc(MarketBreadthSnapshot.snapshot_time))
        .first()
    )


def count_indices(db: Session) -> int:
    """Return the total number of market index records in the DB."""
    return db.query(func.count(MarketIndex.id)).scalar() or 0


# =====================================================================
# IPO AND RELATED REPOSITORIES
# =====================================================================

def get_ipo_by_symbol(
    db: Session,
    symbol: str,
) -> Optional[IpoDetail]:
    """Retrieve IPO detail record by its ticker symbol."""
    return (
        db.query(IpoDetail)
        .filter(IpoDetail.symbol == symbol.upper().strip())
        .first()
    )

def list_upcoming_ipos(
    db: Session,
    exchange: Optional[str] = None,
    limit: int = 20,
) -> List[IpoDetail]:
    """List upcoming IPOs, optionally filtered by exchange (mainboard or sme)."""
    query = db.query(IpoDetail).filter(IpoDetail.status == "upcoming")
    if exchange:
        query = query.filter(IpoDetail.exchange == exchange.lower().strip())
    return query.order_by(IpoDetail.issue_date.asc()).limit(limit).all()

def list_recent_ipos(
    db: Session,
    days: int = 30,
) -> List[IpoDetail]:
    """List IPOs that have been listed in the last *days* days."""
    cutoff = utc_now() - timedelta(days=days)
    return (
        db.query(IpoDetail)
        .filter(IpoDetail.status == "listed", IpoDetail.issue_date >= cutoff)
        .order_by(IpoDetail.issue_date.desc())
        .all()
    )

def upsert_ipo_detail(
    db: Session,
    data: dict[str, Any],
) -> IpoDetail:
    """Insert or update an IPO detail record."""
    symbol = data["symbol"].upper().strip()
    record = get_ipo_by_symbol(db, symbol)
    if record is None:
        record = IpoDetail(
            company_name=data.get("company_name", symbol),
            symbol=symbol,
            exchange=data.get("exchange", "mainboard"),
            issue_date=data.get("issue_date"),
            price_range_low=data.get("price_range_low"),
            price_range_high=data.get("price_range_high"),
            total_shares=data.get("total_shares"),
            listing_price=data.get("listing_price"),
            underwriters=data.get("underwriters"),
            status=data.get("status", "upcoming"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db.add(record)
    else:
        # Update mutable fields
        record.company_name = data.get("company_name", record.company_name)
        record.exchange = data.get("exchange", record.exchange)
        record.issue_date = data.get("issue_date", record.issue_date)
        record.price_range_low = data.get("price_range_low", record.price_range_low)
        record.price_range_high = data.get("price_range_high", record.price_range_high)
        record.total_shares = data.get("total_shares", record.total_shares)
        record.listing_price = data.get("listing_price", record.listing_price)
        record.underwriters = data.get("underwriters", record.underwriters)
        record.status = data.get("status", record.status)
        record.updated_at = utc_now()
    db.commit()
    db.refresh(record)
    return record

def get_ipo_performance(
    db: Session,
    symbol: str,
    limit: int = 30,
) -> List[IpoPerformance]:
    """Retrieve daily performance records for a listed IPO, most recent *limit* rows."""
    return (
        db.query(IpoPerformance)
        .filter(IpoPerformance.ipo_id == db.query(IpoDetail.id).filter(IpoDetail.symbol == symbol.upper().strip()).scalar_subquery())
        .order_by(IpoPerformance.trade_date.desc())
        .limit(limit)
        .all()
    )

def upsert_ipo_performance(
    db: Session,
    ipo_id: int,
    data: dict[str, Any],
) -> IpoPerformance:
    """Insert a daily IPO performance record (no duplicate check for simplicity)."""
    record = IpoPerformance(
        ipo_id=ipo_id,
        trade_date=data.get("trade_date", utc_now()),
        open_price=data.get("open_price"),
        close_price=data.get("close_price"),
        high_price=data.get("high_price"),
        low_price=data.get("low_price"),
        volume=data.get("volume"),
        pct_change=data.get("pct_change"),
        created_at=utc_now(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# =====================================================================
# MARKET NEWS REPOSITORY
# =====================================================================

def bulk_upsert_market_news(
    db: Session,
    items: List[dict[str, Any]],
) -> None:
    """Efficiently upsert a list of market news items (by unique URL)."""
    for item in items:
        existing = (
            db.query(MarketNews).filter(MarketNews.url == item.get("url")).first()
        )
        if existing:
            existing.title = item.get("title", existing.title)
            existing.source = item.get("source", existing.source)
            existing.published_at = item.get("published_at", existing.published_at)
            existing.summary = item.get("summary", existing.summary)
        else:
            db.add(
                MarketNews(
                    title=item.get("title"),
                    url=item.get("url"),
                    source=item.get("source"),
                    published_at=item.get("published_at"),
                    summary=item.get("summary"),
                    created_at=utc_now(),
                )
            )
    db.commit()

def list_latest_news(
    db: Session,
    limit: int = 20,
) -> List[MarketNews]:
    """Return the most recent market news items ordered by published timestamp descending."""
    return (
        db.query(MarketNews)
        .order_by(MarketNews.published_at.desc())
        .limit(limit)
        .all()
    )

# =====================================================================
# MACRO INDICATORS REPOSITORY
# =====================================================================

def bulk_upsert_macro_indicators(
    db: Session,
    items: List[dict[str, Any]],
) -> None:
    """Upsert macro indicator records (identified by name and recorded_at)."""
    for item in items:
        existing = (
            db.query(MacroIndicator)
            .filter(
                MacroIndicator.name == item.get("name"),
                MacroIndicator.recorded_at == item.get("recorded_at"),
            )
            .first()
        )
        if existing:
            existing.value = item.get("value", existing.value)
            existing.unit = item.get("unit", existing.unit)
        else:
            db.add(
                MacroIndicator(
                    name=item.get("name"),
                    value=item.get("value"),
                    unit=item.get("unit"),
                    recorded_at=item.get("recorded_at", utc_now()),
                    created_at=utc_now(),
                )
            )
    db.commit()

def list_macro_indicators(
    db: Session,
) -> List[MacroIndicator]:
    """Return the latest value for each macro indicator (most recent recorded_at per name)."""
    subq = (
        db.query(
            MacroIndicator.name,
            func.max(MacroIndicator.recorded_at).label("max_date"),
        )
        .group_by(MacroIndicator.name)
        .subquery()
    )
    return (
        db.query(MacroIndicator)
        .join(
            subq,
            (MacroIndicator.name == subq.c.name)
            & (MacroIndicator.recorded_at == subq.c.max_date),
        )
        .all()
    )

# =====================================================================
# CURRENCY RATES REPOSITORY
# =====================================================================

def upsert_currency_rate(
    db: Session,
    data: dict[str, Any],
) -> CurrencyRate:
    """Insert or update a currency pair rate (identified by unique pair string)."""
    pair = data["pair"].upper().strip()
    record = db.query(CurrencyRate).filter(CurrencyRate.pair == pair).first()
    if record is None:
        record = CurrencyRate(
            pair=pair,
            bid=data.get("bid"),
            ask=data.get("ask"),
            timestamp=data.get("timestamp", utc_now()),
            created_at=utc_now(),
        )
        db.add(record)
    else:
        record.bid = data.get("bid", record.bid)
        record.ask = data.get("ask", record.ask)
        record.timestamp = data.get("timestamp", record.timestamp)
    db.commit()
    db.refresh(record)
    return record

def list_currency_rates(
    db: Session,
) -> List[CurrencyRate]:
    """Return all stored currency rates ordered by pair."""
    return db.query(CurrencyRate).order_by(CurrencyRate.pair.asc()).all()

# End of optional repository block
