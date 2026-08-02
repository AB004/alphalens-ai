from fastapi import APIRouter

from backend.schemas.rag import IndexRequest, IndexResponse, SearchRequest, SearchResponse
from backend.services.rag.index_service import index_document, search_document


router = APIRouter()


@router.post("/documents/{document_id}/index", response_model=IndexResponse)
def build_document_index(document_id: int, request: IndexRequest):
    return index_document(document_id, request.chunk_size, request.chunk_overlap)


@router.post("/documents/{document_id}/search", response_model=SearchResponse)
def search_document_index(document_id: int, request: SearchRequest):
    return search_document(document_id, request.query, request.top_k)
