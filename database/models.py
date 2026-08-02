from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False, index=True)
    stored_filename = Column(String(320), nullable=False, unique=True, index=True)
    storage_path = Column(String(1024), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False, default="uploaded")
    parsed_text = Column(Text, nullable=True)
    clean_text = Column(Text, nullable=True)
    tables = Column(JSON, nullable=True)
    upload_timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    processed_timestamp = Column(DateTime(timezone=True), nullable=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),)

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    faiss_vector_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class DocumentIndex(Base):
    __tablename__ = "document_indexes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    index_path = Column(String(1024), nullable=False)
    embedding_model = Column(String(255), nullable=False)
    vector_dimension = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    indexed_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
