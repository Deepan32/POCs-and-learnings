import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class ScheduledStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ScheduledMessage(BaseModel):
    __tablename__ = "scheduled_messages"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True)
    
    recipient_phone = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(Enum(ScheduledStatus), default=ScheduledStatus.SCHEDULED, nullable=False, index=True)
    variables_json = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

class WebhookEvent(BaseModel):
    __tablename__ = "webhook_events"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    meta_message_id = Column(String(128), unique=True, index=True, nullable=True)
    event_type = Column(String(50), nullable=False)  # messages, statuses, errors
    status = Column(String(30), default="PROCESSED", nullable=False)  # RECEIVED, PROCESSED, DUPLICATE, FAILED
    processing_time_ms = Column(Integer, default=0, nullable=False)
    raw_payload = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)

class Notification(BaseModel):
    __tablename__ = "notifications"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO", nullable=False)  # NEW_MESSAGE, NEW_LEAD, HANDOVER, ERROR
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    link = Column(String(255), nullable=True)

class AnalyticsEvent(BaseModel):
    __tablename__ = "analytics_events"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    event_name = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), default="GENERAL", nullable=False)
    event_value = Column(Integer, default=1, nullable=False)
    metadata_json = Column(Text, nullable=True)

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details_json = Column(Text, nullable=True)

    user = relationship("User")
