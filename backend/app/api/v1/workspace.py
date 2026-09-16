import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_workspace, RoleChecker
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceMember, RoleEnum
from backend.app.models.whatsapp import WhatsAppAccount
from backend.app.models.automation import AutomationRule
from backend.app.models.template import MessageTemplate, TemplateCategory, TemplateStatus, TemplateHeaderType
from backend.app.schemas.workspace import (
    WorkspaceResponse, WorkspaceUpdate, OnboardingStepPayload
)

router = APIRouter()

@router.get("", response_model=WorkspaceResponse)
async def get_workspace(
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace.id,
        WorkspaceMember.user_id == user.id
    )
    res = await db.execute(stmt)
    member = res.scalars().first()
    
    resp = WorkspaceResponse.model_validate(workspace)
    resp.role = member.role if member else RoleEnum.AGENT
    return resp

@router.put("", response_model=WorkspaceResponse)
async def update_workspace(
    payload: WorkspaceUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    if payload.name:
        workspace.name = payload.name
    if payload.industry:
        workspace.industry = payload.industry
    if payload.timezone:
        workspace.timezone = payload.timezone
    if payload.country:
        workspace.country = payload.country
    if payload.business_hours_config is not None:
        workspace.business_hours_config = payload.business_hours_config

    await db.commit()
    await db.refresh(workspace)
    return WorkspaceResponse.model_validate(workspace)

@router.post("/onboarding")
async def process_onboarding(
    payload: OnboardingStepPayload,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Handles the multi-step onboarding wizard for ALLSTREAK."""
    step = payload.step

    if step == 2:  # Workspace Details
        if payload.business_name:
            workspace.name = payload.business_name
        if payload.industry:
            workspace.industry = payload.industry
        if payload.timezone:
            workspace.timezone = payload.timezone
        if payload.country:
            workspace.country = payload.country

    elif step == 3 or step == 4:  # Connect WhatsApp
        if payload.phone_number_id and payload.access_token:
            stmt = select(WhatsAppAccount).where(WhatsAppAccount.workspace_id == workspace.id)
            res = await db.execute(stmt)
            account = res.scalars().first()
            if not account:
                account = WhatsAppAccount(
                    workspace_id=workspace.id,
                    phone_number_id=payload.phone_number_id,
                    waba_id=payload.waba_id or "waba_default",
                    business_id=payload.business_id,
                    access_token=payload.access_token,
                    webhook_verify_token="allstreak_secure_verify_token_2026",
                    display_phone_number="+1 555-0199",
                    verified_name=workspace.name
                )
                db.add(account)
            else:
                account.phone_number_id = payload.phone_number_id
                account.access_token = payload.access_token
                account.waba_id = payload.waba_id or account.waba_id

    elif step == 5:  # Create first automation
        greeting = payload.first_automation_greeting or "Hello! 👋 Welcome to our business. How can we help you?"
        # Check if default rule exists
        r_stmt = select(AutomationRule).where(
            AutomationRule.workspace_id == workspace.id,
            AutomationRule.name == "First Greeting"
        )
        r_res = await db.execute(r_stmt)
        if not r_res.scalars().first():
            rule = AutomationRule(
                workspace_id=workspace.id,
                name="First Greeting",
                trigger_keyword="hi",
                match_type="contains",
                action_reply_text=greeting,
                action_buttons_json=json.dumps(["Sales", "Support", "Pricing", "Talk to Human"]),
                action_create_lead=True,
                action_add_tag="New Lead",
                priority=10
            )
            db.add(rule)

    elif step == 6:  # Create first template
        tpl_name = payload.first_template_name or "welcome_notice"
        t_stmt = select(MessageTemplate).where(
            MessageTemplate.workspace_id == workspace.id,
            MessageTemplate.name == tpl_name
        )
        t_res = await db.execute(t_stmt)
        if not t_res.scalars().first():
            tpl = MessageTemplate(
                workspace_id=workspace.id,
                name=tpl_name,
                category=TemplateCategory.UTILITY,
                language="en_US",
                status=TemplateStatus.APPROVED,
                header_type=TemplateHeaderType.NONE,
                body_text="Hello {{1}}, thank you for reaching out to us! Our specialist is reviewing your inquiry.",
                footer_text="Reply STOP to unsubscribe"
            )
            db.add(tpl)

    await db.commit()
    return {"status": "success", "step": step, "message": f"Step {step} configured successfully"}
