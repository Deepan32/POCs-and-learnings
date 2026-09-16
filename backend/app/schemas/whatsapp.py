from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class WhatsAppConnectRequest(BaseModel):
    phone_number_id: str
    waba_id: str
    business_id: Optional[str] = None
    access_token: str
    webhook_verify_token: Optional[str] = "allstreak_secure_verify_token_2026"
    display_phone_number: Optional[str] = None
    verified_name: Optional[str] = None

class WhatsAppAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    phone_number_id: str
    waba_id: str
    business_id: Optional[str] = None
    display_phone_number: Optional[str] = None
    verified_name: Optional[str] = None
    is_active: bool
    quality_rating: str
    webhook_verify_token: str
    saved_to_env: bool = True
    created_at: datetime

class WhatsAppTestResponse(BaseModel):
    success: bool
    phone_number_id: str
    verified_name: Optional[str] = None
    quality_rating: Optional[str] = None
    message: str

class WhatsAppSendTestRequest(BaseModel):
    to_phone: str
    message: Optional[str] = "Hello from ALLSTREAK! Your Meta WhatsApp Cloud API connection is active and verified. 🎉"

class WhatsAppWebhookInfoResponse(BaseModel):
    is_connected: bool
    phone_number_id: Optional[str] = None
    waba_id: Optional[str] = None
    display_phone_number: Optional[str] = None
    verified_name: Optional[str] = None
    quality_rating: Optional[str] = None
    webhook_verify_token: str
    callback_url: str
    saved_to_env: bool = True
    meta_dashboard_url: str = "https://developers.facebook.com/apps"


