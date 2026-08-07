from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
)

from backend.database.session import Base


def utc_now() ->datetime:
    return datetime.utcnow()


class CompanyCache(Base):
    __tablename__ = "company_cache"

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
        unique=True,
        nullable=False,
        index=True,
    )

    last_profile_update = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_financial_update = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
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