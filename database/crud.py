from typing import Optional

from sqlalchemy.orm import Session

from database.models import Document, DocumentChunk, DocumentIndex


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


def get_document_index(db: Session, document_id: int) -> Optional[DocumentIndex]:
    return db.query(DocumentIndex).filter(DocumentIndex.document_id == document_id).first()


def get_chunks_for_document(db: Session, document_id: int) -> list[DocumentChunk]:
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def replace_document_index(
    db: Session,
    document: Document,
    index_values: dict,
    chunks: list[dict],
) -> DocumentIndex:
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
    db.query(DocumentIndex).filter(DocumentIndex.document_id == document.id).delete()
    document_index = DocumentIndex(document_id=document.id, **index_values)
    db.add(document_index)
    db.add_all([DocumentChunk(document_id=document.id, **chunk) for chunk in chunks])
    db.commit()
    db.refresh(document_index)
    return document_index


def delete_document_index(db: Session, document_id: int) -> Optional[DocumentIndex]:
    document_index = get_document_index(db, document_id)
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    if document_index:
        db.delete(document_index)
    db.commit()
    return document_index
