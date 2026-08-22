from sqlalchemy.orm import Session

from backend.repositories.company_repository import (
    get_company_by_symbol,
)

from backend.services.company_chat.exceptions import (
    CompanyNotFoundError,
)


class CompanyResolver:
    """
    Resolve a company identifier into a Company record.

    Module 11 uses Module 7's company data as the
    canonical source of company identity.
    """

    def resolve(
        self,
        db: Session,
        symbol: str,
    ):
        if not isinstance(symbol, str):
            raise CompanyNotFoundError(
                "Company symbol must be a string."
            )

        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise CompanyNotFoundError(
                "Company symbol cannot be empty."
            )

        company = get_company_by_symbol(
            db=db,
            symbol=normalized_symbol,
        )

        if company is None:
            raise CompanyNotFoundError(
                f"Company '{normalized_symbol}' not found."
            )

        return company

    def resolve_context(
        self,
        db: Session,
        symbol: str,
    ) -> dict:
        """
        Resolve a company and return the normalized
        identity context required by Company Chat.
        """

        company = self.resolve(
            db=db,
            symbol=symbol,
        )

        return {
            "company_id": company.id,
            "symbol": company.symbol,
            "company_name": company.company_name,
            "sector": company.sector,
            "industry": company.industry,
            "exchange": company.exchange,
            "currency": company.currency,
            "country": company.country,
        }


company_resolver = CompanyResolver()