from fastapi import APIRouter

from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.services.document_chat.document_chat_service import (
    document_chat_service,
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    return document_chat_service.chat(
        document_ids=request.document_ids,
        question=request.question,
        top_k=request.top_k,
    )
