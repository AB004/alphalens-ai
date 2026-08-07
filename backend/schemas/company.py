from datetime import datetime

from pydantic import BaseModel


class CompanyResponse(BaseModel):

    id: int

    symbol: str

    company_name: str

    sector: str | None = None

    industry: str | None = None

    exchange: str | None = None

    currency: str | None = None

    country: str | None = None

    website: str | None = None

    updated_at: datetime

    class Config:
        from_attributes = True


class FinancialStatementResponse(BaseModel):

    statement_type: str

    period_type: str

    fiscal_year: int

    report_date: str

    data: dict

    class Config:
        from_attributes = True

class RefreshResponse(BaseModel):

    message: str

    company_id: int