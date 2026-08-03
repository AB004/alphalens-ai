from fastapi import APIRouter

from backend.schemas.index import (
    IndexRequest,
    IndexResponse,
)

from backend.services.rag.index_service import (
    create_document_index,
)

router = APIRouter()


@router.post(
    "/{document_id}/index",
    response_model=IndexResponse,
)
def create_index(
    document_id: int,
    request: IndexRequest,
):
    return create_document_index(
        document_id=document_id,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )