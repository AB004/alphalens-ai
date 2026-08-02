import os
import re
from typing import List, Dict, Any
from fastapi import HTTPException, status
from pypdf import PdfReader

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def get_upload_path(filename: str) -> str:
    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Uploaded file not found: {safe_name}")
    return path


def extract_text_from_pdf(path: str) -> str:
    try:
        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n\f\n".join(pages)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to extract text from PDF: {exc}")


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


def process_pdf_file(path: str) -> Dict[str, Any]:
    parsed_text = extract_text_from_pdf(path)
    clean_text = clean_extracted_text(parsed_text)
    tables = extract_tables_from_text(parsed_text)
    return {
        "parsed_text": parsed_text,
        "clean_text": clean_text,
        "tables": tables,
        "page_count": len(PdfReader(path).pages),
        "size_bytes": os.path.getsize(path),
        "storage_path": path,
        "stored_filename": os.path.basename(path),
    }


def process_pdf_files(filenames: List[str]) -> Dict[str, Any]:
    results = []
    for filename in filenames:
        path = get_upload_path(filename)
        result = process_pdf_file(path)
        result["original_filename"] = filename
        results.append(result)
    return {"processed": results}
