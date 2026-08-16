from datetime import datetime, timedelta, timezone

from backend.models.market_recommendation import (
    MarketRecommendation,
)


# ============================================================
# CACHE CONFIGURATION
# ============================================================

MARKET_RECOMMENDATION_CACHE_TTL_MINUTES = 60


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_datetime(
    value: datetime,
) -> datetime:
    """
    Normalize a datetime so naive SQLite timestamps
    can safely be compared with UTC timestamps.
    """

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc,
        )

    return value.astimezone(timezone.utc)


def is_recommendation_fresh(
    recommendation,
    sentiment_limit: int,
    provider: str | None,
    ttl_minutes: int = 60,
) -> bool:

    if recommendation is None:
        return False

    if recommendation.sentiment_limit != sentiment_limit:
        return False

    if recommendation.sentiment_provider != provider:
        return False

    created_at = _normalize_datetime(
        recommendation.created_at,
    )

    expires_at = (
        created_at
        + timedelta(minutes=ttl_minutes)
    )

    return expires_at > _utc_now()


def get_recommendation_expiry(
    recommendation: MarketRecommendation,
    ttl_minutes: int = MARKET_RECOMMENDATION_CACHE_TTL_MINUTES,
) -> datetime:
    """
    Return the expiry time of a recommendation.
    """

    created_at = _normalize_datetime(
        recommendation.created_at,
    )

    return (
        created_at
        + timedelta(minutes=ttl_minutes)
    )


def get_cache_age_seconds(
    recommendation: MarketRecommendation,
) -> float:
    """
    Return the age of a recommendation in seconds.
    """

    created_at = _normalize_datetime(
        recommendation.created_at,
    )

    return (
        _utc_now() - created_at
    ).total_seconds()