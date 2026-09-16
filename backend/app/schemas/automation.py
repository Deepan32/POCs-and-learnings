from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.automation import FlowStatus, TriggerType, ExecutionStatus

class AutomationFlowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: Optional[int] = 10
    trigger_type: TriggerType = TriggerType.KEYWORD
    trigger_config: Optional[str] = None
    nodes_json: Optional[str] = None
    edges_json: Optional[str] = None
    is_active: Optional[bool] = True

class AutomationFlowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    trigger_type: Optional[TriggerType] = None
    trigger_config: Optional[str] = None
    nodes_json: Optional[str] = None
    edges_json: Optional[str] = None
    status: Optional[FlowStatus] = None

class AutomationExecutionResponse(BaseModel):
    id: str
    flow_id: str
    conversation_id: Optional[str] = None
    contact_id: Optional[str] = None
    status: ExecutionStatus
    input_text: Optional[str] = None
    logs_json: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True

class AutomationFlowResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    priority: int
    version: int
    status: FlowStatus
    trigger_type: TriggerType
    trigger_config: Optional[str] = None
    nodes_json: Optional[str] = None
    edges_json: Optional[str] = None
    triggered_count: int
    completed_count: int
    failed_count: int
    leads_generated_count: int
    handovers_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class FlowSimulationRequest(BaseModel):
    message_text: str
    contact_phone: Optional[str] = "+919876543210"
    contact_name: Optional[str] = "Simulation Tester"

class FlowSimulationResult(BaseModel):
    matched: bool
    flow_name: Optional[str] = None
    execution_steps: List[str] = []
    response_preview: Optional[str] = None
    buttons_preview: Optional[List[str]] = None
    created_lead: bool = False
    triggered_handover: bool = False

# Simplified No-Code Rule Builder
class AutomationRuleCreate(BaseModel):
    name: str
    priority: Optional[int] = 10
    trigger_keyword: str
    match_type: Optional[str] = "contains"
    condition_contact_is_new: Optional[bool] = False
    action_reply_text: str
    action_buttons_json: Optional[str] = None
    action_create_lead: Optional[bool] = False
    action_add_tag: Optional[str] = None
    action_handover: Optional[bool] = False
    is_active: Optional[bool] = True

class AutomationRuleResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    priority: int
    trigger_keyword: str
    match_type: str
    condition_contact_is_new: bool
    action_reply_text: str
    action_buttons_json: Optional[str] = None
    action_create_lead: bool
    action_add_tag: Optional[str] = None
    action_handover: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
