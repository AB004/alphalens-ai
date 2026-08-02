from pydantic import BaseModel
from typing import List, Any
from pydantic import model_validator

class TableData(BaseModel):
    lines: List[str]
    rows: List[List[str]]

class ProcessResult(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    storage_path: str
    size_bytes: int
    page_count: int
    parsed_text: str
    clean_text: str
    tables: List[TableData]

class ProcessResponse(BaseModel):
    processed: List[ProcessResult]

class ProcessRequest(BaseModel):
    document_ids: List[int] = []
    filenames: List[str] = []

    @model_validator(mode="after")
    def has_document_reference(self):
        if not self.document_ids and not self.filenames:
            raise ValueError("At least one document ID or filename is required.")
        return self
