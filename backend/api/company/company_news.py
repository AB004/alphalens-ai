from fastapi import APIRouter, Query

from backend.schemas.news import (
    NewsListResponse,
    NewsRefreshResponse,
)

from backend.services.news.news_service import (
    news_service,
)


router = APIRouter()


@router.get(
    "/{symbol}/news",
)
def get_company_news(
    symbol: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=500,
    ),
    provider: str | None = Query(
        default=None,
    ),
    force_refresh: bool = False,
):
    return news_service.get_news(
        symbol=symbol,
        limit=limit,
        force_refresh=force_refresh,
        provider=provider,
    )

@router.get(
    "/{symbol}/news/count",
)
def get_company_news_count(
    symbol: str,
):

    count = news_service.count(
        symbol=symbol,
    )

    return {
        "symbol": symbol.upper(),
        "count": count,
    }


@router.post(
    "/{symbol}/news/refresh",
    response_model=NewsRefreshResponse,
)
def refresh_company_news(
    symbol: str,
):

    # First resolve the company.
    #
    # news_service.get_news() already knows how
    # to resolve the company and refresh its cache.

    articles = news_service.get_news(
        symbol=symbol,
        limit=100,
        force_refresh=True,
    )

    return {
        "message": "News refreshed successfully.",
        "symbol": symbol.upper(),
        "count": len(articles),
    }