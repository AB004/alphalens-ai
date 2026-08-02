from typing import Optional

from sqlalchemy.orm import Session

from database.models import Document


def create_document(db: Session, **values) -> Document:
    document = Document(**values)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    return db.get(Document, document_id)


def get_document_by_stored_filename(db: Session, stored_filename: str) -> Optional[Document]:
    return db.query(Document).filter(Document.stored_filename == stored_filename).first()


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.upload_timestamp.desc()).all()


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()
