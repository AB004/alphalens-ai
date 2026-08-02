from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, status
from typing import List
from sqlalchemy.orm import Session

from backend.schemas.upload import DocumentListResponse, UploadResponse
from backend.services.pdf_upload.upload_service import handle_pdf_uploads
from database.crud import delete_document, get_document, list_documents
from database.session import get_db

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
@router.post("/documents/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one PDF file is required.")
    return await handle_pdf_uploads(files)


def document_list_item(document) -> dict:
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "size_bytes": document.size_bytes,
        "page_count": document.page_count,
        "status": document.status,
        "upload_timestamp": document.upload_timestamp.isoformat(),
        "processed_timestamp": document.processed_timestamp.isoformat() if document.processed_timestamp else None,
    }


@router.get("/documents", response_model=DocumentListResponse)
def get_documents(db: Session = Depends(get_db)):
    return {"documents": [document_list_item(document) for document in list_documents(db)]}


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(document_id: int, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")

    storage_path = Path(document.storage_path)
    delete_document(db, document)
    storage_path.unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
