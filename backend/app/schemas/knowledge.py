from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.knowledge import KnowledgeCategory

class KnowledgeDocumentCreate(BaseModel):
    title: str
    category: KnowledgeCategory = KnowledgeCategory.FAQ
    question: Optional[str] = None
    answer_or_content: str
    keywords: Optional[str] = None
    is_active: Optional[bool] = True

class KnowledgeDocumentResponse(BaseModel):
    id: str
    knowledge_base_id: str
    title: str
    category: KnowledgeCategory
    question: Optional[str] = None
    answer_or_content: str
    keywords: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    documents: List[KnowledgeDocumentResponse] = []

    class Config:
        from_attributes = True

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    matched: bool
    confidence: float
    answer: str
    source_documents: List[str] = []
