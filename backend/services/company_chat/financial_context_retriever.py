from sqlalchemy.orm import Session

from backend.repositories.financial_repository import (
    get_latest_financials,
)


class FinancialContextRetriever:
    """
    Retrieves financial information required by
    Company Chat.

    Module 7 remains the source of truth for
    financial data.
    """

    def retrieve(
        self,
        db: Session,
        company_id: int,
    ) -> dict:
        """
        Retrieve financial context for a company.
        """

        statements = get_latest_financials(
            db=db,
            company_id=company_id,
        )

        serialized_statements = [
            self._serialize_statement(statement)
            for statement in statements
        ]

        return {
            "available": bool(serialized_statements),
            "statements": serialized_statements,
        }

    @staticmethod
    def _serialize_statement(
        statement,
    ) -> dict:
        return {
            "id": statement.id,
            "statement_type": (
                statement.statement_type
            ),
            "period_type": (
                statement.period_type
            ),
            "fiscal_year": (
                statement.fiscal_year
            ),
            "report_date": (
                statement.report_date
            ),
            "data": statement.data,
        }


financial_context_retriever = (
    FinancialContextRetriever()
)