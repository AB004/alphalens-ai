from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from backend.database.session import Base


def utc_now() -> datetime:
    return datetime.utcnow()


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    company_name = Column(
        String(255),
        nullable=False,
    )

    sector = Column(
        String(255),
        nullable=True,
    )

    industry = Column(
        String(255),
        nullable=True,
    )

    exchange = Column(
        String(100),
        nullable=True,
    )

    currency = Column(
        String(20),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    website = Column(
        String(500),
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