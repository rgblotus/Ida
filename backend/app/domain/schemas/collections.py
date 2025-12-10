from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    document_count: int
    created_at: datetime
    updated_at: datetime

class CollectionStatsResponse(BaseModel):
    id: int
    name: str
    document_count: int
    total_chunks: int
    milvus_entities: int
    status: str