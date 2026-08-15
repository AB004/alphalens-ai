from datetime import datetime
from typing import Protocol, TypedDict


PROVIDER_GOOGLE_NEWS = "google_news"
PROVIDER_NSE = "nse"
PROVIDER_ECONOMIC_TIMES = "economic_times"
PROVIDER_FINNHUB = "finnhub"


CATEGORY_GENERAL = "general"
CATEGORY_MARKET = "market"
CATEGORY_CORPORATE_ANNOUNCEMENT = "corporate_announcement"
CATEGORY_FINANCIAL_RESULT = "financial_result"
CATEGORY_BOARD_MEETING = "board_meeting"
CATEGORY_CORPORATE_ACTION = "corporate_action"
CATEGORY_REGULATORY = "regulatory"


class NewsArticle(TypedDict):
    title: str
    summary: str | None
    content: str | None
    source: str
    provider: str
    category: str
    url: str
    published_at: datetime | None


class NewsProvider(Protocol):

    def search_news(
        self,
        symbol: str,
        company_name: str,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """
        Fetch and normalize news for a company.
        """
        ...