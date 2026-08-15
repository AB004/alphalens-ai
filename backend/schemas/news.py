from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsResponse(BaseModel):

    id: int

    company_id: int

    title: str

    summary: str | None = None

    content: str | None = None

    source: str

    provider: str

    category: str | None = None

    url: str

    published_at: datetime | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class NewsListResponse(BaseModel):

    symbol: str

    count: int

    articles: list[NewsResponse]


class NewsRefreshResponse(BaseModel):

    message: str

    symbol: str

    count: int