from fastapi import HTTPException, status

from backend.database.session import SessionLocal

from backend.repositories.conversation_repository import (
    create_session,
    delete_session,
    get_session,
    list_sessions,
    update_session,
)
from backend.repositories.message_repository import (
    create_message,
    list_messages
)


class ConversationService:

    def create(
        self,
        title: str,
        document_ids: list[int],
    ):

        db = SessionLocal()

        try:

            conversation = create_session(
                db,
                title=title,
                document_ids=document_ids,
                settings={
                    "top_k": 10,
                    "temperature": 0.2,
                },
            )

            return conversation

        finally:
            db.close()

    def get(
        self,
        session_id: int,
    ):

        db = SessionLocal()

        try:

            conversation = get_session(
                db,
                session_id,
            )

            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

            return conversation

        finally:
            db.close()

    def list(self):

        db = SessionLocal()

        try:

            return list_sessions(db)

        finally:
            db.close()

    def rename(
        self,
        session_id: int,
        title: str,
    ):

        db = SessionLocal()

        try:

            conversation = get_session(
                db,
                session_id,
            )

            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

            return update_session(
                db,
                conversation,
                title=title,
            )

        finally:
            db.close()

    def delete(
        self,
        session_id: int,
    ):

        db = SessionLocal()

        try:

            conversation = get_session(
                db,
                session_id,
            )

            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

            delete_session(
                db,
                conversation,
            )

            return {
                "message": "Conversation deleted successfully."
            }

        finally:
            db.close()

    def add_user_message(
        self,
        session_id: int,
        message: str,
    ):

        db = SessionLocal()

        try:

            session = get_session(
                db,
                session_id,
            )

            if session is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found.",
                )

            return create_message(
                db,
                session_id=session_id,
                role="user",
                message=message,
            )

        finally:
            db.close()

    def add_assistant_message(
        self,
        session_id: int,
        message: str,
        citations=None,
    ):

        db = SessionLocal()

        try:

            return create_message(
                db,
                session_id=session_id,
                role="assistant",
                message=message,
                citations=citations or [],
            )

        finally:
            db.close()
    def get_messages(
        self,
        session_id: int,
    ):

        db = SessionLocal()

        try:

            session = get_session(
                db,
                session_id,
            )

            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

            return list_messages(
                db,
                session_id=session_id,
            )

        finally:
            db.close()

conversation_service = ConversationService()