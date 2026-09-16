from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.template import MessageTemplate, TemplateVariable, TemplateStatus
from backend.app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateSyncResponse, TemplateVariableSchema
)
from backend.app.integrations.whatsapp.service import WhatsAppMessageService

router = APIRouter()

def get_template_pricing(category: str):
    cat = (category or "").upper()
    if cat == "MARKETING":
        return 0.88, 0.0107, "₹0.88 / msg (Marketing)"
    elif cat == "AUTHENTICATION":
        return 0.15, 0.0018, "₹0.15 / msg (Auth OTP)"
    elif cat == "SERVICE":
        return 0.00, 0.0000, "₹0.00 Free (24h Service)"
    else:  # UTILITY
        return 0.35, 0.0042, "₹0.35 / msg (Utility)"

@router.get("/pricing-summary")
async def get_pricing_summary(
    workspace: Workspace = Depends(get_current_workspace)
):
    """Returns official Meta Cloud API conversation-based pricing for India (+91)"""
    return {
        "rates": {
            "MARKETING": {
                "inr": 0.88,
                "usd": 0.0107,
                "label": "Marketing",
                "description": "Promotions, deals, discounts, announcements, re-engagement"
            },
            "UTILITY": {
                "inr": 0.35,
                "usd": 0.0042,
                "label": "Utility",
                "description": "Order confirmations, billing, shipping updates, hello_world"
            },
            "AUTHENTICATION": {
                "inr": 0.15,
                "usd": 0.0018,
                "label": "Authentication",
                "description": "One-time passwords (OTP) and account security verification"
            },
            "SERVICE": {
                "inr": 0.00,
                "usd": 0.0000,
                "label": "Service (24h)",
                "description": "Customer-initiated support queries within active 24h window"
            }
        },
        "currency": "INR",
        "symbol": "₹",
        "country": "India (+91)",
        "meta_billing_note": "Meta charges per 24-hour conversation window based on category."
    }

@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    tpl_status: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(MessageTemplate)
        .options(selectinload(MessageTemplate.variables))
        .where(MessageTemplate.workspace_id == workspace.id)
    )
    if tpl_status:
        stmt = stmt.where(MessageTemplate.status == tpl_status.upper())
    stmt = stmt.order_by(MessageTemplate.created_at.desc())

    res = await db.execute(stmt)
    templates = res.scalars().all()
    output = []
    for t in templates:
        vars_schema = [
            TemplateVariableSchema(
                variable_index=v.variable_index,
                variable_name=v.variable_name,
                mapping_source=v.mapping_source
            )
            for v in t.variables
        ]
        cat_str = t.category.value if hasattr(t.category, "value") else str(t.category)
        inr, usd, badge = get_template_pricing(cat_str)
        tr = TemplateResponse(
            id=t.id,
            workspace_id=t.workspace_id,
            meta_template_id=t.meta_template_id,
            name=t.name,
            category=t.category,
            language=t.language,
            status=t.status,
            rejection_reason=t.rejection_reason,
            header_type=t.header_type,
            header_content=t.header_content,
            body_text=t.body_text,
            footer_text=t.footer_text,
            buttons_json=t.buttons_json,
            estimated_cost_inr=inr,
            estimated_cost_usd=usd,
            cost_badge=badge,
            created_at=t.created_at,
            variables=vars_schema
        )
        output.append(tr)
    return output

