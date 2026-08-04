from sqlalchemy.orm import Session

from backend.models import ChatMessage


def create_message(
    db: Session,
    **values,
):

    message = ChatMessage(**values)

    db.add(message)

    db.commit()

    db.refresh(message)

    return message


def list_messages(
    db: Session,
    session_id: int,
):

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )


def get_recent_messages(
    db: Session,
    session_id: int,
    limit: int = 10,
):

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .order_by(
            ChatMessage.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return list(reversed(messages))


def delete_messages(
    db: Session,
    session_id: int,
):

    (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .delete()
    )

    db.commit()

def get_message(
    db: Session,
    message_id: int,
):

    return db.get(
        ChatMessage,
        message_id,
    )