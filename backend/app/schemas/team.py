from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from backend.app.models.workspace import RoleEnum
from backend.app.schemas.auth import UserResponse

class TeamMemberInvite(BaseModel):
    email: EmailStr
    full_name: str
    role: RoleEnum = RoleEnum.AGENT

class TeamMemberUpdate(BaseModel):
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

class TeamMemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True
