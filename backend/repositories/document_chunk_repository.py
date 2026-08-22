
from typing import Optional

from sqlalchemy.orm import Session

from backend.models import DocumentChunk

def get_chunks_for_document(db: Session, document_id: int) -> list[DocumentChunk]:
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


