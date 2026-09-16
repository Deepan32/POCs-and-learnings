from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class QuickReply(BaseModel):
    __tablename__ = "quick_replies"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    shortcut = Column(String(50), nullable=False, index=True)  # e.g., "/catalog", "/timing", "/price"
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="General", nullable=False)

    workspace = relationship("Workspace", back_populates="quick_replies")
