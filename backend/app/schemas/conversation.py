from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.conversation import ConversationMode, ConversationStatus
from backend.app.schemas.contact import ContactResponse
from backend.app.schemas.auth import UserResponse

class ConversationResponse(BaseModel):
    id: str
    workspace_id: str
    contact_id: str
    assigned_agent_id: Optional[str] = None
    mode: ConversationMode
    status: ConversationStatus
    unread_count: int
    last_message_preview: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_customer_message_at: Optional[datetime] = None
    window_expires_at: Optional[datetime] = None
    is_window_open: bool
    handover_reason: Optional[str] = None
    handover_at: Optional[datetime] = None
    lead_id: Optional[str] = None
    created_at: datetime

    contact: Optional[ContactResponse] = None
    assigned_agent: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    status: Optional[ConversationStatus] = None

class HandoverRequest(BaseModel):
    reason: Optional[str] = "Customer requested human support"
    assigned_agent_id: Optional[str] = None

class ReturnToBotRequest(BaseModel):
    target_mode: ConversationMode = ConversationMode.BOT  # BOT or AI
    reason: Optional[str] = "Agent returned conversation to automated flow"

class AssignAgentRequest(BaseModel):
    agent_id: str
    reason: Optional[str] = "Manual agent assignment"

class StartConversationRequest(BaseModel):
    phone: str
    name: Optional[str] = None
    initial_message: Optional[str] = None
    template_name: Optional[str] = None
    mode: Optional[ConversationMode] = ConversationMode.HUMAN

