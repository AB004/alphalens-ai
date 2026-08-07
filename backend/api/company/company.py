from fastapi import APIRouter,Query

from backend.schemas.company import (
    CompanyResponse,
    FinancialStatementResponse,
    RefreshResponse,
)

from backend.services.company.company_service import (
    company_service,
)

router = APIRouter()

@router.get(
    "/search",
    response_model=list[CompanyResponse],
)
def search_companies(
    q: str,
    skip: int = 0,
    limit: int = 20,
):

    return company_service.search(
        query=q,
        skip=skip,
        limit=limit,
    )

@router.get(
    "/{symbol}",
    response_model=CompanyResponse,
)
def get_company(
    symbol: str,
):

    return company_service.get_company(
        symbol,
    )

@router.get(
    "/{symbol}/financials",
    response_model=list[FinancialStatementResponse],
)
def get_financials(
    symbol: str,
):

    return company_service.get_financials(
        symbol,
    )

@router.post(
    "/{symbol}/refresh",
    response_model=RefreshResponse,
)
def refresh_company(
    symbol: str,
):

    return company_service.refresh(
        symbol,
    )


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def list_companies(
    skip: int = 0,
    limit: int = Query(
        default=100,
        le=100,
    ),
):

    return company_service.list_companies(
        skip=skip,
        limit=limit,
    )

