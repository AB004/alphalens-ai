from sqlalchemy.orm import Session

from backend.models.company import Company

from sqlalchemy import or_

def create_company(
    db: Session,
    **kwargs,
) -> Company:
    """
    Create a new company.
    """

    company = Company(**kwargs)

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def get_company(
    db: Session,
    company_id: int,
) -> Company | None:
    """
    Get company by primary key.
    """

    return (
        db.query(Company)
        .filter(
            Company.id == company_id,
        )
        .first()
    )


def get_company_by_symbol(
    db: Session,
    symbol: str,
) -> Company | None:
    """
    Get company using ticker symbol.
    """

    return (
        db.query(Company)
        .filter(
            Company.symbol == symbol.upper(),
        )
        .first()
    )


def list_companies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Company]:
    """
    Return all companies.
    """

    return (
        db.query(Company)
        .order_by(
            Company.company_name.asc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_company(
    db: Session,
    company: Company,
    **kwargs,
) -> Company:
    """
    Update company fields.
    """

    for key, value in kwargs.items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)

    return company


def delete_company(
    db: Session,
    company: Company,
) -> None:
    """
    Delete company.
    """

    db.delete(company)
    db.commit()

def search_companies(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
) -> list[Company]:
    """
    Search companies by symbol or company name.
    """

    search = f"%{query}%"

    return (
        db.query(Company)
        .filter(
            or_(
                Company.symbol.ilike(search),
                Company.company_name.ilike(search),
            )
        )
        .order_by(
            Company.company_name.asc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def list_companies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Company]:
    """
    Return cached companies.
    """

    return (
        db.query(Company)
        .order_by(
            Company.company_name.asc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

