from typing import Any

from pydantic import BaseModel


class ReportResponse(BaseModel):

    document_id: int

    executive_summary: Any

    financial_metrics: Any

    swot: Any

    risks: Any

    opportunities: Any