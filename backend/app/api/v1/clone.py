import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_workspace, RoleChecker
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, WorkspaceMember, RoleEnum
from backend.app.models.product import ProductService
from backend.app.models.quick_reply import QuickReply
from backend.app.models.automation import AutomationFlow, AutomationRule
from backend.app.models.template import MessageTemplate, TemplateVariable
from backend.app.models.ai import AISetting
from backend.app.schemas.client_setup import ClientCloneRequest, ClientCloneResponse

router = APIRouter()

def generate_slug(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    slug = re.sub(r'[\s_-]+', '-', cleaned)
    return slug[:40]

@router.post("/clone", response_model=ClientCloneResponse)
async def clone_client_workspace(
    payload: ClientCloneRequest,
    user: User = Depends(get_current_user),
    src_workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Client Clone Engine:
    Clones workspace structure, branding, flows, templates, products, and quick replies.
    STRICTLY EXCLUDES WhatsApp credentials, access tokens, customer contacts, and chat history.
    """
    base_slug = payload.target_slug or generate_slug(payload.target_name)
    slug = base_slug
    # Ensure unique slug
    suffix = 1
    while True:
        existing = (await db.execute(select(Workspace).where(Workspace.slug == slug))).scalars().first()
        if not existing:
            break
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    # 1. Create new workspace
    new_ws = Workspace(
        name=payload.target_name,
        slug=slug,
        industry=payload.industry or src_workspace.industry,
        timezone=src_workspace.timezone,
        country=src_workspace.country,
        business_hours_config=src_workspace.business_hours_config,
        is_active=True
    )

    # 2. Copy branding & profile if requested
    if payload.copy_branding:
        new_ws.logo_url = src_workspace.logo_url
        new_ws.primary_color = src_workspace.primary_color
        new_ws.secondary_color = src_workspace.secondary_color
        new_ws.background_color = src_workspace.background_color
        new_ws.text_color = src_workspace.text_color
        new_ws.button_style = src_workspace.button_style

    db.add(new_ws)
    await db.flush()  # gets new_ws.id

    # 3. Add current user as OWNER
    member = WorkspaceMember(
        workspace_id=new_ws.id,
        user_id=user.id,
        role=RoleEnum.OWNER,
        is_active=True
    )
    db.add(member)

    copied_counts = {
        "products": 0,
        "quick_replies": 0,
        "flows": 0,
        "templates": 0,
        "rules": 0
    }

    # 4. Copy Products / Services
    if payload.copy_products:
        p_res = await db.execute(select(ProductService).where(ProductService.workspace_id == src_workspace.id))
        for p in p_res.scalars().all():
            new_p = ProductService(
                workspace_id=new_ws.id,
                name=p.name,
                description=p.description,
                category=p.category,
                price=p.price,
                currency=p.currency,
                image_url=p.image_url,
                sku=p.sku,
                is_available=p.is_available,
                tags=p.tags,
                order_index=p.order_index
            )
            db.add(new_p)
            copied_counts["products"] += 1

    # 5. Copy Quick Replies
    if payload.copy_quick_replies:
        qr_res = await db.execute(select(QuickReply).where(QuickReply.workspace_id == src_workspace.id))
        for qr in qr_res.scalars().all():
            new_qr = QuickReply(
                workspace_id=new_ws.id,
                shortcut=qr.shortcut,
                title=qr.title,
                message=qr.message,
                category=qr.category
            )
            db.add(new_qr)
            copied_counts["quick_replies"] += 1

    # 6. Copy Automation Flows
    if payload.copy_flows:
        flow_res = await db.execute(select(AutomationFlow).where(AutomationFlow.workspace_id == src_workspace.id))
        for f in flow_res.scalars().all():
            new_flow = AutomationFlow(
                workspace_id=new_ws.id,
                name=f.name,
                description=f.description,
                status=f.status,
                trigger_type=f.trigger_type,
                trigger_config=f.trigger_config,
                nodes_json=f.nodes_json,
                edges_json=f.edges_json
            )
            db.add(new_flow)
            copied_counts["flows"] += 1

        # Copy Automation Rules
        rule_res = await db.execute(select(AutomationRule).where(AutomationRule.workspace_id == src_workspace.id))
        for r in rule_res.scalars().all():
            new_rule = AutomationRule(
                workspace_id=new_ws.id,
                name=r.name,
                trigger_keyword=r.trigger_keyword,
                match_type=r.match_type,
                condition_contact_is_new=r.condition_contact_is_new,
                action_reply_text=r.action_reply_text,
                action_buttons_json=r.action_buttons_json,
                action_create_lead=r.action_create_lead,
                action_add_tag=r.action_add_tag,
                action_handover=r.action_handover,
                is_active=r.is_active,
                priority=r.priority
            )
            db.add(new_rule)
            copied_counts["rules"] += 1

    # 7. Copy Message Templates
    if payload.copy_templates:
        tmpl_res = await db.execute(select(MessageTemplate).where(MessageTemplate.workspace_id == src_workspace.id))
        for t in tmpl_res.scalars().all():
            new_t = MessageTemplate(
                workspace_id=new_ws.id,
                name=f"{t.name}_{str(uuid.uuid4())[:4]}",
                category=t.category,
                language=t.language,
                status=t.status,
                header_type=t.header_type,
                header_content=t.header_content,
                body_text=t.body_text,
                footer_text=t.footer_text,
                buttons_json=t.buttons_json
            )
            db.add(new_t)
            copied_counts["templates"] += 1

    # 8. Copy AI Settings
    if payload.copy_ai_settings:
        ai_res = await db.execute(select(AISetting).where(AISetting.workspace_id == src_workspace.id))
        ai_src = ai_res.scalars().first()
        if ai_src:
            new_ai = AISetting(
                workspace_id=new_ws.id,
                ai_name=ai_src.ai_name,
                business_name=new_ws.name,
                business_description=ai_src.business_description,
                tone=ai_src.tone,
                instructions=ai_src.instructions,
                fallback_message=ai_src.fallback_message,
                max_tokens=ai_src.max_tokens,
                mode=ai_src.mode,
                auto_handover_on_fallback=ai_src.auto_handover_on_fallback,
                confidence_threshold=ai_src.confidence_threshold
            )
            db.add(new_ai)

    await db.commit()
    await db.refresh(new_ws)

    return ClientCloneResponse(
        new_workspace_id=new_ws.id,
        new_workspace_name=new_ws.name,
        new_workspace_slug=new_ws.slug,
        copied_items=copied_counts,
        message=f"Client '{new_ws.name}' created successfully with template assets copied (credentials and customer data excluded)."
    )
