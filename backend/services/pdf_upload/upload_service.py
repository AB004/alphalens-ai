import os
import uuid
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy.exc import SQLAlchemyError

from database.crud import create_document
from database.session import SessionLocal


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf"}
CHUNK_SIZE = 1024 * 1024


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def is_pdf_filename(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def validate_pdf_file(upload_file: UploadFile) -> None:
    if not upload_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a filename.")
    if not is_pdf_filename(upload_file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {upload_file.filename}")

    upload_file.file.seek(0)
    header = upload_file.file.read(5)
    upload_file.file.seek(0)
    if header != b"%PDF-":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File is not a valid PDF: {upload_file.filename}")


def save_upload_file(upload_file: UploadFile) -> tuple[Path, int]:
    """Save an upload while enforcing the size limit without loading it into memory."""
    original_name = Path(upload_file.filename or "document.pdf").name
    stored_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{original_name}"
    size_bytes = 0

    try:
        with stored_path.open("wb") as out_file:
            while chunk := upload_file.file.read(CHUNK_SIZE):
                size_bytes += len(chunk)
                if size_bytes > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail=f"PDF exceeds the {MAX_FILE_SIZE // (1024 * 1024)} MB upload limit.",
                    )
                out_file.write(chunk)
    except Exception:
        stored_path.unlink(missing_ok=True)
        raise

    return stored_path, size_bytes


def get_pdf_page_count(path: Path) -> int:
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ValueError("encrypted PDFs are not supported")
        return len(reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to read PDF pages: {exc}") from exc


def _serialize_document(document) -> dict:
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "storage_path": document.storage_path,
        "size_bytes": document.size_bytes,
        "page_count": document.page_count,
        "upload_timestamp": document.upload_timestamp.isoformat(),
    }


async def handle_pdf_uploads(files: List[UploadFile]):
    ensure_upload_dir()
    results = []
    db = SessionLocal()

    try:
        for upload_file in files:
            validate_pdf_file(upload_file)
            upload_file.file.seek(0)
            stored_path, size_bytes = save_upload_file(upload_file)
            try:
                page_count = get_pdf_page_count(stored_path)
                document = create_document(
                    db,
                    original_filename=Path(upload_file.filename or "").name,
                    stored_filename=stored_path.name,
                    storage_path=str(stored_path),
                    content_type=upload_file.content_type,
                    size_bytes=size_bytes,
                    page_count=page_count,
                    status="uploaded",
                )
            except Exception:
                stored_path.unlink(missing_ok=True)
                raise
            results.append(_serialize_document(document))
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save document metadata.") from exc
    finally:
        db.close()

    return {"uploads": results}
