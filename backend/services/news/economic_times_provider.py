from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urljoin
import re
import xml.etree.ElementTree as ET

import requests

from backend.services.news.provider import (
    NewsArticle,
    PROVIDER_ECONOMIC_TIMES,
    CATEGORY_MARKET,
)


class EconomicTimesProvider:
    """
    Economic Times RSS provider.

    ET exposes section-based RSS feeds rather than a simple
    company-symbol news API. We therefore fetch the Stocks
    feed and filter articles locally using the company name
    and symbol.
    """

    BASE_URL = (
        "https://economictimes.indiatimes.com"
    )

    STOCKS_FEED_URL = (
        "https://economictimes.indiatimes.com/"
        "markets/stocks/rssfeeds/2146842.cms"
    )

    REQUEST_TIMEOUT = 15

    HEADERS = {
        "User-Agent": (
            "AlphaLens/1.0 "
            "(Financial Research Assistant)"
        ),
        "Accept": (
            "application/rss+xml,"
            "application/xml,text/xml,*/*"
        ),
    }

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            self.HEADERS
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

        symbol = symbol.strip().upper()
        company_name = company_name.strip()

        if not symbol or not company_name:
            return []

        xml_content = self._fetch_feed()

        items = self._parse_feed(
            xml_content,
        )

        matching_items = self._filter_company_news(
            items=items,
            symbol=symbol,
            company_name=company_name,
        )

        articles = []

        for item in matching_items:

            if len(articles) >= limit:
                break

            article = self._normalize_article(
                item,
            )

            if article is not None:
                articles.append(article)

        return articles

    # ---------------------------------------------------------
    # FETCH
    # ---------------------------------------------------------

    def _fetch_feed(self) -> str:
        """
        Download the ET Stocks RSS feed.
        """

        try:

            response = self.session.get(
                self.STOCKS_FEED_URL,
                timeout=self.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as exc:

            raise RuntimeError(
                "Failed to fetch Economic Times RSS feed."
            ) from exc

    # ---------------------------------------------------------
    # XML PARSING
    # ---------------------------------------------------------

    def _parse_feed(
        self,
        xml_content: str,
    ) -> list[dict[str, Any]]:

        try:

            root = ET.fromstring(
                xml_content,
            )

        except ET.ParseError as exc:

            raise RuntimeError(
                "Invalid Economic Times RSS response."
            ) from exc

        channel = root.find("channel")

        if channel is None:
            return []

        items = []

        for item in channel.findall("item"):

            parsed = self._parse_item(
                item,
            )

            if parsed is not None:
                items.append(parsed)

        return items

    def _parse_item(
        self,
        item: ET.Element,
    ) -> dict[str, Any] | None:

        title = self._get_text(
            item,
            "title",
        )

        link = self._get_text(
            item,
            "link",
        )

        description = self._get_text(
            item,
            "description",
        )

        pub_date = self._get_text(
            item,
            "pubDate",
        )

        if not title or not link:
            return None

        return {
            "title": title,
            "url": self._normalize_url(
                link,
            ),
            "description": description,
            "published_at": self._parse_date(
                pub_date,
            ),
        }

    # ---------------------------------------------------------
    # COMPANY FILTERING
    # ---------------------------------------------------------

    def _filter_company_news(
        self,
        items: list[dict[str, Any]],
        symbol: str,
        company_name: str,
    ) -> list[dict[str, Any]]:

        symbol_normalized = self._normalize_text(
            symbol,
        )

        company_normalized = self._normalize_text(
            company_name,
        )

        company_words = [
            word
            for word in company_normalized.split()
            if len(word) >= 3
        ]

        matching = []

        for item in items:

            title = self._normalize_text(
                item.get("title", ""),
            )

            description = self._normalize_text(
                item.get("description", ""),
            )

            text = (
                f"{title} {description}"
            )

            # Exact symbol match first.
            if self._contains_symbol(
                text,
                symbol_normalized,
            ):
                matching.append(item)
                continue

            # Company-name match.
            if company_normalized in text:
                matching.append(item)
                continue

            # Partial company-name match.
            #
            # Require at least two meaningful words
            # to reduce false positives.
            if len(company_words) >= 2:

                matched_words = sum(
                    1
                    for word in company_words
                    if word in text
                )

                if matched_words >= 2:
                    matching.append(item)

        return matching

    # ---------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------

    def _normalize_article(
        self,
        item: dict[str, Any],
    ) -> NewsArticle | None:

        title = item.get(
            "title",
        )

        url = item.get(
            "url",
        )

        if not title or not url:
            return None

        description = item.get(
            "description",
        )

        return {
            "title": self._clean_text(
                title,
            ),
            "summary": self._clean_description(
                description,
            ),
            "content": None,
            "source": "Economic Times",
            "provider": PROVIDER_ECONOMIC_TIMES,
            "category": CATEGORY_MARKET,
            "url": url,
            "published_at": item.get(
                "published_at",
            ),
        }

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    @staticmethod
    def _parse_date(
        value: str | None,
    ) -> datetime | None:

        if not value:
            return None

        try:

            return parsedate_to_datetime(
                value,
            ).replace(
                tzinfo=None,
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    # ---------------------------------------------------------
    # URL
    # ---------------------------------------------------------

    def _normalize_url(
        self,
        url: str,
    ) -> str:

        url = unescape(
            url.strip(),
        )

        if url.startswith("/"):
            return urljoin(
                self.BASE_URL,
                url,
            )

        return url

    # ---------------------------------------------------------
    # TEXT CLEANING
    # ---------------------------------------------------------

    @staticmethod
    def _clean_description(
        value: str | None,
    ) -> str | None:

        if not value:
            return None

        value = unescape(
            value,
        )

        value = re.sub(
            r"<[^>]+>",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip()

        return value or None

    @staticmethod
    def _clean_text(
        value: str,
    ) -> str:

        value = unescape(
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:

        value = value.lower()

        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ---------------------------------------------------------
    # SYMBOL MATCHING
    # ---------------------------------------------------------

    @staticmethod
    def _contains_symbol(
        text: str,
        symbol: str,
    ) -> bool:

        if not symbol:
            return False

        pattern = (
            rf"\b{re.escape(symbol)}\b"
        )

        return re.search(
            pattern,
            text,
        ) is not None

    # ---------------------------------------------------------
    # XML HELPER
    # ---------------------------------------------------------

    @staticmethod
    def _get_text(
        element: ET.Element,
        tag: str,
    ) -> str | None:

        child = element.find(
            tag,
        )

        if child is None:
            return None

        if child.text is None:
            return None

        return child.text.strip()