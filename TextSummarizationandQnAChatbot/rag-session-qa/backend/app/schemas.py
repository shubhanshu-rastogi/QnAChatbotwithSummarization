from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    message: str
    num_chunks: int


class AskRequest(BaseModel):
    session_id: str
    question: str


class Citation(BaseModel):
    id: str
    chunk_id: str | None = None
    snippet: str
    metadata: dict[str, Any] | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieval_context: list[str]


class SummaryRequest(BaseModel):
    session_id: str


class SummaryResponse(BaseModel):
    summary: str
    citations: list[Citation]
