from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
)
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceMember, RoleEnum
from backend.app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse, RefreshTokenRequest
)

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    stmt = select(User).where(User.email == payload.email.lower())
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Create User
    user = User(
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        is_active=True
    )
    db.add(user)
    await db.flush()

    # Create Initial Workspace
    ws_name = payload.workspace_name or f"{payload.full_name}'s Workspace"
    slug = f"{payload.full_name.lower().replace(' ', '-')[:20]}-{user.id[:6]}"
    workspace = Workspace(
        name=ws_name,
        slug=slug,
        industry=payload.industry or "Technology",
        timezone="Asia/Kolkata",
        country="IN"
    )
    db.add(workspace)
    await db.flush()

    # Add as OWNER
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=RoleEnum.OWNER
    )
    db.add(member)
    await db.commit()
    await db.refresh(user)

    # Issue Tokens
    token_data = {"sub": user.id, "email": user.email, "workspace_id": workspace.id, "role": RoleEnum.OWNER.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
        workspace_id=workspace.id,
        role=RoleEnum.OWNER
    )

@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email.lower(), User.is_active == True)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Find primary workspace
    m_stmt = (
        select(WorkspaceMember)
        .where(WorkspaceMember.user_id == user.id, WorkspaceMember.is_active == True)
    )
    m_res = await db.execute(m_stmt)
    member = m_res.scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any active workspace"
        )

    token_data = {"sub": user.id, "email": user.email, "workspace_id": member.workspace_id, "role": member.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
        workspace_id=member.workspace_id,
        role=member.role
    )

@router.post("/refresh")
async def refresh_token_endpoint(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    decoded = decode_token(payload.refresh_token, is_refresh=True)
    if not decoded:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = decoded.get("sub")
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_data = {
        "sub": user.id,
        "email": user.email,
        "workspace_id": decoded.get("workspace_id"),
        "role": decoded.get("role")
    }
    new_access_token = create_access_token(token_data)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
