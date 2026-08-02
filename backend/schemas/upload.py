from pydantic import BaseModel
from typing import List

class UploadResult(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    storage_path: str
    size_bytes: int
    page_count: int
    upload_timestamp: str

class UploadResponse(BaseModel):
    uploads: List[UploadResult]


class DocumentListItem(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    size_bytes: int
    page_count: int | None
    status: str
    upload_timestamp: str
    processed_timestamp: str | None


class DocumentListResponse(BaseModel):
    documents: List[DocumentListItem]
