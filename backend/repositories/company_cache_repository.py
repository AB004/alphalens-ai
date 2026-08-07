from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.models.company_cache import CompanyCache


CACHE_DURATION_HOURS = 24


def create_cache(
    db: Session,
    **kwargs,
) -> CompanyCache:
    """
    Create cache entry for a company.
    """

    cache = CompanyCache(**kwargs)

    db.add(cache)
    db.commit()
    db.refresh(cache)

    return cache


def get_cache(
    db: Session,
    company_id: int,
) -> CompanyCache | None:
    """
    Get cache information for a company.
    """

    return (
        db.query(CompanyCache)
        .filter(
            CompanyCache.company_id == company_id,
        )
        .first()
    )


def update_cache(
    db: Session,
    cache: CompanyCache,
    **kwargs,
) -> CompanyCache:
    """
    Update cache metadata.
    """

    for key, value in kwargs.items():
        setattr(cache, key, value)

    db.commit()
    db.refresh(cache)

    return cache


def refresh_cache(
    db: Session,
    company_id: int,
) -> CompanyCache:
    """
    Update cache timestamps after a successful refresh.
    """

    now = datetime.utcnow()

    cache = get_cache(
        db=db,
        company_id=company_id,
    )

    if cache is None:

        return create_cache(
            db=db,
            company_id=company_id,
            last_profile_update=now,
            last_financial_update=now,
            expires_at=now + timedelta(hours=CACHE_DURATION_HOURS),
        )

    return update_cache(
        db=db,
        cache=cache,
        last_profile_update=now,
        last_financial_update=now,
        expires_at=now + timedelta(hours=CACHE_DURATION_HOURS),
    )


def cache_expired(
    cache: CompanyCache | None,
) -> bool:
    """
    Returns True if cache should be refreshed.
    """

    if cache is None:
        return True

    return cache.expires_at <= datetime.utcnow()


def delete_cache(
    db: Session,
    cache: CompanyCache,
) -> None:
    """
    Delete cache entry.
    """

    db.delete(cache)
    db.commit()