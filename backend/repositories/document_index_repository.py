
from typing import Optional

from sqlalchemy.orm import Session


from backend.models import Document, DocumentChunk, DocumentIndex



def get_document_index(db: Session, document_id: int) -> Optional[DocumentIndex]:
    return db.query(DocumentIndex).filter(DocumentIndex.document_id == document_id).first()

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
