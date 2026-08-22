from sqlalchemy.orm import Session

from backend.models.financial_statement import FinancialStatement


def save_financial_statement(
    db: Session,
    **kwargs,
) -> FinancialStatement:
    """
    Save a financial statement.
    """

    statement = FinancialStatement(**kwargs)

    db.add(statement)
    db.commit()
    db.refresh(statement)

    return statement


def get_financial_statement(
    db: Session,
    company_id: int,
    statement_type: str,
    period_type: str | None = None,
) -> list[FinancialStatement]:
    """
    Return financial statements of a given type.
    """

    query = (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.statement_type == statement_type,
        )
    )

    if period_type:
        query = query.filter(
            FinancialStatement.period_type == period_type,
        )

    return (
        query.order_by(
            FinancialStatement.fiscal_year.desc(),
        )
        .all()
    )


def get_latest_financial_statement(
    db: Session,
    company_id: int,
    statement_type: str,
) -> FinancialStatement | None:
    """
    Return the latest financial statement.
    """

    return (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.statement_type == statement_type,
        )
        .order_by(
            FinancialStatement.fiscal_year.desc(),
        )
        .first()
    )


def get_latest_financials(
    db: Session,
    company_id: int,
) -> list[FinancialStatement]:
    """
    Return all financial statements for a company.
    """

    return (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
        )
        .order_by(
            FinancialStatement.statement_type.asc(),
            FinancialStatement.fiscal_year.desc(),
        )
        .all()
    )


def financial_statement_exists(
    db: Session,
    company_id: int,
    statement_type: str,
    fiscal_year: int,
    period_type: str,
) -> FinancialStatement | None:
    """
    Check whether a financial statement already exists.
    """

    return (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
            FinancialStatement.statement_type == statement_type,
            FinancialStatement.fiscal_year == fiscal_year,
            FinancialStatement.period_type == period_type,
        )
        .first()
    )


def update_financial_statement(
    db: Session,
    statement: FinancialStatement,
    **kwargs,
) -> FinancialStatement:
    """
    Update an existing financial statement.
    """

    for key, value in kwargs.items():
        setattr(statement, key, value)

    db.commit()
    db.refresh(statement)

    return statement


def upsert_financial_statement(
    db: Session,
    company_id: int,
    statement_type: str,
    period_type: str,
    fiscal_year: int,
    report_date: str,
    data: dict,
) -> FinancialStatement:
    """
    Create or update a financial statement.
    """

    statement = financial_statement_exists(
        db=db,
        company_id=company_id,
        statement_type=statement_type,
        fiscal_year=fiscal_year,
        period_type=period_type,
    )

    if statement:

        return update_financial_statement(
            db=db,
            statement=statement,
            report_date=report_date,
            data=data,
        )

    return save_financial_statement(
        db=db,
        company_id=company_id,
        statement_type=statement_type,
        period_type=period_type,
        fiscal_year=fiscal_year,
        report_date=report_date,
        data=data,
    )


def delete_financial_statement(
    db: Session,
    statement: FinancialStatement,
) -> None:
    """
    Delete one financial statement.
    """

    db.delete(statement)
    db.commit()


def delete_company_financials(
    db: Session,
    company_id: int,
) -> None:
    """
    Delete all financial statements of a company.
    """

    (
        db.query(FinancialStatement)
        .filter(
            FinancialStatement.company_id == company_id,
        )
        .delete(
            synchronize_session=False,
        )
    )

    db.commit()