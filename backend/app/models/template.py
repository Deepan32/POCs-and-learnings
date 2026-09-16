import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class TemplateCategory(str, enum.Enum):
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"
    AUTHENTICATION = "AUTHENTICATION"

class TemplateStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAUSED = "PAUSED"

class TemplateHeaderType(str, enum.Enum):
    NONE = "NONE"
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"

class MessageTemplate(BaseModel):
    __tablename__ = "message_templates"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    meta_template_id = Column(String(100), nullable=True, index=True)  # WhatsApp/Meta internal template ID
    name = Column(String(100), nullable=False)
    category = Column(Enum(TemplateCategory), default=TemplateCategory.UTILITY, nullable=False)
    language = Column(String(20), default="en_US", nullable=False)
    status = Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT, nullable=False, index=True)
    rejection_reason = Column(Text, nullable=True)

    header_type = Column(Enum(TemplateHeaderType), default=TemplateHeaderType.NONE, nullable=False)
    header_content = Column(Text, nullable=True)
    body_text = Column(Text, nullable=False)
    footer_text = Column(String(255), nullable=True)
    buttons_json = Column(Text, nullable=True)  # Stored JSON array of buttons (QUICK_REPLY, URL, PHONE_NUMBER)

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", "language", name="uq_workspace_template_lang"),
    )

    workspace = relationship("Workspace", back_populates="templates")
    variables = relationship("TemplateVariable", back_populates="template", cascade="all, delete-orphan", order_by="TemplateVariable.variable_index")

class TemplateVariable(BaseModel):
    __tablename__ = "template_variables"

    template_id = Column(String(36), ForeignKey("message_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    variable_index = Column(Integer, nullable=False)  # 1, 2, 3
    variable_name = Column(String(50), nullable=False)  # e.g., "customer_name"
    mapping_source = Column(String(50), default="contact.name", nullable=False)  # contact.name, lead.company, order.id

    template = relationship("MessageTemplate", back_populates="variables")
