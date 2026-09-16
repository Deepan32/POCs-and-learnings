from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BusinessProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    description: Optional[str] = None
    business_hours_config: Optional[str] = None

class BrandingUpdate(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    button_style: Optional[str] = None

class ClientSetupOverview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_id: str
    name: str
    slug: str
    industry: Optional[str] = None
    timezone: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    description: Optional[str] = None
    business_hours_config: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#25D366"
    secondary_color: Optional[str] = "#128C7E"
    background_color: Optional[str] = "#0B141A"
    text_color: Optional[str] = "#E9EDEF"
    button_style: Optional[str] = "rounded"

    # Meta Integration Status
    whatsapp_connected: bool = False
    whatsapp_phone_number: Optional[str] = None
    whatsapp_quality_rating: Optional[str] = None

    # Counts
    products_count: int = 0
    quick_replies_count: int = 0
    flows_count: int = 0
    templates_count: int = 0
    leads_count: int = 0

class ProductServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "General"
    price: Optional[float] = 0.0
    currency: Optional[str] = "INR"
    image_url: Optional[str] = None
    sku: Optional[str] = None
    is_available: Optional[bool] = True
    tags: Optional[str] = None
    order_index: Optional[int] = 0

class ProductServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    is_available: Optional[bool] = None
    tags: Optional[str] = None
    order_index: Optional[int] = None

class ProductServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = "General"
    price: Optional[float] = 0.0
    currency: str = "INR"
    image_url: Optional[str] = None
    sku: Optional[str] = None
    is_available: bool = True
    tags: Optional[str] = None
    order_index: int = 0
    created_at: datetime

class QuickReplyCreate(BaseModel):
    shortcut: str
    title: str
    message: str
    category: Optional[str] = "General"

class QuickReplyUpdate(BaseModel):
    shortcut: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    category: Optional[str] = None

class QuickReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shortcut: str
    title: str
    message: str
    category: str
    created_at: datetime

class ClientCloneRequest(BaseModel):
    target_name: str
    target_slug: Optional[str] = None
    industry: Optional[str] = None
    copy_branding: bool = True
    copy_flows: bool = True
    copy_templates: bool = True
    copy_products: bool = True
    copy_quick_replies: bool = True
    copy_ai_settings: bool = True

class ClientCloneResponse(BaseModel):
    new_workspace_id: str
    new_workspace_name: str
    new_workspace_slug: str
    copied_items: Dict[str, int]
    message: str

class ConfigVersionCreate(BaseModel):
    version_tag: str
    notes: Optional[str] = None

class ConfigVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    version_tag: str
    snapshot_json: str
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

class AISuggestRequest(BaseModel):
    conversation_id: str
    context_hint: Optional[str] = None

class AISuggestionItem(BaseModel):
    id: str
    type: str  # "direct_answer", "lead_qualify", "catalog_send", "schedule_visit"
    label: str
    text: str

class AISuggestResponse(BaseModel):
    conversation_id: str
    suggestions: List[AISuggestionItem]

class IndustryTemplateItem(BaseModel):
    id: str
    name: str
    category: str
    icon: str
    description: str
    greeting_message: str
    products: List[Dict[str, Any]]
    quick_replies: List[Dict[str, Any]]
    lead_stages: List[str]
    sample_flows: List[Dict[str, Any]]
