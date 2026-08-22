from backend.database.session import SessionLocal

from backend.repositories.conversation_repository import (
    get_session,
)

from backend.repositories.message_repository import (
    get_recent_messages,
)


class MemoryService:
    """
    Handles conversation memory retrieval.
    """

    def get_recent_history(
        self,
        session_id: int,
        limit: int = 10,
    ) -> list[dict]:
        """
        Return recent conversation messages
        formatted for the LLM.
        """

        db = SessionLocal()

        try:

            session = get_session(
                db,
                session_id,
            )

            if session is None:
                return []

            messages = get_recent_messages(
                db,
                session_id=session_id,
                limit=limit,
            )

            history = []

            for message in messages:

                history.append(
                    {
                        "role": message.role,
                        "message": message.message,
                    }
                )

            return history

        finally:
            db.close()

    def build_history(
        self,
        session_id: int,
        limit: int = 10,
    ) -> str:
        """
        Convert recent messages into text
        for prompt injection.
        """

        history = self.get_recent_history(
            session_id=session_id,
            limit=limit,
        )

        if not history:
            return ""

        conversation = []

        for message in history:

            role = message["role"].capitalize()

            conversation.append(
                f"{role}: {message['message']}"
            )

        return "\n".join(conversation)


memory_service = MemoryService()