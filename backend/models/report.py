from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
)
from sqlalchemy.orm import relationship

from backend.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocumentReport(Base):
    __tablename__ = "document_reports"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    executive_summary = Column(JSON, nullable=False)

    financial_metrics = Column(JSON, nullable=False)

    swot = Column(JSON, nullable=False)

    risks = Column(JSON, nullable=False)

    opportunities = Column(JSON, nullable=False)

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    document = relationship("Document")