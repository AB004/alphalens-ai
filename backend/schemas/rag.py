from datetime import datetime

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    chunk_size: int = Field(default=1200, ge=300, le=3000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)


class IndexResponse(BaseModel):
    document_id: int
    status: str
    chunk_count: int
    vector_dimension: int
    embedding_model: str
    indexed_at: datetime


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
