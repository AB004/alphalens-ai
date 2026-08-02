from pydantic import BaseModel
from typing import List, Any

class TableData(BaseModel):
    lines: List[str]
    rows: List[List[str]]

class ProcessResult(BaseModel):
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
    filenames: List[str]
