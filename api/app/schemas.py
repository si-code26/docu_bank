"""Pydantic schemas: API req/resp contracts"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    year: int
    chunk_count: int

class AskRequest(BaseModel):
    question: str=Field(min_length=3, max_length=1000)
    year: int | None = None
    user_id: str = Field(min_length=1, max_length=64)

class SourceChunk(BaseModel):
    page: int
    year: int
    text: str
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    year: int
    created_at: datetime
    model_config={"from_attributes":True}