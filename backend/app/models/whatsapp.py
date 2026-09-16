from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class WhatsAppAccount(BaseModel):
    __tablename__ = "whatsapp_accounts"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_number_id = Column(String(100), unique=True, index=True, nullable=False)
    waba_id = Column(String(100), nullable=False)  # WhatsApp Business Account ID
    business_id = Column(String(100), nullable=True)
    display_phone_number = Column(String(50), nullable=True)
    verified_name = Column(String(100), nullable=True)
    access_token = Column(Text, nullable=False)
    webhook_verify_token = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    quality_rating = Column(String(20), default="GREEN", nullable=False)  # GREEN, YELLOW, RED, UNKNOWN
    
    workspace = relationship("Workspace", back_populates="whatsapp_accounts")
