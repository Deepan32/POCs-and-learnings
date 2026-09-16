from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class TagResponse(BaseModel):
    id: str
    name: str
    color: str

    class Config:
        from_attributes = True

class TagCreate(BaseModel):
    name: str
    color: Optional[str] = "#3B82F6"

class ContactCreate(BaseModel):
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = []

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

class ContactResponse(BaseModel):
    id: str
    workspace_id: str
    whatsapp_id: str
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    conversation_count: int
    last_active_at: Optional[datetime] = None
    created_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True
