from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.models.workspace import RoleEnum

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    workspace_name: Optional[str] = "My Workspace"
    industry: Optional[str] = "E-Commerce"
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"
    workspace_id: str
    role: RoleEnum

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    workspace_id: Optional[str] = None
    role: Optional[RoleEnum] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

Token.model_rebuild()
