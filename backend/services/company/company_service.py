from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from backend.database.session import SessionLocal

from backend.repositories.company_repository import (
    create_company,
    get_company_by_symbol,
    update_company,
    search_companies,
    list_companies,
)

from backend.repositories.financial_repository import (
    delete_company_financials,
    upsert_financial_statement,
    get_latest_financials,
)

from backend.repositories.company_cache_repository import (
    get_cache,
    cache_expired,
    refresh_cache,
)

from backend.services.company import provider


class CompanyService:

    CACHE_DURATION = timedelta(hours=24)

    def _save_financials(
        self,
        db,
        company_id: int,
        statement_type: str,
        statements: list[dict],
    ):
        """
        Save or update financial statements.
        """

        for statement in statements:

            upsert_financial_statement(
                db=db,
                company_id=company_id,
                statement_type=statement_type,
                period_type="annual",
                fiscal_year=statement["fiscal_year"],
                report_date=statement["report_date"],
                data=statement["data"],
            )

    def refresh_company(
        self,
        symbol: str,
    ):
        """
        Refresh company information from provider.
        """

        db = SessionLocal()

        try:

            company_data = self._fetch_company_data(
                symbol,
            )

            company = self._persist_company_data(
                db,
                company_data,
            )

            return {
                "company": company,
                "company_data": company_data,
            }

        finally:
            db.close()

    def get_company(
        self,
        symbol: str,
    ):

        db = SessionLocal()

        try:

            company = get_company_by_symbol(
                db,
                symbol,
            )

            if company is None:

                result = self.refresh_company(
                    symbol,
                )

                return result["company"]

            cache = get_cache(
                db,
                company.id,
            )

            if cache_expired(
                cache,
            ):

                db.close()

                result = self.refresh_company(
                    symbol,
                )

                return result["company"]

            return company

        finally:

            if db.is_active:
                db.close()

    def get_financials(
        self,
        symbol: str,
    ):

        company = self.get_company(
            symbol,
        )

        db = SessionLocal()

        try:

            return get_latest_financials(
                db,
                company.id,
            )

        finally:
            db.close()

    def refresh(
        self,
        symbol: str,
    ):

        result = self.refresh_company(
            symbol,
        )

        return {
            "message": "Company refreshed successfully.",
            "company_id": result["company"].id,
        }

    def _fetch_company_data(
        self,
        symbol: str,
    ) -> dict:
        """
        Fetch latest company data from external provider.
        """

        return provider.get_company_data(
            symbol,
        )

    def _persist_company_data(
        self,
        db,
        company_data: dict,
    ):
        """
        Persist company profile and financial statements.
        """

        profile = company_data["profile"]

        company = get_company_by_symbol(
            db,
            profile["symbol"],
        )

        if company is None:

            company = create_company(
                db,
                **profile,
            )

        else:

            company = update_company(
                db,
                company,
                **profile,
            )

        delete_company_financials(
            db,
            company.id,
        )

        self._save_financials(
            db,
            company.id,
            "income_statement",
            company_data["income_statements"],
        )

        self._save_financials(
            db,
            company.id,
            "balance_sheet",
            company_data["balance_sheets"],
        )

        self._save_financials(
            db,
            company.id,
            "cash_flow",
            company_data["cash_flows"],
        )

        refresh_cache(
            db,
            company.id,
        )

        return company

    def list_companies(
        self,
        skip: int = 0,
        limit: int = 100,
    ):

        db = SessionLocal()

        try:

            return list_companies(
                db=db,
                skip=skip,
                limit=limit,
            )

        finally:
            db.close()

    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ):

        db = SessionLocal()

        try:

            return search_companies(
                db=db,
                query=query,
                skip=skip,
                limit=limit,
            )

        finally:
            db.close()

company_service = CompanyService()
