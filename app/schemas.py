from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    byte_size: int
    created_at: datetime
    chunk_count: int = 0


class DocumentDetail(DocumentSummary):
    character_count: int
    word_count: int
    preview: str


class SearchHit(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    position: int
    score: float = Field(ge=0.0, le=1.0)
    text: str


class SearchResponse(BaseModel):
    query: str
    total_hits: int
    hits: list[SearchHit]


class IntelligenceResponse(BaseModel):
    document_id: int
    summary: str
    keywords: list[str]


class AnalyticsResponse(BaseModel):
    documents: int
    chunks: int
    total_bytes: int
    total_words: int
