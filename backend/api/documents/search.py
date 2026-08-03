from fastapi import APIRouter

from backend.schemas.search import (
    SearchRequest,
    SearchResponse,
)

from backend.services.rag.index_service import (
    search_document,
)

router = APIRouter()


@router.post(
    "/{document_id}/search",
    response_model=SearchResponse,
)
def search(
    document_id: int,
    request: SearchRequest,
):
    return search_document(
        document_id=document_id,
        query=request.query,
        top_k=request.top_k,
    )