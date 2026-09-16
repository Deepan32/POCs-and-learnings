from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class Contact(BaseModel):
    __tablename__ = "contacts"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    whatsapp_id = Column(String(50), nullable=False, index=True)  # phone number e.g. 919876543210
    name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    conversation_count = Column(Integer, default=0, nullable=False)
    last_active_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("workspace_id", "phone", name="uq_workspace_phone"),
    )

    workspace = relationship("Workspace", back_populates="contacts")
    conversations = relationship("Conversation", back_populates="contact", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="contact", cascade="all, delete-orphan")
    tags = relationship("ContactTag", back_populates="contact", cascade="all, delete-orphan")
    custom_fields = relationship("ContactCustomField", back_populates="contact", cascade="all, delete-orphan")

class Tag(BaseModel):
    __tablename__ = "tags"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(20), default="#3B82F6", nullable=False)

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_workspace_tag_name"),
    )

class ContactTag(BaseModel):
    __tablename__ = "contact_tags"

    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(String(36), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    contact = relationship("Contact", back_populates="tags")
    tag = relationship("Tag")

    __table_args__ = (
        UniqueConstraint("contact_id", "tag_id", name="uq_contact_tag"),
    )

class ContactCustomField(BaseModel):
    __tablename__ = "contact_custom_fields"

    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    field_key = Column(String(50), nullable=False)
    field_value = Column(Text, nullable=True)

    contact = relationship("Contact", back_populates="custom_fields")
