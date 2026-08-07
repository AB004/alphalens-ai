from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database.session import Base


def utc_now():
    return datetime.utcnow()


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    score = Column(Float, nullable=False)

    recommendation = Column(
        String(20),
        nullable=False,
    )

    confidence = Column(
        Float,
        nullable=False,
    )

    reasoning = Column(
        Text,
        nullable=False,
    )

    generated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    document = relationship("Document")