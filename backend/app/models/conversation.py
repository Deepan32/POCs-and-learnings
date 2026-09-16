import enum
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class ConversationMode(str, enum.Enum):
    BOT = "BOT"
    AI = "AI"
    HUMAN = "HUMAN"

class ConversationStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    SNOOZED = "SNOOZED"

class Conversation(BaseModel):
    __tablename__ = "conversations"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_agent_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    mode = Column(Enum(ConversationMode), default=ConversationMode.BOT, nullable=False, index=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.OPEN, nullable=False, index=True)
    
    unread_count = Column(Integer, default=0, nullable=False)
    last_message_preview = Column(Text, nullable=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Meta WhatsApp 24-hour customer service window
    last_customer_message_at = Column(DateTime(timezone=True), nullable=True)
    window_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Human Handover tracking
    handover_reason = Column(String(255), nullable=True)
    handover_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    returned_to_bot_at = Column(DateTime(timezone=True), nullable=True)
    
    # Lead linkage
    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="conversations")
    contact = relationship("Contact", back_populates="conversations")
    assigned_agent = relationship("User", back_populates="assigned_conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    lead = relationship("Lead", foreign_keys=[lead_id], post_update=True)
    assignments = relationship("ConversationAssignment", back_populates="conversation", cascade="all, delete-orphan")

    def update_window(self, window_hours: int = 24):
        now = datetime.now(timezone.utc)
        self.last_customer_message_at = now
        self.window_expires_at = now + timedelta(hours=window_hours)

    @property
    def is_window_open(self) -> bool:
        if not self.window_expires_at:
            return False
        # Normalize timezone
        expires = self.window_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < expires

class ConversationAssignment(BaseModel):
    __tablename__ = "conversation_assignments"

    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String(255), nullable=True)

    conversation = relationship("Conversation", back_populates="assignments")
