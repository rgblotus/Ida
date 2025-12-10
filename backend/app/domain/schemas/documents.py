from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    collection_id: int
    collection_name: str
    status: str
    chunk_count: int
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

class UploadResponse(BaseModel):
    message: str
    document_ids: List[int]
    collection_name: str