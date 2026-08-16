from datetime import datetime, timezone

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.session import Base


class MarketRecommendation(Base):
    __tablename__ = "market_recommendations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey(
            "companies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    recommendation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    financial_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    financial_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sentiment_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    overall_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v1",
    )

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    company = relationship(
        "Company",
        back_populates="market_recommendations",
    )

    sentiment_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    sentiment_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )