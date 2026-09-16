from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.ai import AIMode, AITone

class AISettingsUpdate(BaseModel):
    ai_name: Optional[str] = None
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    tone: Optional[AITone] = None
    instructions: Optional[str] = None
    fallback_message: Optional[str] = None
    max_tokens: Optional[int] = None
    mode: Optional[AIMode] = None
    auto_handover_on_fallback: Optional[bool] = None
    confidence_threshold: Optional[float] = None

class AISettingsResponse(BaseModel):
    id: str
    workspace_id: str
    ai_name: str
    business_name: str
    business_description: Optional[str] = None
    tone: AITone
    instructions: str
    fallback_message: str
    max_tokens: int
    mode: AIMode
    auto_handover_on_fallback: bool
    confidence_threshold: float
    created_at: datetime

    class Config:
        from_attributes = True
