import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

class MessageOrigin(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    BOT = "BOT"
    AI = "AI"
    HUMAN = "HUMAN"

class MessageDeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"

class MessageType(str, enum.Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    LOCATION = "LOCATION"
    INTERACTIVE = "INTERACTIVE"
    BUTTON = "BUTTON"
    TEMPLATE = "TEMPLATE"

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Meta idempotency key (must be unique across incoming/outgoing messages)
    meta_message_id = Column(String(128), unique=True, index=True, nullable=True)
    
    direction = Column(Enum(MessageDirection), nullable=False, index=True)
    origin = Column(Enum(MessageOrigin), default=MessageOrigin.CUSTOMER, nullable=False, index=True)
    status = Column(Enum(MessageDeliveryStatus), default=MessageDeliveryStatus.SENT, nullable=False, index=True)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    
    body = Column(Text, nullable=True)
    raw_payload = Column(Text, nullable=True)  # Full JSON payload from webhook or outbound request
    error_message = Column(Text, nullable=True)
    
    # Interactive components (e.g., Quick Reply buttons or List rows stored as JSON)
    buttons_json = Column(Text, nullable=True)
    
    # Template metadata if sent via template
    template_name = Column(String(100), nullable=True)
    template_language = Column(String(10), nullable=True)
    is_from_template = Column(Boolean, default=False, nullable=False)
    
    # Status timestamps
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")

class MessageAttachment(BaseModel):
    __tablename__ = "message_attachments"

    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_url = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    message = relationship("Message", back_populates="attachments")
