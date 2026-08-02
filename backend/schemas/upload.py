from pydantic import BaseModel
from typing import List

class UploadResult(BaseModel):
    original_filename: str
    stored_filename: str
    storage_path: str
    size_bytes: int
    page_count: int
    upload_timestamp: str

class UploadResponse(BaseModel):
    uploads: List[UploadResult]
