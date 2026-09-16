from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.workspace import RoleEnum

class WorkspaceCreate(BaseModel):
    name: str
    industry: Optional[str] = "Technology"
    timezone: Optional[str] = "Asia/Kolkata"
    country: Optional[str] = "IN"

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    business_hours_config: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    industry: Optional[str] = None
    timezone: str
    country: str
    is_active: bool
    business_hours_config: Optional[str] = None
    created_at: datetime
    role: Optional[RoleEnum] = None

    class Config:
        from_attributes = True

class OnboardingStepPayload(BaseModel):
    step: int
    business_name: Optional[str] = None
    industry: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    phone_number_id: Optional[str] = None
    waba_id: Optional[str] = None
    business_id: Optional[str] = None
    access_token: Optional[str] = None
    first_automation_greeting: Optional[str] = None
    first_template_name: Optional[str] = None
