from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from backend.schemas.upload import UploadResponse
from backend.services.pdf_upload.upload_service import handle_pdf_uploads

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one PDF file is required.")
    return await handle_pdf_uploads(files)
