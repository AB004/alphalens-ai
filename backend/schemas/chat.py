from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    document_ids: list[int] = Field(..., min_length=1)
    question: str
    top_k: int = 10


class CitationResponse(BaseModel):
    document_id: int
    document_name: str
    page_number: int


class ChatResponse(BaseModel):
    question: str
    answer: str
    citations: list[CitationResponse]