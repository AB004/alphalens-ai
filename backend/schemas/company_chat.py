from datetime import datetime

from pydantic import BaseModel, Field


class CompanyChatRequest(BaseModel):
    conversation_id: int | None = Field(
        default=None,
        description="Existing conversation ID. "
        "If omitted, a new conversation is created.",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Company-related question.",
    )


class CompanyChatSource(BaseModel):
    type: str

    source: str | None = None

    title: str | None = None

    reference_id: int | None = None

    url: str | None = None


class CompanyChatResponse(BaseModel):
    conversation_id: int

    symbol: str

    company_name: str

    answer: str

    sources: list[CompanyChatSource]


from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CompanyConversationResponse(BaseModel):

    id: int

    title: str

    company_id: int

    document_ids: list[int]

    settings: dict[str, Any] | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
    
class CompanyConversationListResponse(BaseModel):
    symbol: str

    conversations: list[CompanyConversationResponse]

class CompanyConversationMessage(BaseModel):
    id: int
    role: str
    message: str
    citations: list | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyConversationDetailResponse(BaseModel):
    id: int
    title: str
    company_id: int
    created_at: datetime
    updated_at: datetime
    messages: list[CompanyConversationMessage]