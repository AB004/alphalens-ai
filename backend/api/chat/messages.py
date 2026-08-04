from fastapi import APIRouter

from backend.schemas.conversation import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    MessageResponse,
)
from backend.services.chat.conversation_service import (
    conversation_service,
)
from backend.services.chat.chat_service import (
    chat_service,
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
    return chat_service.conversation_chat(
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
    return conversation_service.get_messages(
        session_id=session_id,
    )