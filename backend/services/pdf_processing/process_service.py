import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import HTTPException, status
from pypdf import PdfReader
from sqlalchemy.exc import SQLAlchemyError
from backend.repositories.document_repository import get_document, get_document_by_stored_filename
from backend.database.session import SessionLocal


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def get_upload_path(filename: str) -> Path:
    safe_name = Path(filename).name
    path = UPLOAD_DIR / safe_name
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Uploaded file not found: {safe_name}")
    return path


def extract_text_from_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n\f\n".join(pages)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to extract text from PDF: {exc}") from exc


def clean_extracted_text(text: str) -> str:
    text = text.replace("\x0c", "\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    cleaned_lines = []
    blank = False
    for line in lines:
        if not line:
            if not blank:
                cleaned_lines.append("")
            blank = True
            continue
        cleaned_lines.append(line)
        blank = False
    return "\n".join(cleaned_lines).strip()


def extract_tables_from_text(text: str) -> List[Dict[str, Any]]:
    """Identify text-layout tables. Structured table extraction is a later enhancement."""
    tables = []
    lines = [line for line in text.splitlines() if line.strip()]
    candidate = []

    def flush_candidate():
        nonlocal candidate
        if len(candidate) >= 2:
            rows = []
            for row_text in candidate:
                row = [cell.strip() for cell in re.split(r"\s{2,}|\|", row_text) if cell.strip()]
                if len(row) >= 2:
                    rows.append(row)
            if rows:
                tables.append({"lines": candidate.copy(), "rows": rows})
        candidate = []

    for line in lines:
        if "|" in line or re.search(r"\s{2,}", line):
            candidate.append(line)
            continue
        flush_candidate()
    flush_candidate()
    return tables


def process_pdf_file(path: Path) -> Dict[str, Any]:
    parsed_text = extract_text_from_pdf(path)
    return {
        "parsed_text": parsed_text,
        "clean_text": clean_extracted_text(parsed_text),
        "tables": extract_tables_from_text(parsed_text),
        "page_count": len(PdfReader(str(path)).pages),
        "size_bytes": os.path.getsize(path),
    }


def _serialize_processed_document(document) -> Dict[str, Any]:
    return {
        "id": document.id,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "storage_path": document.storage_path,
        "size_bytes": document.size_bytes,
        "page_count": document.page_count,
        "parsed_text": document.parsed_text,
        "clean_text": document.clean_text,
        "tables": document.tables or [],
    }


def process_pdf_files(document_ids: List[int] | None = None, filenames: List[str] | None = None) -> Dict[str, Any]:
    document_ids = document_ids or []
    filenames = filenames or []
    results = []
    db = SessionLocal()

    try:
        documents = []
        seen_ids = set()
        for document_id in document_ids:
            document = get_document(db, document_id)
            if not document:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
            if document.id not in seen_ids:
                documents.append(document)
                seen_ids.add(document.id)
        for filename in filenames:
            document = get_document_by_stored_filename(db, Path(filename).name)
            if not document:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Uploaded document not found: {Path(filename).name}")
            if document.id not in seen_ids:
                documents.append(document)
                seen_ids.add(document.id)

        for document in documents:
            path = get_upload_path(document.stored_filename)
            processed = process_pdf_file(path)
            document.parsed_text = processed["parsed_text"]
            document.clean_text = processed["clean_text"]
            document.tables = processed["tables"]
            document.page_count = processed["page_count"]
            document.size_bytes = processed["size_bytes"]
            document.status = "processed"
            document.processed_timestamp = datetime.utcnow()
            results.append(document)
        db.commit()
        for document in results:
            db.refresh(document)
        return {"processed": [_serialize_processed_document(document) for document in results]}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save processed document.") from exc
    finally:
        db.close()
