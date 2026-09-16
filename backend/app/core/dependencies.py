from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.database import get_db
from backend.app.core.security import decode_token
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceMember, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception

    return user

async def get_current_workspace(
    user: User = Depends(get_current_user),
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID"),
    db: AsyncSession = Depends(get_db)
) -> Workspace:
    # If workspace header provided, verify membership
    if x_workspace_id:
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == x_workspace_id, WorkspaceMember.user_id == user.id, WorkspaceMember.is_active == True)
        )
        res = await db.execute(stmt)
        member = res.scalar_one_or_none()
        if member:
            w_stmt = select(Workspace).where(Workspace.id == x_workspace_id, Workspace.is_active == True)
            w_res = await db.execute(w_stmt)
            ws = w_res.scalar_one_or_none()
            if ws:
                return ws

    # Fallback to user's first active workspace
    stmt = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user.id, Workspace.is_active == True)
    )
    res = await db.execute(stmt)
    ws = res.scalars().first()
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active workspace found for user")

    return ws

class RoleChecker:
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        user: User = Depends(get_current_user),
        workspace: Workspace = Depends(get_current_workspace),
        db: AsyncSession = Depends(get_db)
    ) -> WorkspaceMember:
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id,
            WorkspaceMember.is_active == True
        )
        res = await db.execute(stmt)
        member = res.scalar_one_or_none()
        if not member or member.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {[r.value for r in self.allowed_roles]}"
            )
        return member
