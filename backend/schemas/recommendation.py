from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    document_id: int
    score: float
    recommendation: str
    confidence: float
    reasoning: str