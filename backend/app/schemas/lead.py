from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.lead import LeadStatus
from backend.app.schemas.auth import UserResponse

class ContactSummary(BaseModel):
    id: str
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LeadStageHistoryResponse(BaseModel):
    id: str
    from_stage: Optional[LeadStatus] = None
    to_stage: LeadStatus
    notes: Optional[str] = None
    created_at: datetime
    changed_by: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

class LeadCreate(BaseModel):
    contact_id: Optional[str] = None
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = "WHATSAPP"
    status: Optional[LeadStatus] = LeadStatus.NEW
    value: Optional[float] = 0.0
    score: Optional[int] = 10
    notes: Optional[str] = None
    assigned_agent_id: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    status: Optional[LeadStatus] = None
    value: Optional[float] = None
    score: Optional[int] = None
    notes: Optional[str] = None
    assigned_agent_id: Optional[str] = None

class LeadStageUpdate(BaseModel):
    status: LeadStatus
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    workspace_id: str
    contact_id: str
    assigned_agent_id: Optional[str] = None
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    source: str
    status: LeadStatus
    value: float
    score: int
    notes: Optional[str] = None
    last_contact_at: Optional[datetime] = None
    created_at: datetime

    contact: Optional[ContactSummary] = None
    assigned_agent: Optional[UserResponse] = None
    stage_history: List[LeadStageHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)

class LeadKanbanColumn(BaseModel):
    stage: LeadStatus
    label: str
    count: int
    total_value: float
    leads: List[LeadResponse]

class LeadKanbanResponse(BaseModel):
    columns: List[LeadKanbanColumn]
