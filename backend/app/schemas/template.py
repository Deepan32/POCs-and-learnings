from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.template import TemplateCategory, TemplateStatus, TemplateHeaderType

class TemplateVariableSchema(BaseModel):
    variable_index: int
    variable_name: str
    mapping_source: str = "contact.name"

class TemplateCreate(BaseModel):
    name: str
    category: TemplateCategory = TemplateCategory.UTILITY
    language: str = "en_US"
    header_type: TemplateHeaderType = TemplateHeaderType.NONE
    header_content: Optional[str] = None
    body_text: str
    footer_text: Optional[str] = None
    buttons_json: Optional[str] = None
    variables: Optional[List[TemplateVariableSchema]] = []

class TemplateUpdate(BaseModel):
    category: Optional[TemplateCategory] = None
    header_type: Optional[TemplateHeaderType] = None
    header_content: Optional[str] = None
    body_text: Optional[str] = None
    footer_text: Optional[str] = None
    buttons_json: Optional[str] = None

from pydantic import BaseModel, ConfigDict

class TemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    meta_template_id: Optional[str] = None
    name: str
    category: TemplateCategory
    language: str
    status: TemplateStatus
    rejection_reason: Optional[str] = None
    header_type: TemplateHeaderType
    header_content: Optional[str] = None
    body_text: str
    footer_text: Optional[str] = None
    buttons_json: Optional[str] = None
    estimated_cost_inr: float = 0.35
    estimated_cost_usd: float = 0.0042
    cost_badge: str = "₹0.35 / msg"
    created_at: datetime
    variables: List[TemplateVariableSchema] = []

class TemplateSyncResponse(BaseModel):
    synced_count: int
    templates: List[TemplateResponse]

