import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Integer, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class AIMode(str, enum.Enum):
    OFF = "OFF"
    SUGGEST = "SUGGEST"
    AUTO = "AUTO"

class AITone(str, enum.Enum):
    PROFESSIONAL = "PROFESSIONAL"
    FRIENDLY = "FRIENDLY"
    CASUAL = "CASUAL"
    FORMAL = "FORMAL"

class AISetting(BaseModel):
    __tablename__ = "ai_settings"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    ai_name = Column(String(100), default="Streak AI", nullable=False)
    business_name = Column(String(100), default="My Business", nullable=False)
    business_description = Column(Text, nullable=True)
    tone = Column(Enum(AITone), default=AITone.PROFESSIONAL, nullable=False)
    instructions = Column(Text, default="You are an intelligent, helpful WhatsApp assistant for this business. Be concise, friendly, and accurate. If you do not know the answer or the customer requests human help, transfer to a human specialist.", nullable=False)
    fallback_message = Column(Text, default="I'm not completely certain about that detail. Let me immediately connect you with our human specialist! 👋", nullable=False)
    max_tokens = Column(Integer, default=250, nullable=False)
    mode = Column(Enum(AIMode), default=AIMode.AUTO, nullable=False)
    auto_handover_on_fallback = Column(Boolean, default=True, nullable=False)
    confidence_threshold = Column(Float, default=0.7, nullable=False)

    workspace = relationship("Workspace", back_populates="ai_settings")
