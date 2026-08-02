from fastapi import APIRouter, HTTPException, status
from backend.schemas.process import ProcessRequest, ProcessResponse
from backend.services.pdf_processing.process_service import process_pdf_files

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
def process_pdfs(request: ProcessRequest):
    if not request.filenames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one filename is required.")
    return process_pdf_files(request.filenames)
