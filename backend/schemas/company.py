from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class FinancialStatementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    statement_type: str
    period_type: str
    fiscal_year: int
    report_date: str
    data: dict

class RefreshResponse(BaseModel):

    message: str

    company_id: int