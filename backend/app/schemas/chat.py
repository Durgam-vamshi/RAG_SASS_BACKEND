from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    session_id: str
    question: str


class Citation(BaseModel):
    document: str
    page: Optional[int] = None
    chunk: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]