"""
SQLAlchemy models for Home Page and Market Intelligence.
Defines schemas for indices, stock quotes, quarterly results, watchlists,
and market breadth snapshots.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from backend.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketIndex(Base):
    """Stores major market indices like NIFTY 50, SENSEX, NIFTY BANK, etc."""
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, default="benchmark")  # benchmark, sectoral, global
    current_value = Column(Float, nullable=False)
    change = Column(Float, nullable=False, default=0.0)
    percent_change = Column(Float, nullable=False, default=0.0)
    open_value = Column(Float, nullable=True)
    high_value = Column(Float, nullable=True)
    low_value = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class StockQuote(Base):
    """
    Stores market quotes for stocks across market caps:
    large (high cap), mid cap, and small cap.
    """
    __tablename__ = "stock_quotes"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False, index=True)
    market_cap_category = Column(String(50), nullable=False, index=True)  # large, mid, small
    current_price = Column(Float, nullable=False)
    change = Column(Float, nullable=False, default=0.0)
    percent_change = Column(Float, nullable=False, default=0.0, index=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True, default=0)
    avg_volume_10d = Column(Integer, nullable=True, default=0)
    volume_surge_ratio = Column(Float, nullable=True, default=1.0)
    high_52w = Column(Float, nullable=True)
    low_52w = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class QuarterlyResultRecord(Base):
    """Stores upcoming and recently declared quarterly results for companies."""
    __tablename__ = "quarterly_results"
    __table_args__ = (
        UniqueConstraint("symbol", "fiscal_year", "quarter", name="uq_quarterly_symbol_period"),
    )

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    fiscal_year = Column(String(20), nullable=False)  # e.g., FY25, FY26
    quarter = Column(String(10), nullable=False)      # e.g., Q1, Q2, Q3, Q4
    result_date = Column(DateTime(timezone=True), nullable=False)
    is_upcoming = Column(Boolean, nullable=False, default=False)
    revenue = Column(Float, nullable=True)             # in Cr
    revenue_growth_yoy = Column(Float, nullable=True) # in %
    net_profit = Column(Float, nullable=True)          # in Cr
    profit_growth_yoy = Column(Float, nullable=True)  # in %
    verdict = Column(String(50), nullable=True)        # Beat, Met, Miss, Pending
    impact_percent = Column(Float, nullable=True)     # Post-result price impact %
    key_highlights = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class WatchlistItemRecord(Base):
    """Stores watchlist entries for home page and custom user watchlists."""
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", name="uq_watchlist_user_symbol"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, default="default", index=True)
    symbol = Column(String(50), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default="bluechip")
    notes = Column(String(500), nullable=True)
    added_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)




class IpoDetail(Base):
    """Metadata about an IPO (Indian market Mainboard or SME)."""
    __tablename__ = "ipo_details"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False, unique=True, index=True)
    exchange = Column(String(20), nullable=False)  # "mainboard" or "sme"
    issue_date = Column(DateTime(timezone=True), nullable=False)
    price_range_low = Column(Float, nullable=True)
    price_range_high = Column(Float, nullable=True)
    total_shares = Column(Integer, nullable=True)
    listing_price = Column(Float, nullable=True)
    underwriters = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="upcoming")  # upcoming, listed, cancelled
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)



class MarketNews(Base):
    """News items relevant to the market (e.g., headline, source, URL)."""
    __tablename__ = "market_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    source = Column(String(100), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class MacroIndicator(Base):
    """Economic macro indicators (e.g., RBI repo rate, inflation)."""
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class CurrencyRate(Base):
    """FX rates for common currency pairs (e.g., USD/INR)."""
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String(20), nullable=False, unique=True, index=True)  # e.g., "USD/INR"
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

class IpoPerformance(Base):
    """Daily performance metrics for an IPO after it has been listed."""
    __tablename__ = "ipo_performance"

    id = Column(Integer, primary_key=True, index=True)
    ipo_id = Column(Integer, nullable=False, index=True)  # FK to IpoDetail.id (not enforced)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    pct_change = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class MarketBreadthSnapshot(Base):
    """Stores a snapshot of market breadth metrics for a given timestamp."""
    __tablename__ = "market_breadth_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_time = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    advances = Column(Integer, nullable=False)
    declines = Column(Integer, nullable=False)
    unchanged = Column(Integer, nullable=False)
    total_tracked = Column(Integer, nullable=False)
    advance_decline_ratio = Column(Float, nullable=False)
    market_status = Column(String(50), nullable=False, default="CLOSED")
    market_regime = Column(String(50), nullable=False, default="Neutral")
    mood_score = Column(Float, nullable=False, default=0.0)
    raw_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
