from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.message import MessageDirection, MessageOrigin, MessageDeliveryStatus, MessageType

class AttachmentResponse(BaseModel):
    id: str
    file_type: str
    file_name: Optional[str] = None
    file_url: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: Optional[str] = None
    meta_message_id: Optional[str] = None
    direction: MessageDirection
    origin: MessageOrigin
    status: MessageDeliveryStatus
    message_type: MessageType
    body: Optional[str] = None
    buttons_json: Optional[str] = None
    template_name: Optional[str] = None
    is_from_template: bool
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    created_at: datetime
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    message_type: MessageType = MessageType.TEXT
    body: Optional[str] = None
    media_url: Optional[str] = None
    media_filename: Optional[str] = None
    buttons: Optional[List[str]] = None  # Quick reply buttons

class SendTemplateRequest(BaseModel):
    template_name: str
    language_code: str = "en_US"
    variable_values: Optional[Dict[str, str]] = None  # e.g. {"1": "Rahul", "2": "#9823"}
