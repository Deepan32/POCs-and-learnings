from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.ai import AISetting, AIMode, AITone
from backend.app.schemas.ai import AISettingsUpdate, AISettingsResponse

router = APIRouter()

@router.get("/settings", response_model=AISettingsResponse)
async def get_ai_settings(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AISetting).where(AISetting.workspace_id == workspace.id)
    res = await db.execute(stmt)
    setting = res.scalars().first()
    if not setting:
        setting = AISetting(
            workspace_id=workspace.id,
            ai_name="Streak AI",
            business_name=workspace.name,
            business_description=f"{workspace.name} automated customer assistant.",
            tone=AITone.PROFESSIONAL,
            mode=AIMode.AUTO
        )
        db.add(setting)
        await db.commit()
        await db.refresh(setting)

    return AISettingsResponse.model_validate(setting)

@router.put("/settings", response_model=AISettingsResponse)
async def update_ai_settings(
    payload: AISettingsUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AISetting).where(AISetting.workspace_id == workspace.id)
    res = await db.execute(stmt)
    setting = res.scalars().first()
    if not setting:
        setting = AISetting(workspace_id=workspace.id)
        db.add(setting)

    if payload.ai_name is not None:
        setting.ai_name = payload.ai_name
    if payload.business_name is not None:
        setting.business_name = payload.business_name
    if payload.business_description is not None:
        setting.business_description = payload.business_description
    if payload.tone is not None:
        setting.tone = payload.tone
    if payload.instructions is not None:
        setting.instructions = payload.instructions
    if payload.fallback_message is not None:
        setting.fallback_message = payload.fallback_message
    if payload.max_tokens is not None:
        setting.max_tokens = payload.max_tokens
    if payload.mode is not None:
        setting.mode = payload.mode
    if payload.auto_handover_on_fallback is not None:
        setting.auto_handover_on_fallback = payload.auto_handover_on_fallback
    if payload.confidence_threshold is not None:
        setting.confidence_threshold = payload.confidence_threshold

    await db.commit()
    await db.refresh(setting)
    return AISettingsResponse.model_validate(setting)
