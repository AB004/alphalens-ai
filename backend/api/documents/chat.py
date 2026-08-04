from fastapi import APIRouter

from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.services.chat.chat_service import (
    chat_service,
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    return chat_service.chat(
        document_ids=request.document_ids,
        question=request.question,
        top_k=request.top_k,
    )