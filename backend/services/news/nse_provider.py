from datetime import datetime
from typing import Any

import requests

from backend.services.news.provider import (
    NewsArticle,
    PROVIDER_NSE,
    CATEGORY_CORPORATE_ANNOUNCEMENT,
    CATEGORY_CORPORATE_ACTION,
    CATEGORY_FINANCIAL_RESULT,
    CATEGORY_BOARD_MEETING,
)


class NSEProvider:
    """
    NSE India news/corporate-filings provider.

    Fetches company-specific corporate announcements from NSE
    and normalizes them into AlphaLens NewsArticle objects.
    """

    BASE_URL = "https://www.nseindia.com"

    ANNOUNCEMENTS_ENDPOINT = (
        "/api/corporate-announcements"
    )

    REQUEST_TIMEOUT = 15

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": (
            "https://www.nseindia.com/"
            "companies-listing/"
            "corporate-filings-announcements"
        ),
    }

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
        )

    def search_news(
        self,
        symbol: str,
        company_name: str,
        limit: int = 20,
    ) -> list[NewsArticle]:

        symbol = symbol.strip().upper()

        if not symbol:
            return []

        data = self._fetch_announcements(
            symbol=symbol,
        )

        return self._normalize_articles(
            data=data,
            symbol=symbol,
            limit=limit,
        )

    # ---------------------------------------------------------
    # HTTP
    # ---------------------------------------------------------

    def _bootstrap_session(self):
        """
        Visit NSE first so the session receives the cookies
        required by subsequent API requests.
        """

        response = self.session.get(
            self.BASE_URL,
            timeout=self.REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    def _fetch_announcements(
        self,
        symbol: str,
    ) -> list[dict[str, Any]]:

        self._bootstrap_session()

        url = (
            f"{self.BASE_URL}"
            f"{self.ANNOUNCEMENTS_ENDPOINT}"
        )

        params = {
            "index": "equities",
            "symbol": symbol,
        }

        try:

            response = self.session.get(
                url,
                params=params,
                timeout=self.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as exc:

            raise RuntimeError(
                "Failed to fetch NSE corporate announcements."
            ) from exc

        except ValueError as exc:

            raise RuntimeError(
                "NSE returned an invalid JSON response."
            ) from exc

        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):

            # Some NSE endpoints wrap the records.
            for key in (
                "data",
                "results",
                "records",
            ):

                value = payload.get(key)

                if isinstance(value, list):
                    return value

        return []

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def _normalize_articles(
        self,
        data: list[dict[str, Any]],
        symbol: str,
        limit: int,
    ) -> list[NewsArticle]:

        articles: list[NewsArticle] = []

        for item in data:

            if len(articles) >= limit:
                break

            article = self._normalize_article(
                item=item,
                symbol=symbol,
            )

            if article is None:
                continue

            articles.append(article)

        return articles

    def _normalize_article(
        self,
        item: dict[str, Any],
        symbol: str,
    ) -> NewsArticle | None:

        title = self._first_value(
            item,
            "desc",
            "subject",
            "title",
            "headline",
        )

        if not title:
            return None

        description = self._first_value(
            item,
            "attchmntText",
            "description",
            "details",
            "summary",
        )

        url = self._build_article_url(
            item=item,
            symbol=symbol,
        )

        published_at = self._parse_date(
            self._first_value(
                item,
                "an_dt",
                "broadcastDateTime",
                "broadcastDate",
                "date",
            )
        )

        category = self._detect_category(
            title=title,
        )

        return {
            "title": title.strip(),

            "summary": (
                description.strip()
                if description
                else None
            ),

            "content": None,

            "source": "NSE India",

            "provider": PROVIDER_NSE,

            "category": category,

            "url": url,

            "published_at": published_at,
        }

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    @staticmethod
    def _detect_category(
        title: str,
    ) -> str:

        value = title.lower()

        if any(
            keyword in value
            for keyword in (
                "financial result",
                "financial results",
                "quarterly result",
                "quarterly results",
                "earnings",
            )
        ):
            return CATEGORY_FINANCIAL_RESULT

        if any(
            keyword in value
            for keyword in (
                "board meeting",
                "board of directors",
                "meeting of board",
            )
        ):
            return CATEGORY_BOARD_MEETING

        if any(
            keyword in value
            for keyword in (
                "dividend",
                "bonus",
                "split",
                "buyback",
                "buy-back",
                "rights issue",
                "record date",
            )
        ):
            return CATEGORY_CORPORATE_ACTION

        return CATEGORY_CORPORATE_ANNOUNCEMENT

    # ---------------------------------------------------------
    # URL
    # ---------------------------------------------------------

    def _build_article_url(
        self,
        item: dict[str, Any],
        symbol: str,
    ) -> str:

        # Prefer an explicit URL supplied by NSE.
        url = self._first_value(
            item,
            "url",
            "link",
            "detailUrl",
            "attchmntFile",
        )

        if url:
            return url

        # Stable fallback for deduplication.
        #
        # This is not necessarily the original attachment URL,
        # but gives us a deterministic URL-like identifier.
        timestamp = self._first_value(
            item,
            "an_dt",
            "broadcastDateTime",
            "broadcastDate",
        )

        return (
            f"{self.BASE_URL}/"
            f"companies-listing/"
            f"corporate-filings-announcements"
            f"?symbol={symbol}"
            f"&date={timestamp or ''}"
        )

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    @staticmethod
    def _parse_date(
        value: Any,
    ) -> datetime | None:

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.replace(
                tzinfo=None,
            )

        value = str(value).strip()

        if not value:
            return None

        formats = (
            "%d-%b-%Y %H:%M:%S",
            "%d-%b-%Y %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        )

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt,
                )

            except ValueError:
                continue

        return None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _first_value(
        item: dict[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:

            value = item.get(key)

            if value is not None:

                if isinstance(value, str):

                    value = value.strip()

                    if not value:
                        continue

                return value

        return None