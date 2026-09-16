import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class RoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class Workspace(BaseModel):
    __tablename__ = "workspaces"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    industry = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    country = Column(String(10), default="IN", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Business hours configuration JSON string
    business_hours_config = Column(Text, nullable=True)

    # Business Profile & Contact Info
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    instagram = Column(String(100), nullable=True)
    facebook = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Branding & Custom Styling
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(20), default="#25D366", nullable=True)
    secondary_color = Column(String(20), default="#128C7E", nullable=True)
    background_color = Column(String(20), default="#0B141A", nullable=True)
    text_color = Column(String(20), default="#E9EDEF", nullable=True)
    button_style = Column(String(50), default="rounded", nullable=True)
    
    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    whatsapp_accounts = relationship("WhatsAppAccount", back_populates="workspace", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="workspace", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="workspace", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="workspace", cascade="all, delete-orphan")
    templates = relationship("MessageTemplate", back_populates="workspace", cascade="all, delete-orphan")
    automations = relationship("AutomationFlow", back_populates="workspace", cascade="all, delete-orphan")
    rules = relationship("AutomationRule", back_populates="workspace", cascade="all, delete-orphan")
    knowledge_bases = relationship("KnowledgeBase", back_populates="workspace", cascade="all, delete-orphan")
    ai_settings = relationship("AISetting", back_populates="workspace", uselist=False, cascade="all, delete-orphan")
    products = relationship("ProductService", back_populates="workspace", cascade="all, delete-orphan")
    quick_replies = relationship("QuickReply", back_populates="workspace", cascade="all, delete-orphan")
    configuration_versions = relationship("ConfigurationVersion", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(BaseModel):
    __tablename__ = "workspace_members"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.AGENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")
