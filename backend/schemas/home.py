"""
Pydantic schemas for the Home Page and Market Overview endpoints.
Uses Pydantic v2 ConfigDict(from_attributes=True) for modern validation and serialization.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# INDICES & OVERVIEW SCHEMAS
# =====================================================================

class IndexQuoteResponse(BaseSchema):
    symbol: str
    name: str
    category: str
    current_value: float
    change: float
    percent_change: float
    open_value: Optional[float] = None
    high_value: Optional[float] = None
    low_value: Optional[float] = None
    previous_close: Optional[float] = None
    last_updated: str


class MarketStatusResponse(BaseSchema):
    status: str = Field(description="Trading status: OPEN, CLOSED, or PRE_MARKET")
    is_open: bool
    message: str
    exchange: str
    timezone: str
    server_time_utc: str


class MarketOverviewResponse(BaseSchema):
    market_status: MarketStatusResponse
    market_regime: str = Field(description="Regime: Strongly Bullish, Bullish, Neutral, Bearish, Strongly Bearish")
    mood_score: float = Field(description="Normalized sentiment score from -1.0 to 1.0")
    indices: List[IndexQuoteResponse]
    timestamp: str


# =====================================================================
# ADVANCE / DECLINE (MARKET BREADTH)
# =====================================================================

class AdvanceDeclineResponse(BaseSchema):
    advances: int
    declines: int
    unchanged: int
    total_tracked: int
    advance_decline_ratio: float
    advance_percentage: float
    decline_percentage: float
    unchanged_percentage: float
    breadth_sentiment: str
    market_regime: str
    mood_score: float
    timestamp: str


# =====================================================================
# STOCK QUOTES & MARKET MOVERS
# =====================================================================

class StockQuoteResponse(BaseSchema):
    symbol: str
    company_name: str
    sector: str
    market_cap_category: str
    current_price: float
    change: float
    percent_change: float
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[int] = 0
    avg_volume_10d: Optional[int] = 0
    volume_surge_ratio: Optional[float] = 1.0
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    last_updated: str


class CapMoversBlock(BaseSchema):
    gainers: List[StockQuoteResponse]
    losers: List[StockQuoteResponse]


class MarketMoversResponse(BaseSchema):
    cap_filter: str
    large_cap: Optional[CapMoversBlock] = None
    mid_cap: Optional[CapMoversBlock] = None
    small_cap: Optional[CapMoversBlock] = None
    overall_gainers: Optional[List[StockQuoteResponse]] = None
    overall_losers: Optional[List[StockQuoteResponse]] = None
    most_active: Optional[List[StockQuoteResponse]] = None
    gainers: Optional[List[StockQuoteResponse]] = None
    losers: Optional[List[StockQuoteResponse]] = None
    timestamp: str


# =====================================================================
# SECTOR PERFORMANCE SCHEMAS
# =====================================================================

class SectorMoverItem(BaseSchema):
    symbol: str
    company_name: str
    percent_change: float


class SectorPerformanceItem(BaseSchema):
    sector: str
    stock_count: int
    average_change_percent: float
    advances: int
    declines: int
    momentum: str = Field(description="Leading, Improving, Weakening, or Lagging")
    top_gainer: Optional[SectorMoverItem] = None
    top_loser: Optional[SectorMoverItem] = None


class SectorMoversResponse(BaseSchema):
    sector: str
    stock_count: int
    average_change_percent: float
    gainers: List[StockQuoteResponse]
    losers: List[StockQuoteResponse]
    constituents: List[StockQuoteResponse]
    timestamp: str


# =====================================================================
# QUARTERLY RESULTS SCHEMAS
# =====================================================================

class QuarterlyResultResponse(BaseSchema):
    id: int
    symbol: str
    company_name: str
    sector: Optional[str] = None
    fiscal_year: str
    quarter: str
    result_date: Optional[str] = None
    is_upcoming: bool
    revenue: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    net_profit: Optional[float] = None
    profit_growth_yoy: Optional[float] = None
    verdict: Optional[str] = None
    impact_percent: Optional[float] = None
    key_highlights: Optional[str] = None


class QuarterlyResultsListResponse(BaseSchema):
    filter: str
    upcoming: List[QuarterlyResultResponse]
    recent: List[QuarterlyResultResponse]
    timestamp: str


# =====================================================================
# WATCHLIST SCHEMAS
# =====================================================================

class WatchlistItemResponse(BaseSchema):
    id: int
    user_id: str
    symbol: str
    company_name: str
    category: str
    notes: Optional[str] = None
    added_at: str
    quote: Optional[StockQuoteResponse] = None


class WatchlistResponse(BaseSchema):
    user_id: str
    total_items: int
    average_return: float
    items: List[WatchlistItemResponse]
    timestamp: str


class AddWatchlistRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    user_id: str = Field(default="default", max_length=100)
    category: str = Field(default="custom", max_length=50)
    notes: Optional[str] = Field(default=None, max_length=500)


# =====================================================================
# 52-WEEK HIGH / LOW & VOLUME SHOCKERS
# =====================================================================

class HighLow52WeekResponse(BaseSchema):
    threshold_percentage: float
    near_52w_high: List[StockQuoteResponse]
    near_52w_low: List[StockQuoteResponse]
    timestamp: str


class MarketSentimentPulseResponse(BaseSchema):
    overall_sentiment: str
    sentiment_score: float
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    total_articles_analyzed: int
    timestamp: str


# =====================================================================
# CONSOLIDATED MASTER DASHBOARD
# =====================================================================

class HomeDashboardResponse(BaseSchema):
    status: str
    market_overview: MarketOverviewResponse
    advance_decline: AdvanceDeclineResponse
    market_movers: MarketMoversResponse
    sector_performance: List[SectorPerformanceItem]
    quarterly_results: QuarterlyResultsListResponse
    watchlist: WatchlistResponse
    breakouts_52w: HighLow52WeekResponse
    volume_shockers: List[StockQuoteResponse]
    market_sentiment: MarketSentimentPulseResponse
    data_source: str
    timestamp: str


class RefreshStatusResponse(BaseSchema):
    status: str
    message: str
    indices_updated: int
    quotes_updated: int
    timestamp: str
