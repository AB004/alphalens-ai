from datetime import datetime

from pydantic import BaseModel, Field



class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    chunk_id: int
    chunk_index: int
    page_number: int
    text: str
    score: float


class SearchResponse(BaseModel):
    document_id: int
    query: str
    results: list[SearchResult]
