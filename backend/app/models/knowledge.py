import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class KnowledgeCategory(str, enum.Enum):
    FAQ = "FAQ"
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"
    PRICING = "PRICING"
    HOURS = "HOURS"
    POLICY = "POLICY"
    GENERAL = "GENERAL"

class KnowledgeBase(BaseModel):
    __tablename__ = "knowledge_bases"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    workspace = relationship("Workspace", back_populates="knowledge_bases")
    documents = relationship("KnowledgeDocument", back_populates="knowledge_base", cascade="all, delete-orphan")

class KnowledgeDocument(BaseModel):
    __tablename__ = "knowledge_documents"

    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(Enum(KnowledgeCategory), default=KnowledgeCategory.FAQ, nullable=False)
    question = Column(Text, nullable=True)  # If FAQ format
    answer_or_content = Column(Text, nullable=False)
    keywords = Column(String(255), nullable=True)  # Comma-separated search tokens
    is_active = Column(Boolean, default=True, nullable=False)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
