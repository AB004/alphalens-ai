"""Reusable FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.database.session import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per request."""

    yield from _get_db()
