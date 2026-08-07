from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from backend.database.session import Base

def utc_now() -> datetime:
    return datetime.utcnow()


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