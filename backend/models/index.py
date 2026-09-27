
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from backend.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DocumentIndex(Base):
    __tablename__ = "document_indexes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    index_path = Column(String(1024), nullable=False)
    embedding_model = Column(String(255), nullable=False)
    vector_dimension = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    indexed_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
