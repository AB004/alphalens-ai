import datetime
import os
import uuid
from typing import List
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf"}


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def is_pdf_filename(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


def validate_pdf_file(upload_file: UploadFile):
    if not upload_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a filename.")
    if not is_pdf_filename(upload_file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {upload_file.filename}")
    upload_file.file.seek(0)
    header = upload_file.file.read(10)
    upload_file.file.seek(0)
    if not header.startswith(b"%PDF-"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File is not a valid PDF: {upload_file.filename}")


def save_upload_file(upload_file: UploadFile) -> str:
    unique_name = f"{uuid.uuid4().hex}_{os.path.basename(upload_file.filename)}"
    stored_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(stored_path, "wb") as out_file:
        while True:
            chunk = upload_file.file.read(4096)
            if not chunk:
                break
            out_file.write(chunk)
    return stored_path


def get_pdf_page_count(path: str) -> int:
    try:
        reader = PdfReader(path)
        return len(reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to read PDF pages: {exc}")


async def handle_pdf_uploads(files: List[UploadFile]):
    ensure_upload_dir()
    results = []

    for upload_file in files:
        validate_pdf_file(upload_file)
        upload_file.file.seek(0)
        stored_path = save_upload_file(upload_file)
        size_bytes = os.path.getsize(stored_path)
        page_count = get_pdf_page_count(stored_path)
        results.append(
            {
                "original_filename": upload_file.filename,
                "stored_filename": os.path.basename(stored_path),
                "storage_path": stored_path,
                "size_bytes": size_bytes,
                "page_count": page_count,
                "upload_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )

    return {"uploads": results}