@router.post("", response_model=TemplateResponse)
async def create_template(
    payload: TemplateCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MessageTemplate).where(
        MessageTemplate.workspace_id == workspace.id,
        MessageTemplate.name == payload.name,
        MessageTemplate.language == payload.language
    )
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Template with this name and language already exists")

    tpl = MessageTemplate(
        workspace_id=workspace.id,
        name=payload.name,
        category=payload.category,
        language=payload.language,
        status=TemplateStatus.APPROVED,  # Marked as approved in sandbox/demo, or submitted to Meta
        header_type=payload.header_type,
        header_content=payload.header_content,
        body_text=payload.body_text,
        footer_text=payload.footer_text,
        buttons_json=payload.buttons_json
    )
    db.add(tpl)
    await db.flush()

    vars_out = []
    if payload.variables:
        for v in payload.variables:
            tv = TemplateVariable(
                template_id=tpl.id,
                variable_index=v.variable_index,
                variable_name=v.variable_name,
                mapping_source=v.mapping_source
            )
            db.add(tv)
            vars_out.append(v)

    await db.commit()
    await db.refresh(tpl)

    cat_str = tpl.category.value if hasattr(tpl.category, "value") else str(tpl.category)
    inr, usd, badge = get_template_pricing(cat_str)

    return TemplateResponse(
        id=tpl.id,
        workspace_id=tpl.workspace_id,
        meta_template_id=tpl.meta_template_id,
        name=tpl.name,
        category=tpl.category,
        language=tpl.language,
        status=tpl.status,
        rejection_reason=tpl.rejection_reason,
        header_type=tpl.header_type,
        header_content=tpl.header_content,
        body_text=tpl.body_text,
        footer_text=tpl.footer_text,
        buttons_json=tpl.buttons_json,
        estimated_cost_inr=inr,
        estimated_cost_usd=usd,
        cost_badge=badge,
        created_at=tpl.created_at,
        variables=vars_out
    )

@router.get("/{id}", response_model=TemplateResponse)
async def get_template(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(MessageTemplate)
        .options(selectinload(MessageTemplate.variables))
        .where(MessageTemplate.id == id, MessageTemplate.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    t = res.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    vars_schema = [
        TemplateVariableSchema(
            variable_index=v.variable_index,
            variable_name=v.variable_name,
            mapping_source=v.mapping_source
        )
        for v in t.variables
    ]
    cat_str = t.category.value if hasattr(t.category, "value") else str(t.category)
    inr, usd, badge = get_template_pricing(cat_str)
    return TemplateResponse(
        id=t.id,
        workspace_id=t.workspace_id,
        meta_template_id=t.meta_template_id,
        name=t.name,
        category=t.category,
        language=t.language,
        status=t.status,
        rejection_reason=t.rejection_reason,
        header_type=t.header_type,
        header_content=t.header_content,
        body_text=t.body_text,
        footer_text=t.footer_text,
        buttons_json=t.buttons_json,
        estimated_cost_inr=inr,
        estimated_cost_usd=usd,
        cost_badge=badge,
        created_at=t.created_at,
        variables=vars_schema
    )

@router.delete("/{id}")
async def delete_template(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MessageTemplate).where(MessageTemplate.id == id, MessageTemplate.workspace_id == workspace.id)
    res = await db.execute(stmt)
    tpl = res.scalars().first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(tpl)
    await db.commit()
    return {"status": "success", "message": "Template deleted"}

@router.post("/sync", response_model=TemplateSyncResponse)
async def sync_templates_from_meta(
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    msg_service = WhatsAppMessageService(db)
    provider = await msg_service.get_provider(workspace.id)
    remote_templates = await provider.fetch_templates()

    synced_count = 0
    for rt in remote_templates:
        tpl_name = rt.get("name")
        tpl_lang = rt.get("language", "en_US")
        tpl_status = rt.get("status", "APPROVED").upper()

        stmt = select(MessageTemplate).where(
            MessageTemplate.workspace_id == workspace.id,
            MessageTemplate.name == tpl_name,
            MessageTemplate.language == tpl_lang
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            if tpl_status in [s.value for s in TemplateStatus]:
                existing.status = TemplateStatus(tpl_status)
            synced_count += 1
        else:
            # Build body text from components
            body_text = "Sample template text"
            for comp in rt.get("components", []):
                if comp.get("type") == "BODY":
                    body_text = comp.get("text", body_text)

            new_tpl = MessageTemplate(
                workspace_id=workspace.id,
                meta_template_id=rt.get("id"),
                name=tpl_name,
                language=tpl_lang,
                status=TemplateStatus(tpl_status) if tpl_status in [s.value for s in TemplateStatus] else TemplateStatus.APPROVED,
                body_text=body_text
            )
            db.add(new_tpl)
            synced_count += 1

    await db.commit()

    # Re-fetch templates
    all_tpls = await list_templates(None, workspace, db)
    return TemplateSyncResponse(synced_count=synced_count, templates=all_tpls)
