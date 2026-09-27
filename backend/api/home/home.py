"""
FastAPI Router for Home Page and Market Intelligence Endpoints.
Module 11.5: Professional Home Page backend APIs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.schemas.home import (
    AddWatchlistRequest,
    AdvanceDeclineResponse,
    HighLow52WeekResponse,
    HomeDashboardResponse,
    MarketMoversResponse,
    MarketOverviewResponse,
    MarketSentimentPulseResponse,
    QuarterlyResultsListResponse,
    RefreshStatusResponse,
    SectorMoversResponse,
    SectorPerformanceItem,
    StockQuoteResponse,
    WatchlistResponse,
)
from backend.services.market.home_service import home_service

router = APIRouter()


# =====================================================================
# CONSOLIDATED MASTER HOME PAGE
# =====================================================================

@router.get(
    "",
    response_model=HomeDashboardResponse,
    summary="Get Consolidated Home Page Dashboard",
    description="Returns the complete, production-grade Home Page payload in a single roundtrip, including market overview, advance/decline, multi-cap movers, sectors, earnings, watchlist, 52-week breakouts, volume shockers, and sentiment pulse.",
)
def get_home_dashboard(
    force_refresh: bool = Query(default=False, description="Force re-seed or refresh data"),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_home_dashboard(db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate home dashboard: {str(exc)}",
        ) from exc


# =====================================================================
# 1. MARKET OVERVIEW
# =====================================================================

@router.get(
    "/overview",
    response_model=MarketOverviewResponse,
    summary="Get Market Overview & Major Indices",
    description="Returns live index values (Nifty 50, Sensex, Bank Nifty, Nifty IT, S&P 500), trading status, and market mood.",
)
def get_market_overview(
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_market_overview(db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market overview: {str(exc)}",
        ) from exc


# =====================================================================
# 2. ADVANCE / DECLINE
# =====================================================================

@router.get(
    "/advance-decline",
    response_model=AdvanceDeclineResponse,
    summary="Get Advance / Decline Ratio & Market Breadth",
    description="Returns market breadth metrics: advances count, declines count, unchanged count, advance/decline ratio, and breadth sentiment.",
)
def get_advance_decline(
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_advance_decline(db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate advance/decline: {str(exc)}",
        ) from exc


# =====================================================================
# 3. TOP GAINERS / LOSERS ACROSS MARKET CAPS
# =====================================================================

@router.get(
    "/movers",
    response_model=MarketMoversResponse,
    summary="Get Top Gainers & Losers across Market Caps",
    description="Returns top gainers, losers, and most active stocks. Filter by cap ('large', 'mid', 'small', or 'all').",
)
def get_market_movers(
    cap: str = Query(
        default="all",
        description="Market cap segment filter: 'large' (high cap), 'mid', 'small', or 'all'",
    ),
    limit: int = Query(default=10, ge=1, le=50, description="Max items per category"),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_market_movers(
            db=db,
            cap=cap if cap != "all" else None,
            limit=limit,
            force_refresh=force_refresh,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market movers: {str(exc)}",
        ) from exc


# =====================================================================
# 4. SECTOR PERFORMANCE & SECTOR TOP MOVERS
# =====================================================================

@router.get(
    "/sectors",
    response_model=List[SectorPerformanceItem],
    summary="Get Sector Performance Heatmap",
    description="Returns performance across all major market sectors, including average returns, advances vs declines, top gainer, top loser, and momentum status.",
)
def get_sector_performance(
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_sector_performance(db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sector performance: {str(exc)}",
        ) from exc


@router.get(
    "/sectors/{sector_name}/movers",
    response_model=SectorMoversResponse,
    summary="Get Top Movers for a Specific Sector",
    description="Returns constituents, top gainers, and top losers for a selected sector (e.g. 'Technology', 'Financial Services', 'Automobile').",
)
def get_sector_movers(
    sector_name: str,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_sector_movers(db, sector_name=sector_name, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sector movers: {str(exc)}",
        ) from exc


# =====================================================================
# 5. QUARTERLY RESULTS BASED STOCKS
# =====================================================================

@router.get(
    "/quarterly-results",
    response_model=QuarterlyResultsListResponse,
    summary="Get Quarterly Results (Upcoming & Recent)",
    description="Returns upcoming earnings announcements and recently declared quarterly results with revenue, profit growth, verdict (Beat/Met/Miss), and stock price impact.",
)
def get_quarterly_results(
    status_filter: str = Query(
        default="all",
        alias="status",
        description="Filter by result status: 'upcoming', 'recent' (declared), or 'all'",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_quarterly_results(
            db=db,
            status=status_filter,
            limit=limit,
            force_refresh=force_refresh,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch quarterly results: {str(exc)}",
        ) from exc


# =====================================================================
# 6. WATCHLIST BASED STOCKS
# =====================================================================

@router.get(
    "/watchlist",
    response_model=WatchlistResponse,
    summary="Get Watchlist Stocks with Live Quotes",
    description="Returns watchlist stocks enriched with real-time price quotes, percentage change, day ranges, and 52-week ranges. Defaults to top tracked bluechips if user has no items.",
)
def get_watchlist(
    user_id: str = Query(default="default", description="User identifier or 'default' for home page trending watchlist"),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_watchlist(db, user_id=user_id, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist: {str(exc)}",
        ) from exc


@router.post(
    "/watchlist",
    status_code=status.HTTP_201_CREATED,
    summary="Add Stock to Watchlist",
    description="Add a ticker symbol to a user's watchlist. Automatically fetches quote data if not previously tracked.",
)
def add_to_watchlist(
    payload: AddWatchlistRequest,
    db: Session = Depends(get_db),
):
    try:
        return home_service.add_to_watchlist(
            db=db,
            symbol=payload.symbol,
            user_id=payload.user_id,
            category=payload.category,
            notes=payload.notes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add symbol to watchlist: {str(exc)}",
        ) from exc


@router.delete(
    "/watchlist/{symbol}",
    summary="Remove Stock from Watchlist",
    description="Removes a stock ticker from user's watchlist.",
)
def remove_from_watchlist(
    symbol: str,
    user_id: str = Query(default="default"),
    db: Session = Depends(get_db),
):
    try:
        return home_service.remove_from_watchlist(db, symbol=symbol, user_id=user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove symbol from watchlist: {str(exc)}",
        ) from exc


# =====================================================================
# 7. 52-WEEK HIGH / LOW BREAKOUTS
# =====================================================================

@router.get(
    "/52-week-high-low",
    response_model=HighLow52WeekResponse,
    summary="Get 52-Week High & Low Breakouts",
    description="Returns stocks trading near or at their 52-week high and 52-week low levels.",
)
def get_52_week_high_low(
    threshold_percent: float = Query(
        default=3.5,
        ge=0.1,
        le=20.0,
        description="Percentage proximity to 52-week extremes",
    ),
    limit: int = Query(default=10, ge=1, le=50),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_52_week_high_low(
            db=db,
            threshold_pct=threshold_percent,
            limit=limit,
            force_refresh=force_refresh,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch 52-week high/low stocks: {str(exc)}",
        ) from exc


# =====================================================================
# 8. VOLUME SHOCKERS & MOST ACTIVE
# =====================================================================

@router.get(
    "/volume-shockers",
    response_model=List[StockQuoteResponse],
    summary="Get Volume Shockers",
    description="Returns stocks experiencing unusually large trading volume surges (volume / 10-day average volume ratio >= threshold).",
)
def get_volume_shockers(
    min_ratio: float = Query(default=1.5, ge=1.0, le=10.0, description="Minimum surge ratio vs 10-day average"),
    limit: int = Query(default=10, ge=1, le=50),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_volume_shockers(
            db=db,
            min_ratio=min_ratio,
            limit=limit,
            force_refresh=force_refresh,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch volume shockers: {str(exc)}",
        ) from exc


# =====================================================================
# 9. MARKET SENTIMENT PULSE
# =====================================================================

@router.get(
    "/sentiment",
    response_model=MarketSentimentPulseResponse,
    summary="Get Market Sentiment Pulse",
    description="Returns market-wide aggregated sentiment breakdown (Bullish/Neutral/Bearish) and composite sentiment score.",
)
def get_market_sentiment(
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_market_sentiment_pulse(db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market sentiment pulse: {str(exc)}",
        ) from exc


# =====================================================================
# 10. ON-DEMAND LIVE REFRESH
# =====================================================================

@router.post(
    "/refresh",
    response_model=RefreshStatusResponse,
    summary="Trigger On-Demand Live Market Refresh",
    description="Triggers live fetch from external market provider for all tracked indices and stocks, updating the database cache.",
)
def refresh_market_data(
    db: Session = Depends(get_db),
):
    try:
        result = home_service.refresh_from_provider(db)
        return {
            "status": "success",
            "message": "Market data refreshed successfully.",
            "indices_updated": result["indices_updated"],
            "quotes_updated": result["quotes_updated"],
            "timestamp": home_service._determine_market_status()["server_time_utc"],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market refresh failed: {str(exc)}",
        ) from exc

# =====================================================================
# 11. IPO ENDPOINTS (optional)
# =====================================================================

from fastapi import Path
from typing import List, Any

@router.get(
    "/ipo/upcoming",
    response_model=List[Any],
    summary="Get Upcoming IPOs",
    description="Returns a list of upcoming IPO details (company name, symbol, issue date, price range, etc.).",
)
def get_upcoming_ipos(
    force_refresh: bool = Query(default=False, description="Force re-seed or refresh IPO data"),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_upcoming_ipos(db=db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch upcoming IPOs: {str(exc)}",
        ) from exc

@router.get(
    "/ipo/recent",
    response_model=List[Any],
    summary="Get Recent IPOs",
    description="Returns a list of IPOs that were listed recently (default last 30 days).",
)
def get_recent_ipos(
    force_refresh: bool = Query(default=False, description="Force re-seed or refresh IPO data"),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_recent_ipos(db=db, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent IPOs: {str(exc)}",
        ) from exc

@router.get(
    "/ipo/{symbol}/performance",
    response_model=List[Any],
    summary="Get IPO Performance",
    description="Returns daily performance metrics for a specific IPO after it has been listed.",
)
def get_ipo_performance(
    symbol: str = Path(..., description="Ticker symbol of the IPO"),
    force_refresh: bool = Query(default=False, description="Force re-seed or refresh performance data"),
    db: Session = Depends(get_db),
):
    try:
        return home_service.get_ipo_performance(db=db, symbol=symbol, force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch IPO performance for {symbol}: {str(exc)}",
        ) from exc
