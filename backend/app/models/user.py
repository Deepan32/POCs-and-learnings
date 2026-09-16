from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    assigned_conversations = relationship("Conversation", back_populates="assigned_agent")
    assigned_leads = relationship("Lead", back_populates="assigned_agent")
