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