"""Shared persistence operations for document and company chat messages."""

from fastapi import HTTPException, status

from backend.database.session import SessionLocal
from backend.repositories.conversation_repository import get_session
from backend.repositories.message_repository import create_message, list_messages


class ConversationMessageService:
    """Store and retrieve messages for any conversation type."""

    def add_user_message(self, session_id: int, message: str):
        return self._add_message(session_id, "user", message)

    def add_assistant_message(
        self,
        session_id: int,
        message: str,
        citations: list | None = None,
    ):
        return self._add_message(
            session_id,
            "assistant",
            message,
            citations or [],
        )

    def get_messages(self, session_id: int):
        db = SessionLocal()
        try:
            if get_session(db, session_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )
            return list_messages(db, session_id=session_id)
        finally:
            db.close()

    def _add_message(
        self,
        session_id: int,
        role: str,
        message: str,
        citations: list | None = None,
    ):
        db = SessionLocal()
        try:
            if get_session(db, session_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )
            return create_message(
                db,
                session_id=session_id,
                role=role,
                message=message,
                citations=citations or [],
            )
        finally:
            db.close()


conversation_message_service = ConversationMessageService()
