from datetime import datetime, timezone

from sqlalchemy import desc,select
from sqlalchemy.orm import Session

from backend.models.news import News
from backend.models.news_cache import NewsCache

def create_news(
    db: Session,
    company_id: int,
    title: str,
    summary: str | None,
    content: str | None,
    source: str,
    provider: str,
    category: str,
    url: str,
    published_at: datetime | None,
):
    """
    Create a news article.
    """

    news = News(
        company_id=company_id,
        title=title,
        summary=summary,
        content=content,
        source=source,
        provider=provider,
        category=category,
        url=url,
        published_at=published_at,
    )

    db.add(news)
    db.commit()
    db.refresh(news)

    return news

def get_news_by_url(
    db: Session,
    url: str,
):
    """
    Find an existing article using its URL.
    """

    return (
        db.query(News)
        .filter(
            News.url == url,
        )
        .first()
    )

def get_news_by_id(
    db: Session,
    news_id: int,
):
    """
    Retrieve a news article by ID.
    """

    return (
        db.query(News)
        .filter(
            News.id == news_id,
        )
        .first()
    )

def list_news(
    db: Session,
    company_id: int,
    skip: int = 0,
    limit: int = 20,
):
    """
    Return latest news for a company.
    """

    return (
        db.query(News)
        .filter(
            News.company_id == company_id,
        )
        .order_by(
            desc(News.published_at),
            desc(News.created_at),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def list_news_since(
    db: Session,
    company_id: int,
    since: datetime,
    skip: int = 0,
    limit: int = 20,
):
    """
    Return news published after a given timestamp.
    """

    return (
        db.query(News)
        .filter(
            News.company_id == company_id,
            News.published_at >= since,
        )
        .order_by(
            desc(News.published_at),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def count_news(
    db: Session,
    company_id: int,
):
    """
    Return total number of news articles
    stored for a company.
    """

    return (
        db.query(News)
        .filter(
            News.company_id == company_id,
        )
        .count()
    )

def delete_news_before(
    db: Session,
    company_id: int,
    before: datetime,
):
    """
    Delete news older than the given timestamp.
    """

    (
        db.query(News)
        .filter(
            News.company_id == company_id,
            News.published_at < before,
        )
        .delete(
            synchronize_session=False,
        )
    )

    db.commit()

def get_cache(
    db: Session,
    company_id: int,
):
    """
    Retrieve news cache information for a company.
    """

    return (
        db.query(NewsCache)
        .filter(
            NewsCache.company_id == company_id,
        )
        .first()
    )

def cache_expired(
    cache: NewsCache | None,
) -> bool:

    if cache is None:
        return True

    now = datetime.now(timezone.utc)

    expires_at = cache.expires_at

    # Handle existing SQLite rows that may be naive.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return expires_at <= now

def refresh_cache(
    db: Session,
    company_id: int,
    expires_at: datetime,
):
    cache = get_cache(
        db,
        company_id,
    )

    now = datetime.now(timezone.utc)

    if cache is None:

        cache = NewsCache(
            company_id=company_id,
            last_updated=now,
            expires_at=expires_at,
        )

        db.add(cache)

    else:

        cache.last_updated = now
        cache.expires_at = expires_at

    db.commit()
    db.refresh(cache)

    return cache

def delete_cache(
    db: Session,
    company_id: int,
):
    """
    Delete the news cache for a company.
    """

    cache = get_cache(
        db,
        company_id,
    )

    if cache is not None:

        db.delete(cache)
        db.commit()

def create_news_batch(
    db,
    company_id: int,
    articles: list[dict],
):
    if not articles:
        return []

    results = []

    for article in articles:

        existing = db.execute(
            select(News).where(
                News.company_id == company_id,
                News.url == article["url"],
            )
        ).scalar_one_or_none()

        if existing:

            existing.title = article["title"]
            existing.summary = article.get("summary")
            existing.content = article.get("content")
            existing.source = article.get("source")
            existing.provider = article.get("provider")
            existing.category = article.get("category")
            existing.published_at = article.get("published_at")

            results.append(existing)
        else:

            news = News(
                company_id=company_id,
                title=article["title"],
                summary=article.get("summary"),
                content=article.get("content"),
                source=article.get("source"),
                provider=article.get("provider"),
                category=article.get("category"),
                url=article["url"],
                published_at=article.get("published_at"),
            )

            db.add(news)
            results.append(news)

    db.commit()

    for news in results:
        db.refresh(news)

    return results