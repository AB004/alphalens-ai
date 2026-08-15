from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
)

from backend.database.session import Base


class NewsCache(Base):
    __tablename__ = "news_cache"

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
        unique=True,
        index=True,
    )

    last_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )