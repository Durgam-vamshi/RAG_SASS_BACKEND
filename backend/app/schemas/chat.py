# from pydantic import BaseModel
# from typing import List

# class QueryRequest(BaseModel):
#     question: str

# class Citation(BaseModel):
#     document: str
#     page: int
#     chunk: str

# class QueryResponse(BaseModel):
#     answer: str
#     citations: List[Citation]







from pydantic import BaseModel
from typing import List


class QueryRequest(BaseModel):
    session_id: str
    question: str


class Citation(BaseModel):
    document: str
    page: int
    chunk: str


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
