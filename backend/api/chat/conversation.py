from fastapi import APIRouter

from backend.schemas.conversation import (
    CreateConversationRequest,
    ConversationResponse,
)

from backend.services.chat.conversation_service import (
    conversation_service,
)

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ConversationResponse,
)
def create_conversation(
    request: CreateConversationRequest,
):
    return conversation_service.create(
        title=request.title,
        document_ids=request.document_ids,
    )


@router.get(
    "/sessions",
    response_model=list[ConversationResponse],
)
def list_conversations():
    return conversation_service.list()


@router.get(
    "/sessions/{session_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    session_id: int,
):
    return conversation_service.get(session_id)


@router.delete(
    "/sessions/{session_id}",
)
def delete_conversation(
    session_id: int,
):
    return conversation_service.delete(session_id)