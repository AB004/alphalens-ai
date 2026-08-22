from sqlalchemy.orm import Session

from backend.models import ConversationSession

from backend.services.chat.conversation_service import (
    conversation_service,
)

from backend.services.company_chat.exceptions import (
    ConversationNotFoundError,
    InvalidConversationError,
)


class CompanyConversationService:

    def get_or_create(
        self,
        db: Session,
        company,
        conversation_id: int | None = None,
    ):
        if conversation_id is not None:

            conversation = db.get(
                ConversationSession,
                conversation_id,
            )

            if conversation is None:
                raise ConversationNotFoundError(
                    f"Conversation {conversation_id} not found."
                )

            if conversation.company_id != company.id:
                raise InvalidConversationError(
                    "Conversation does not belong to this company."
                )

            return conversation

        conversation = ConversationSession(
            title=f"{company.symbol} Chat",
            document_ids=[],
            company_id=company.id,
            settings={
                "top_k": 10,
                "temperature": 0.2,
                "memory_limit": 10,
            },
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    # =========================================================
    # GET SINGLE CONVERSATION
    # =========================================================

    def get(
        self,
        db: Session,
        company_id: int,
        conversation_id: int,
    ):
        """
        Get a conversation and verify that it belongs
        to the requested company.
        """

        conversation = db.get(
            ConversationSession,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found."
            )

        if conversation.company_id != company_id:
            raise InvalidConversationError(
                "Conversation does not belong to this company."
            )

        return conversation

    # =========================================================
    # LIST COMPANY CONVERSATIONS
    # =========================================================

    def list(
        self,
        db: Session,
        company_id: int,
    ):
        """
        Return all conversations for a company.
        """

        return (
            db.query(ConversationSession)
            .filter(
                ConversationSession.company_id == company_id
            )
            .order_by(
                ConversationSession.updated_at.desc()
            )
            .all()
        )

    def validate(
        self,
        db: Session,
        company_id: int,
        conversation_id: int,
    ):
        conversation = db.get(
            ConversationSession,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found."
            )

        if conversation.company_id != company_id:
            raise InvalidConversationError(
                "Conversation does not belong to this company."
            )

        return conversation

    def get_messages(
        self,
        db: Session,
        conversation_id: int,
    ):
        conversation = db.get(
            ConversationSession,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} not found."
            )

        return conversation_service.get_messages(
            session_id=conversation_id,
        )

company_conversation_service = CompanyConversationService()