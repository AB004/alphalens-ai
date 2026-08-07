from datetime import datetime, timezone

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


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

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

    statement_type = Column(
        String(50),
        nullable=False,
        index=True,
    )
    # income_statement
    # balance_sheet
    # cash_flow

    period_type = Column(
        String(20),
        nullable=False,
    )
    # annual / quarterly

    fiscal_year = Column(
        Integer,
        nullable=False,
    )

    report_date = Column(
        String(30),
        nullable=False,
    )

    data = Column(
        JSON,
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