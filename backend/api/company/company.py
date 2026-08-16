from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal

from backend.services.sentiment import (
    sentiment_service,
)

from backend.schemas.company import (
    CompanyResponse,
    FinancialStatementResponse,
    RefreshResponse,
)

from backend.services.company.company_service import (
    company_service,
)

from backend.repositories.company_repository import (
    get_company_by_symbol,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

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

@router.get(
    "/{symbol}/sentiment",
)
def get_company_sentiment(
    symbol: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    provider: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    """
    Return aggregated sentiment for a company.

    Optionally filter by news provider.
    """

    try:

        return (
            sentiment_service
            .get_company_sentiment_by_symbol(
                db=db,
                symbol=symbol,
                limit=limit,
                provider=provider,
            )
        )

    except ValueError as exc:

        message = str(exc)

        if "not found" in message.lower():

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

@router.post(
    "/{symbol}/sentiment/analyze",
)
def analyze_company_sentiment(
    symbol: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    provider: str | None = Query(
        default=None,
    ),
    batch_size: int = Query(
        default=16,
        ge=1,
        le=128,
    ),
    db: Session = Depends(get_db),
):
    """
    Analyze unanalyzed news for a company.

    This endpoint performs FinBERT inference.
    """

    symbol = symbol.strip().upper()

    company = get_company_by_symbol(
        db,
        symbol,
    )

    if company is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Company '{symbol}' not found."
            ),
        )

    try:

        results = (
            sentiment_service
            .analyze_company_news(
                db=db,
                company_id=company.id,
                limit=limit,
                batch_size=batch_size,
                provider=provider,
            )
        )

        return {
            "symbol": company.symbol,
            "analyzed_count": len(results),
            "sentiments": results,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to analyze company news."
            ),
        ) from exc