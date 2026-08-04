from sqlalchemy.orm import Session

from backend.models import ConversationSession


def create_session(
    db: Session,
    **values,
) -> ConversationSession:

    session = ConversationSession(**values)

    db.add(session)

    db.commit()

    db.refresh(session)

    return session


def get_session(
    db: Session,
    session_id: int,
):

    return db.get(
        ConversationSession,
        session_id,
    )


def list_sessions(
    db: Session,
):

    return (
        db.query(ConversationSession)
        .order_by(
            ConversationSession.updated_at.desc()
        )
        .all()
    )


def update_session(
    db: Session,
    session: ConversationSession,
    **values,
):

    for key, value in values.items():
        setattr(
            session,
            key,
            value,
        )

    db.commit()

    db.refresh(session)

    return session


def delete_session(
    db: Session,
    session: ConversationSession,
):

    db.delete(session)

    db.commit()