from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.core.security import get_password_hash
from backend.app.models.workspace import Workspace, WorkspaceMember, RoleEnum
from backend.app.models.user import User
from backend.app.schemas.team import TeamMemberInvite, TeamMemberUpdate, TeamMemberResponse
from backend.app.schemas.auth import UserResponse

router = APIRouter()

@router.get("", response_model=List[TeamMemberResponse])
async def list_team_members(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(WorkspaceMember)
        .options(selectinload(WorkspaceMember.user))
        .where(WorkspaceMember.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    members = res.scalars().all()
    output = []
    for m in members:
        tm = TeamMemberResponse(
            id=m.id,
            workspace_id=m.workspace_id,
            user_id=m.user_id,
            role=m.role,
            is_active=m.is_active,
            created_at=m.created_at,
            user=UserResponse.model_validate(m.user)
        )
        output.append(tm)
    return output

@router.post("/invite", response_model=TeamMemberResponse)
async def invite_team_member(
    payload: TeamMemberInvite,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    u_stmt = select(User).where(User.email == payload.email.lower())
    u_res = await db.execute(u_stmt)
    user = u_res.scalars().first()

    if not user:
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=get_password_hash("Allstreak@2026"),
            is_active=True
        )
        db.add(user)
        await db.flush()

    # Check if already in workspace
    m_stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace.id,
        WorkspaceMember.user_id == user.id
    )
    m_res = await db.execute(m_stmt)
    if m_res.scalars().first():
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=payload.role,
        is_active=True
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    return TeamMemberResponse(
        id=member.id,
        workspace_id=member.workspace_id,
        user_id=member.user_id,
        role=member.role,
        is_active=member.is_active,
        created_at=member.created_at,
        user=UserResponse.model_validate(user)
    )

@router.delete("/{id}")
async def remove_team_member(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkspaceMember).where(WorkspaceMember.id == id, WorkspaceMember.workspace_id == workspace.id)
    res = await db.execute(stmt)
    member = res.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == RoleEnum.OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove workspace owner")
    await db.delete(member)
    await db.commit()
    return {"status": "success", "message": "Team member removed"}
