from datetime import datetime

from pydantic import BaseModel, Field


class CitationResponse(BaseModel):

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

    id: int

    title: str

    document_ids: list[int]

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):

    role: str

    message: str

    citations: list[CitationResponse] | None = None

    created_at: datetime

    class Config:
        from_attributes = True