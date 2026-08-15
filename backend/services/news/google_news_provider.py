from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode

import requests
import xml.etree.ElementTree as ET

from backend.services.news.provider import (
    NewsArticle,
    NewsProvider,
    PROVIDER_GOOGLE_NEWS,
    CATEGORY_MARKET,
)


class GoogleNewsProvider:
    """
    Google News RSS provider.

    Fetches company-related news from Google News
    and normalizes it into the AlphaLens NewsArticle format.
    """

    BASE_URL = "https://news.google.com/rss/search"

    DEFAULT_LANGUAGE = "en-IN"
    DEFAULT_COUNTRY = "IN"

    REQUEST_TIMEOUT = 15

    def search_news(
        self,
        symbol: str,
        company_name: str,
        limit: int = 20,
    ) -> list[NewsArticle]:

        query = self._build_query(
            symbol=symbol,
            company_name=company_name,
        )

        url = self._build_url(
            query=query,
        )

        response = self._fetch(
            url,
        )

        return self._parse_feed(
            response,
            limit=limit,
        )

    def _build_query(
        self,
        symbol: str,
        company_name: str,
    ) -> str:
        """
        Build the Google News search query.

        Example:

        "Apple Inc" AAPL
        """

        symbol = symbol.strip().upper()
        company_name = company_name.strip()

        return f'"{company_name}" {symbol}'

    def _build_url(
        self,
        query: str,
    ) -> str:
        """
        Build Google News RSS URL.
        """

        params = {
            "q": query,
            "hl": self.DEFAULT_LANGUAGE,
            "gl": self.DEFAULT_COUNTRY,
            "ceid": f"{self.DEFAULT_COUNTRY}:en",
        }

        return (
            f"{self.BASE_URL}"
            f"?{urlencode(params)}"
        )

    def _fetch(
        self,
        url: str,
    ) -> str:
        """
        Download the RSS feed.
        """

        try:

            response = requests.get(
                url,
                timeout=self.REQUEST_TIMEOUT,
                headers={
                    "User-Agent": (
                        "AlphaLens/1.0 "
                        "(Financial Research Assistant)"
                    )
                },
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as exc:

            raise RuntimeError(
                "Failed to fetch Google News RSS feed."
            ) from exc

    def _parse_feed(
        self,
        xml_content: str,
        limit: int,
    ) -> list[NewsArticle]:
        """
        Parse Google News RSS XML into normalized articles.
        """

        try:

            root = ET.fromstring(
                xml_content,
            )

        except ET.ParseError as exc:

            raise RuntimeError(
                "Invalid Google News RSS response."
            ) from exc

        articles: list[NewsArticle] = []

        channel = root.find("channel")

        if channel is None:
            return articles

        for item in channel.findall("item"):

            if len(articles) >= limit:
                break

            article = self._parse_item(
                item,
            )

            if article is None:
                continue

            articles.append(
                article,
            )

        return articles

    def _parse_item(
        self,
        item: ET.Element,
    ) -> NewsArticle | None:
        """
        Convert one RSS item into NewsArticle.
        """

        title = self._get_text(
            item,
            "title",
        )

        url = self._get_text(
            item,
            "link",
        )

        description = self._get_text(
            item,
            "description",
        )

        published_raw = self._get_text(
            item,
            "pubDate",
        )

        source = self._get_source(
            item,
        )

        if not title or not url:
            return None

        published_at = self._parse_date(
            published_raw,
        )

        return {
            "title": title.strip(),
            "summary": self._clean_description(
                description,
            ),
            "content": None,
            "source": source,
            "provider": PROVIDER_GOOGLE_NEWS,
            "category": CATEGORY_MARKET,
            "url": url.strip(),
            "published_at": published_at,
        }

    @staticmethod
    def _get_text(
        element: ET.Element,
        tag: str,
    ) -> str | None:
        """
        Safely retrieve text from an XML element.
        """

        child = element.find(tag)

        if child is None:
            return None

        if child.text is None:
            return None

        return child.text.strip()

    @staticmethod
    def _get_source(
        item: ET.Element,
    ) -> str:
        """
        Extract publisher/source name.

        Google News RSS commonly provides the publisher
        through the <source> element.
        """

        source_element = item.find("source")

        if source_element is None:
            return "Google News"

        source = (
            source_element.text
            or "Google News"
        )

        return source.strip()

    @staticmethod
    def _parse_date(
        value: str | None,
    ) -> datetime | None:
        """
        Convert RSS publication date into datetime.
        """

        if not value:
            return None

        try:

            return parsedate_to_datetime(
                value,
            ).replace(
                tzinfo=None,
            )

        except (TypeError, ValueError):

            return None

    @staticmethod
    def _clean_description(
        description: str | None,
    ) -> str | None:
        """
        Remove basic HTML from RSS descriptions.

        Google News descriptions may contain HTML.
        """

        if not description:
            return None

        import re
        from html import unescape

        text = unescape(
            description,
        )

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        text = text.strip()

        return text or None