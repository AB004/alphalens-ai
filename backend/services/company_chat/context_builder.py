from dataclasses import dataclass, field
from typing import Any

from backend.services.company_chat.question_classifier import (
    CompanyQuestionType,
)


@dataclass
class CompanyIdentity:
    """
    Canonical company identity used by Company Chat.
    """

    company_id: int
    symbol: str
    company_name: str
    sector: str | None = None
    industry: str | None = None
    exchange: str | None = None
    currency: str | None = None
    country: str | None = None

@dataclass
class CompanyChatContext:
    company: CompanyIdentity

    question: str

    question_type: CompanyQuestionType

    conversation: list[dict[str, Any]] = field(
        default_factory=list,
    )

    financial: Any | None = None

    news: Any | None = None

    sentiment: Any | None = None

    recommendation: Any | None = None

    resolved_question: str | None = None


class CompanyContextBuilder:

    def build(
        self,
        company,
        question: str,
        question_type: CompanyQuestionType,
        conversation: list[dict[str, Any]] | None = None,
        resolved_question: str | None = None,
        financial: Any | None = None,
        news: Any | None = None,
        sentiment: Any | None = None,
        recommendation: Any | None = None,
    ) -> CompanyChatContext:

        identity = CompanyIdentity(
            company_id=company.id,
            symbol=company.symbol,
            company_name=company.company_name,
            sector=company.sector,
            industry=company.industry,
            exchange=company.exchange,
            currency=company.currency,
            country=company.country,
        )

        return CompanyChatContext(
            company=identity,
            question=question,
            question_type=question_type,
            conversation=conversation or [],
            resolved_question=resolved_question,
            financial=financial,
            news=news,
            sentiment=sentiment,
            recommendation=recommendation,
        )


company_context_builder = CompanyContextBuilder()