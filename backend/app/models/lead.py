import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Integer, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CONVERTED = "CONVERTED"
    LOST = "LOST"

class Lead(BaseModel):
    __tablename__ = "leads"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_agent_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    company = Column(String(100), nullable=True)
    source = Column(String(50), default="WHATSAPP", nullable=False)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    value = Column(Float, default=0.0, nullable=False)
    score = Column(Integer, default=10, nullable=False)  # 0 to 100
    notes = Column(Text, nullable=True)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    assigned_agent = relationship("User", back_populates="assigned_leads")
    stage_history = relationship("LeadStageHistory", back_populates="lead", cascade="all, delete-orphan", order_by="LeadStageHistory.created_at.desc()")
    tags = relationship("LeadTag", back_populates="lead", cascade="all, delete-orphan")

class LeadStageHistory(BaseModel):
    __tablename__ = "lead_stage_history"

    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    from_stage = Column(Enum(LeadStatus), nullable=True)
    to_stage = Column(Enum(LeadStatus), nullable=False)
    notes = Column(Text, nullable=True)

    lead = relationship("Lead", back_populates="stage_history")
    changed_by = relationship("User")

class LeadTag(BaseModel):
    __tablename__ = "lead_tags"

    lead_id = Column(String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(String(36), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)

    lead = relationship("Lead", back_populates="tags")
    tag = relationship("Tag")

    __table_args__ = (
        UniqueConstraint("lead_id", "tag_id", name="uq_lead_tag"),
    )

class LeadScoringRule(BaseModel):
    __tablename__ = "lead_scoring_rules"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # KEYWORD, BUTTON_CLICK, HUMAN_REQUEST, MESSAGE_COUNT
    keyword_or_pattern = Column(String(100), nullable=True)
    score_delta = Column(Integer, default=10, nullable=False)
    description = Column(String(255), nullable=True)
