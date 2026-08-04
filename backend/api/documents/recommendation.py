from fastapi import APIRouter

from backend.schemas.recommendation import (
    RecommendationResponse,
)

from backend.services.recommendation.recommendation_service import (
    generate_recommendation,
    fetch_recommendation,
)

router = APIRouter()


@router.post(
    "/{document_id}/recommendation",
    response_model=RecommendationResponse,
)
def create_recommendation(document_id: int):
    return generate_recommendation(
        document_id
    )


@router.get(
    "/{document_id}/recommendation",
    response_model=RecommendationResponse,
)
def get_recommendation(document_id: int):
    return fetch_recommendation(
        document_id
    )