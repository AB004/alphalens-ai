from fastapi import APIRouter

from backend.schemas.conversation import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    MessageResponse,
)
from backend.services.conversation.message_service import (
    conversation_message_service,
)
from backend.services.document_chat.document_chat_service import (
    document_chat_service,
)


router = APIRouter()


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ConversationMessageResponse,
)
def send_message(
    session_id: int,
    request: ConversationMessageRequest,
):
    return document_chat_service.conversation_chat(
        session_id=session_id,
        question=request.question,
    )

@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    session_id: int,
):
    return conversation_message_service.get_messages(
        session_id=session_id,
    )
