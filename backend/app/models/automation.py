import enum
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class FlowStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class TriggerType(str, enum.Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    KEYWORD = "KEYWORD"
    BUTTON_CLICK = "BUTTON_CLICK"
    NEW_CONTACT = "NEW_CONTACT"
    NEW_LEAD = "NEW_LEAD"
    WEBHOOK = "WEBHOOK"
    SCHEDULE = "SCHEDULE"

class ExecutionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class AutomationFlow(BaseModel):
    __tablename__ = "automation_flows"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=10, nullable=False)  # Lower number = higher priority
    version = Column(Integer, default=1, nullable=False)
    status = Column(Enum(FlowStatus), default=FlowStatus.PUBLISHED, nullable=False, index=True)
    
    trigger_type = Column(Enum(TriggerType), default=TriggerType.KEYWORD, nullable=False)
    trigger_config = Column(Text, nullable=True)  # JSON config e.g. {"keywords": ["hi", "hello"], "match_type": "contains"}

    # React Flow canvas state
    nodes_json = Column(Text, nullable=True)
    edges_json = Column(Text, nullable=True)

    # Analytics counters
    triggered_count = Column(Integer, default=0, nullable=False)
    completed_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    leads_generated_count = Column(Integer, default=0, nullable=False)
    handovers_count = Column(Integer, default=0, nullable=False)

    workspace = relationship("Workspace", back_populates="automations")
    executions = relationship("AutomationExecution", back_populates="flow", cascade="all, delete-orphan", order_by="AutomationExecution.created_at.desc()")

class AutomationExecution(BaseModel):
    __tablename__ = "automation_executions"

    flow_id = Column(String(36), ForeignKey("automation_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.RUNNING, nullable=False)
    input_text = Column(Text, nullable=True)
    logs_json = Column(Text, nullable=True)  # Array of executed steps and evaluation results
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, default=0, nullable=False)

    flow = relationship("AutomationFlow", back_populates="executions")

class AutomationRule(BaseModel):
    """Simple no-code rules for users who prefer linear trigger -> conditions -> actions table."""
    __tablename__ = "automation_rules"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=10, nullable=False)

    # Simplified configuration
    trigger_keyword = Column(String(100), nullable=False)  # e.g., "hi"
    match_type = Column(String(20), default="contains", nullable=False)  # contains, exact, starts_with
    condition_contact_is_new = Column(Boolean, default=False, nullable=False)
    
    action_reply_text = Column(Text, nullable=False)
    action_buttons_json = Column(Text, nullable=True)  # Buttons e.g., ["Sales", "Support", "Human"]
    action_create_lead = Column(Boolean, default=False, nullable=False)
    action_add_tag = Column(String(50), nullable=True)
    action_handover = Column(Boolean, default=False, nullable=False)

    workspace = relationship("Workspace", back_populates="rules")
