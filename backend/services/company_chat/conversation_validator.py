from sqlalchemy.orm import Session

from backend.services.company_chat.exceptions import (
    ConversationNotFoundError,
    InvalidConversationError,
)

from backend.repositories.conversation_repository import (
    get_session,
)


class CompanyConversationValidator:
    """
    Validate that a conversation belongs to
    the requested company.
    """

    def validate(
        self,
        db: Session,
        conversation_id: int,
        company_id: int,
    ):

        conversation = get_session(
            db,
            conversation_id,
        )

        if conversation is None:

            raise ConversationNotFoundError(
                "Conversation not found."
            )

        if conversation.company_id != company_id:

            raise InvalidConversationError(
                "Conversation does not belong "
                "to the requested company."
            )

        return conversation


company_conversation_validator = (
    CompanyConversationValidator()
)