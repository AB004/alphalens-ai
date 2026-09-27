from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CitationResponse(BaseModel):
    id: int | None = None
    document_id: int
    document_name: str
    page_number: int


class ConversationMessageRequest(BaseModel):
    question: str


class ConversationMessageResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]


class CreateConversationRequest(BaseModel):
    title: str
    document_ids: list[int] = Field(
        ...,
        min_length=1,
    )


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    document_ids: list[int]
    company_id: int | None = None
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    message: str
    citations: list[CitationResponse] | None = None
    created_at: datetime