from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from backend.database.session import Base


def utc_now() -> datetime:
    return datetime.utcnow()


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    document_ids = Column(
        JSON,
        nullable=False,
    )

    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    settings = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )