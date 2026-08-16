from datetime import datetime, timedelta

from fastapi import HTTPException, status

from backend.database.session import SessionLocal

from backend.repositories.company_repository import (
    get_company_by_symbol,
)
from backend.services.company.company_service import (
    company_service,
)
from backend.repositories.news_repository import (
    create_news_batch,
    get_cache,
    cache_expired,
    list_news,
    list_news_since,
    count_news,
    refresh_cache,
    delete_news_before,
)

from backend.services.news.provider import (
    NewsArticle,
)

from backend.services.news.google_news_provider import (
    GoogleNewsProvider,
)

from backend.services.news.nse_provider import (
    NSEProvider,
)

from backend.services.news.economic_times_provider import (
    EconomicTimesProvider,
)

from backend.services.news.finnhub_provider import (
    FinnhubProvider,
)

import re
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
import logging

logger = logging.getLogger(__name__)

class NewsService:

    CACHE_DURATION = timedelta(
        hours=2,
    )

    NEWS_RETENTION_DAYS = 90

    def __init__(self):

        self.providers = [
            GoogleNewsProvider(),
            NSEProvider(),
            EconomicTimesProvider(),
        ]

        # Finnhub is optional because its company-news
        # endpoint is not intended for Indian companies.
        #
        # We initialize it lazily rather than making the
        # entire NewsService fail if FINNHUB_API_KEY is absent.

        self._finnhub_provider = None

    def _fetch_from_provider(
        self,
        provider,
        symbol: str,
        company_name: str,
        limit: int,
    ) -> list[NewsArticle]:
        """
        Fetch news from a single provider.

        Provider failures are isolated so that one failing
        provider does not break the complete news request.
        """

        provider_name = provider.__class__.__name__

        try:

            logger.info(
                "Fetching news from provider=%s symbol=%s",
                provider_name,
                symbol,
            )

            articles = provider.search_news(
                symbol=symbol,
                company_name=company_name,
                limit=limit,
            )

            if articles is None:

                logger.warning(
                    "Provider returned None: provider=%s symbol=%s",
                    provider_name,
                    symbol,
                )

                return []

            logger.info(
                "Provider returned %d articles: provider=%s symbol=%s",
                len(articles),
                provider_name,
                symbol,
            )

            return articles

        except Exception:

            logger.exception(
                "News provider failed: provider=%s symbol=%s",
                provider_name,
                symbol,
            )

            return []

    # =========================================================
    # PUBLIC API
    # =========================================================

    def get_news(
        self,
        symbol: str,
        limit: int = 20,
        force_refresh: bool = False,
        provider: str | None = None,
    ):

        symbol = symbol.strip().upper()

        if provider is not None:
            provider = provider.strip().lower()

            if not provider:
                provider = None

        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol is required.",
            )

        # -------------------------------------------------
        # Ensure company exists
        # -------------------------------------------------

        company = company_service.get_company(
            symbol,
        )

        company_id = company.id
        company_name = company.company_name

        # -------------------------------------------------
        # Check news cache
        # -------------------------------------------------

        db = SessionLocal()

        try:

            cache = get_cache(
                db,
                company_id,
            )

            if (
                not force_refresh
                and not cache_expired(cache)
            ):

                return list_news(
                    db,
                    company_id=company_id,
                    limit=limit,
                    provider=provider,
                )

        finally:
            db.close()

        # -------------------------------------------------
        # Refresh news
        # -------------------------------------------------

        return self.refresh_news(
            symbol=symbol,
            company_id=company_id,
            company_name=company_name,
            limit=limit,
        )
    # =========================================================
    # REFRESH
    # =========================================================

    def refresh_news(
        self,
        symbol: str,
        company_id: int,
        company_name: str,
        limit: int = 20,
    ) -> list[NewsArticle]:

        articles = self._fetch_from_providers(
            symbol=symbol,
            company_name=company_name,
            limit=limit,
        )

        # 1. Structural validation
        articles = self._validate_articles(
            articles,
        )

        # 2. Remove duplicate URLs/titles
        articles = self._deduplicate(
            articles,
        )

        # 3. Remove low-quality articles
        articles = self._quality_filter(
            articles,
        )

        # 4. Sort newest first
        articles = self._sort_articles(
            articles,
        )

        if not articles:
            logger.warning(
                "News refresh produced no usable "
                "articles: symbol=%s company_id=%s",
                symbol,
                company_id,
            )

            db = SessionLocal()

            try:

                return list_news(
                    db,
                    company_id=company_id,
                    limit=limit,
                )

            finally:

                db.close()
        db = SessionLocal()

        try:

            create_news_batch(
                db=db,
                company_id=company_id,
                articles=articles,
            )

            now = datetime.now(
                timezone.utc,
            )
            expires_at = (
                now + self.CACHE_DURATION
            )

            refresh_cache(
                db=db,
                company_id=company_id,
                expires_at=expires_at,
            )

            retention_date = (
                now
                - timedelta(
                    days=self.NEWS_RETENTION_DAYS,
                )
            )

            delete_news_before(
                db=db,
                company_id=company_id,
                before=retention_date,
            )

            return list_news(
                db,
                company_id=company_id,
                limit=limit,
            )

        finally:

            db.close()

    # =========================================================
    # PROVIDER ORCHESTRATION
    # =========================================================

    def _fetch_from_providers(
        self,
        symbol: str,
        company_name: str,
        limit: int,
    ) -> list[NewsArticle]:

        all_articles: list[NewsArticle] = []

        for provider in self.providers:

            articles = self._fetch_from_provider(
                provider=provider,
                symbol=symbol,
                company_name=company_name,
                limit=limit,
            )

            articles = self._validate_articles(
                articles,
            )

            all_articles.extend(
                articles,
            )

        return all_articles

    # =========================================================
    # FINNHUB
    # =========================================================

    def _get_finnhub_provider(self):

        if self._finnhub_provider is not None:
            return self._finnhub_provider

        try:

            self._finnhub_provider = (
                FinnhubProvider()
            )

        except RuntimeError:

            self._finnhub_provider = None

        return self._finnhub_provider

    # =========================================================
    # DEDUPLICATION
    # =========================================================

    @classmethod
    def _deduplicate(
        cls,
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:

        seen_urls: set[str] = set()
        seen_content: set[str] = set()

        unique_articles: list[NewsArticle] = []

        for article in articles:

            url = article.get("url")
            title = article.get("title")
            source = article.get("source")

            if not url or not title:
                continue

            normalized_url = cls._normalize_url(
                url,
            )

            normalized_title = (
                cls._normalize_text(title)
            )

            normalized_source = (
                cls._normalize_text(
                    source or "",
                )
            )

            # Exact URL duplicate
            if normalized_url in seen_urls:
                continue

            # Same title + source
            content_key = (
                f"{normalized_source}|"
                f"{normalized_title}"
            )

            if content_key in seen_content:
                continue

            seen_urls.add(
                normalized_url,
            )

            seen_content.add(
                content_key,
            )

            unique_articles.append(
                article,
            )

        return unique_articles

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:

        value = value.lower().strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = re.sub(
            r"[^\w\s]",
            "",
            value,
        )

        return value

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:

        try:

            parts = urlsplit(
                url.strip(),
            )

            # Remove tracking parameters.
            tracking_params = {
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "gclid",
                "fbclid",
            }

            query_params = [
                (
                    key,
                    value,
                )
                for key, value in parse_qsl(
                    parts.query,
                    keep_blank_values=True,
                )
                if key.lower()
                not in tracking_params
            ]

            clean_query = urlencode(
                query_params,
            )

            return urlunsplit(
                (
                    parts.scheme.lower(),
                    parts.netloc.lower(),
                    parts.path.rstrip("/"),
                    clean_query,
                    "",
                )
            )

        except Exception:

            return url.strip().lower()

    # =========================================================
    # VALIDATION
    # =========================================================
    
    @classmethod
    def _validate_article(
        cls,
        article: NewsArticle,
    ) -> bool:
        """
        Validate a normalized news article before persistence.
        """

        # Required fields
        title = article.get("title")
        url = article.get("url")
        source = article.get("source")
        provider = article.get("provider")

        if not title or not title.strip():
            return False

        if not url or not url.strip():
            return False

        if not source or not source.strip():
            return False

        if not provider or not provider.strip():
            return False

        # Basic URL validation
        url_lower = url.strip().lower()

        if not (
            url_lower.startswith("http://")
            or url_lower.startswith("https://")
        ):
            return False

        # Reject obviously broken titles
        normalized_title = cls._normalize_text(
            title,
        )

        if len(normalized_title) < 5:
            return False

        # Prevent extremely large malformed payloads
        if len(title) > 1000:
            return False

        if len(url) > 5000:
            return False

        if source and len(source) > 500:
            return False

        return True

    @classmethod
    def _validate_articles(
        cls,
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:

        valid_articles: list[NewsArticle] = []

        for article in articles:

            if not isinstance(
                article,
                dict,
            ):
                continue

            if not cls._validate_article(
                article,
            ):
                continue

            valid_articles.append(
                article,
            )

        return valid_articles

    # =========================================================
    # SORTING
    # =========================================================

    @staticmethod
    def _sort_articles(
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:

        return sorted(
            articles,
            key=lambda article: (
                article.get(
                    "published_at"
                )
                or datetime.min
            ),
            reverse=True,
        )

    # =========================================================
    # NEWS SINCE
    # =========================================================

    def get_news_since(
        self,
        symbol: str,
        since: datetime,
        limit: int = 20,
    ):

        symbol = symbol.strip().upper()

        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol is required.",
            )

        # Ensure company exists.
        company = company_service.get_company(
            symbol,
        )

        db = SessionLocal()

        try:

            return list_news_since(
                db,
                company_id=company.id,
                since=since,
                limit=limit,
            )

        finally:

            db.close()
    
    # =========================================================
    # COUNT
    # =========================================================

    def count(
        self,
        symbol: str,
    ):

        symbol = symbol.strip().upper()

        company = company_service.get_company(
            symbol,
        )

        company_id = company.id

        db = SessionLocal()

        try:

            return count_news(
                db,
                company_id=company_id,
            )

        finally:
            db.close()

    @classmethod
    def _quality_filter(
        cls,
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:

        filtered = []

        for article in articles:

            title = article.get("title", "").strip()
            summary = (
                article.get("summary") or ""
            ).strip()
            url = article.get("url", "").strip()

            # -----------------------------------------
            # Minimum title quality
            # -----------------------------------------

            normalized_title = cls._normalize_text(
                title,
            )

            if len(normalized_title) < 15:
                continue

            # -----------------------------------------
            # Reject obvious junk
            # -----------------------------------------

            junk_phrases = (
                "click here",
                "read more",
                "subscribe now",
                "sign up",
                "advertisement",
                "sponsored content",
            )

            title_lower = title.lower()

            if any(
                phrase in title_lower
                for phrase in junk_phrases
            ):
                continue

            # -----------------------------------------
            # Reject URLs that are not articles
            # -----------------------------------------

            blocked_url_patterns = (
                "/video/",
                "/videos/",
                "/photos/",
                "/gallery/",
            )

            url_lower = url.lower()

            if any(
                pattern in url_lower
                for pattern in blocked_url_patterns
            ):
                continue

            # -----------------------------------------
            # Avoid extremely long junk summaries
            # -----------------------------------------

            if len(summary) > 10000:
                continue

            filtered.append(article)

        return filtered

news_service = NewsService()