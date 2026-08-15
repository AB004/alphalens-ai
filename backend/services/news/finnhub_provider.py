from datetime import date, datetime, timedelta
from typing import Any

import os

import requests

from backend.services.news.provider import (
    NewsArticle,
    PROVIDER_FINNHUB,
    CATEGORY_MARKET,
)


class FinnhubProvider:
    """
    Finnhub company-news provider.

    Finnhub's company-news endpoint requires:
        symbol
        from
        to

    The endpoint is documented by Finnhub for
    North American companies.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    COMPANY_NEWS_ENDPOINT = "/company-news"

    REQUEST_TIMEOUT = 15

    DEFAULT_LOOKBACK_DAYS = 7

    def __init__(
        self,
        api_key: str | None = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("FINNHUB_API_KEY")
        )

        if not self.api_key:
            raise RuntimeError(
                "FINNHUB_API_KEY is not configured."
            )

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": (
                    "AlphaLens/1.0 "
                    "(Financial Research Assistant)"
                ),
                "X-Finnhub-Token": self.api_key,
            }
        )

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def search_news(
        self,
        symbol: str,
        company_name: str,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """
        Fetch latest company news from Finnhub.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            return []

        to_date = date.today()

        from_date = (
            to_date
            - timedelta(
                days=self.DEFAULT_LOOKBACK_DAYS
            )
        )

        data = self._fetch_company_news(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
        )

        return self._normalize_articles(
            data=data,
            limit=limit,
        )

    # ---------------------------------------------------------
    # HTTP
    # ---------------------------------------------------------

    def _fetch_company_news(
        self,
        symbol: str,
        from_date: date,
        to_date: date,
    ) -> list[dict[str, Any]]:

        url = (
            f"{self.BASE_URL}"
            f"{self.COMPANY_NEWS_ENDPOINT}"
        )

        params = {
            "symbol": symbol,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        try:

            response = self.session.get(
                url,
                params=params,
                timeout=self.REQUEST_TIMEOUT,
            )

            if response.status_code == 429:

                raise RuntimeError(
                    "Finnhub API rate limit exceeded."
                )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as exc:

            raise RuntimeError(
                "Failed to fetch Finnhub company news."
            ) from exc

        except ValueError as exc:

            raise RuntimeError(
                "Finnhub returned an invalid JSON response."
            ) from exc

        if not isinstance(
            payload,
            list,
        ):
            return []

        return payload

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def _normalize_articles(
        self,
        data: list[dict[str, Any]],
        limit: int,
    ) -> list[NewsArticle]:

        articles: list[NewsArticle] = []

        for item in data:

            if len(articles) >= limit:
                break

            article = self._normalize_article(
                item,
            )

            if article is None:
                continue

            articles.append(
                article,
            )

        return articles

    def _normalize_article(
        self,
        item: dict[str, Any],
    ) -> NewsArticle | None:

        headline = self._get_string(
            item,
            "headline",
        )

        url = self._get_string(
            item,
            "url",
        )

        if not headline or not url:
            return None

        summary = self._get_string(
            item,
            "summary",
        )

        source = self._get_string(
            item,
            "source",
        )

        published_at = self._parse_timestamp(
            item.get(
                "datetime",
            )
        )

        return {
            "title": headline,

            "summary": summary,

            "content": None,

            "source": (
                source
                or "Finnhub"
            ),

            "provider": PROVIDER_FINNHUB,

            "category": CATEGORY_MARKET,

            "url": url,

            "published_at": published_at,
        }

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> datetime | None:

        if value is None:
            return None

        try:

            timestamp = int(
                value,
            )

            return datetime.fromtimestamp(
                timestamp,
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _get_string(
        item: dict[str, Any],
        key: str,
    ) -> str | None:

        value = item.get(
            key,
        )

        if value is None:
            return None

        value = str(
            value,
        ).strip()

        return value or None