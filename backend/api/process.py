from fastapi import APIRouter, HTTPException, status
from backend.schemas.process import ProcessRequest, ProcessResponse
from backend.services.pdf_processing.process_service import process_pdf_files

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
def process_pdfs(request: ProcessRequest):
    return process_pdf_files(document_ids=request.document_ids, filenames=request.filenames)
