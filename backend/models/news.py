from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database.session import Base


class News(Base):
    __tablename__ = "news"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(500),
        nullable=False,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    content = Column(
        Text,
        nullable=True,
    )

    source = Column(
        String(100),
        nullable=False,
    )

    provider = Column(
        String(50),
        nullable=False,
        index=True,
    )

    category = Column(
        String(50),
        nullable=False,
        default="general",
        index=True,
    )

    url = Column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )

    published_at = Column(
        DateTime,
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    sentiment = relationship(
        "Sentiment",
        back_populates="news",
        uselist=False,
        cascade="all, delete-orphan",
    )