import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_workspace, RoleChecker
from backend.app.models.user import User
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.whatsapp import WhatsAppAccount
from backend.app.models.product import ProductService
from backend.app.models.quick_reply import QuickReply
from backend.app.models.versioning import ConfigurationVersion
from backend.app.models.automation import AutomationFlow
from backend.app.models.template import MessageTemplate
from backend.app.models.lead import Lead
from backend.app.schemas.client_setup import (
    BusinessProfileUpdate,
    BrandingUpdate,
    ClientSetupOverview,
    ProductServiceCreate,
    ProductServiceUpdate,
    ProductServiceResponse,
    QuickReplyCreate,
    QuickReplyUpdate,
    QuickReplyResponse,
    ConfigVersionCreate,
    ConfigVersionResponse
)

router = APIRouter()

# --- OVERVIEW ---
@router.get("/overview", response_model=ClientSetupOverview)
async def get_client_setup_overview(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    # WhatsApp Account
    wa_stmt = select(WhatsAppAccount).where(
        WhatsAppAccount.workspace_id == workspace.id,
        WhatsAppAccount.is_active == True
    )
    wa_res = await db.execute(wa_stmt)
    wa_acc = wa_res.scalars().first()

    # Counts
    p_cnt = (await db.execute(select(func.count(ProductService.id)).where(ProductService.workspace_id == workspace.id))).scalar() or 0
    qr_cnt = (await db.execute(select(func.count(QuickReply.id)).where(QuickReply.workspace_id == workspace.id))).scalar() or 0
    f_cnt = (await db.execute(select(func.count(AutomationFlow.id)).where(AutomationFlow.workspace_id == workspace.id))).scalar() or 0
    t_cnt = (await db.execute(select(func.count(MessageTemplate.id)).where(MessageTemplate.workspace_id == workspace.id))).scalar() or 0
    l_cnt = (await db.execute(select(func.count(Lead.id)).where(Lead.workspace_id == workspace.id))).scalar() or 0

    return ClientSetupOverview(
        workspace_id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        industry=workspace.industry,
        timezone=workspace.timezone,
        country=workspace.country,
        phone=workspace.phone,
        email=workspace.email,
        website=workspace.website,
        address=workspace.address,
        city=workspace.city,
        instagram=workspace.instagram,
        facebook=workspace.facebook,
        description=workspace.description,
        business_hours_config=workspace.business_hours_config,
        logo_url=workspace.logo_url,
        primary_color=workspace.primary_color or "#25D366",
        secondary_color=workspace.secondary_color or "#128C7E",
        background_color=workspace.background_color or "#0B141A",
        text_color=workspace.text_color or "#E9EDEF",
        button_style=workspace.button_style or "rounded",
        whatsapp_connected=bool(wa_acc and wa_acc.access_token),
        whatsapp_phone_number=(wa_acc.display_phone_number or wa_acc.phone_number_id) if wa_acc else None,
        whatsapp_quality_rating=wa_acc.quality_rating if wa_acc else None,
        products_count=p_cnt,
        quick_replies_count=qr_cnt,
        flows_count=f_cnt,
        templates_count=t_cnt,
        leads_count=l_cnt
    )

# --- PROFILE UPDATE ---
@router.put("/profile")
async def update_business_profile(
    payload: BusinessProfileUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(workspace, key):
            setattr(workspace, key, value)
    await db.commit()
    await db.refresh(workspace)
    return {"message": "Business profile updated successfully", "name": workspace.name}

# --- BRANDING UPDATE ---
@router.put("/branding")
async def update_branding(
    payload: BrandingUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(workspace, key):
            setattr(workspace, key, value)
    await db.commit()
    await db.refresh(workspace)
    return {"message": "Branding styles updated successfully"}

# --- PRODUCTS / SERVICES CRUD ---
@router.get("/products", response_model=List[ProductServiceResponse])
async def list_products(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductService).where(ProductService.workspace_id == workspace.id).order_by(ProductService.order_index, ProductService.name)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/products", response_model=ProductServiceResponse)
async def create_product(
    payload: ProductServiceCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    item = ProductService(
        workspace_id=workspace.id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        price=payload.price,
        currency=payload.currency or "INR",
        image_url=payload.image_url,
        sku=payload.sku,
        is_available=payload.is_available if payload.is_available is not None else True,
        tags=payload.tags,
        order_index=payload.order_index or 0
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.put("/products/{product_id}", response_model=ProductServiceResponse)
async def update_product(
    product_id: str,
    payload: ProductServiceUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductService).where(
        ProductService.id == product_id,
        ProductService.workspace_id == workspace.id
    )
    res = await db.execute(stmt)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductService).where(
        ProductService.id == product_id,
        ProductService.workspace_id == workspace.id
    )
    res = await db.execute(stmt)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Product removed successfully"}

# --- QUICK REPLIES CRUD ---
@router.get("/quick-replies", response_model=List[QuickReplyResponse])
async def list_quick_replies(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(QuickReply).where(QuickReply.workspace_id == workspace.id).order_by(QuickReply.shortcut)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/quick-replies", response_model=QuickReplyResponse)
async def create_quick_reply(
    payload: QuickReplyCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    reply = QuickReply(
        workspace_id=workspace.id,
        shortcut=payload.shortcut if payload.shortcut.startswith("/") else f"/{payload.shortcut}",
        title=payload.title,
        message=payload.message,
        category=payload.category or "General"
    )
    db.add(reply)
    await db.commit()
    await db.refresh(reply)
    return reply

@router.put("/quick-replies/{reply_id}", response_model=QuickReplyResponse)
async def update_quick_reply(
    reply_id: str,
    payload: QuickReplyUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(QuickReply).where(
        QuickReply.id == reply_id,
        QuickReply.workspace_id == workspace.id
    )
    res = await db.execute(stmt)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Quick reply not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "shortcut" and value and not value.startswith("/"):
            value = f"/{value}"
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/quick-replies/{reply_id}")
async def delete_quick_reply(
    reply_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(QuickReply).where(
        QuickReply.id == reply_id,
        QuickReply.workspace_id == workspace.id
    )
    res = await db.execute(stmt)
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Quick reply not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Quick reply deleted successfully"}

# --- CONFIGURATION SNAPSHOTS & ROLLBACK ---
@router.get("/versions", response_model=List[ConfigVersionResponse])
async def list_versions(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ConfigurationVersion).where(
        ConfigurationVersion.workspace_id == workspace.id
    ).order_by(ConfigurationVersion.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/versions", response_model=ConfigVersionResponse)
async def create_version_snapshot(
    payload: ConfigVersionCreate,
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    # Fetch products and quick replies
    p_res = await db.execute(select(ProductService).where(ProductService.workspace_id == workspace.id))
    products = [
        {
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "price": p.price,
            "currency": p.currency,
            "image_url": p.image_url,
            "sku": p.sku,
            "is_available": p.is_available,
            "tags": p.tags,
            "order_index": p.order_index
        } for p in p_res.scalars().all()
    ]

    qr_res = await db.execute(select(QuickReply).where(QuickReply.workspace_id == workspace.id))
    quick_replies = [
        {
            "shortcut": qr.shortcut,
            "title": qr.title,
            "message": qr.message,
            "category": qr.category
        } for qr in qr_res.scalars().all()
    ]

    snapshot = {
        "workspace_name": workspace.name,
        "industry": workspace.industry,
        "timezone": workspace.timezone,
        "country": workspace.country,
        "phone": workspace.phone,
        "email": workspace.email,
        "website": workspace.website,
        "address": workspace.address,
        "city": workspace.city,
        "instagram": workspace.instagram,
        "facebook": workspace.facebook,
        "description": workspace.description,
        "business_hours_config": workspace.business_hours_config,
        "logo_url": workspace.logo_url,
        "primary_color": workspace.primary_color,
        "secondary_color": workspace.secondary_color,
        "background_color": workspace.background_color,
        "text_color": workspace.text_color,
        "button_style": workspace.button_style,
        "products": products,
        "quick_replies": quick_replies
    }

    ver = ConfigurationVersion(
        workspace_id=workspace.id,
        version_tag=payload.version_tag,
        snapshot_json=json.dumps(snapshot),
        notes=payload.notes,
        created_by=user.name or user.email
    )
    db.add(ver)
    await db.commit()
    await db.refresh(ver)
    return ver

@router.post("/versions/{version_id}/rollback")
async def rollback_to_version(
    version_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ConfigurationVersion).where(
        ConfigurationVersion.id == version_id,
        ConfigurationVersion.workspace_id == workspace.id
    )
    res = await db.execute(stmt)
    ver = res.scalars().first()
    if not ver:
        raise HTTPException(status_code=404, detail="Version snapshot not found")

    snapshot = json.loads(ver.snapshot_json)
    
    # Restore profile & branding
    workspace.industry = snapshot.get("industry", workspace.industry)
    workspace.phone = snapshot.get("phone", workspace.phone)
    workspace.email = snapshot.get("email", workspace.email)
    workspace.website = snapshot.get("website", workspace.website)
    workspace.address = snapshot.get("address", workspace.address)
    workspace.city = snapshot.get("city", workspace.city)
    workspace.instagram = snapshot.get("instagram", workspace.instagram)
    workspace.facebook = snapshot.get("facebook", workspace.facebook)
    workspace.description = snapshot.get("description", workspace.description)
    workspace.business_hours_config = snapshot.get("business_hours_config", workspace.business_hours_config)
    workspace.logo_url = snapshot.get("logo_url", workspace.logo_url)
    workspace.primary_color = snapshot.get("primary_color", workspace.primary_color)
    workspace.secondary_color = snapshot.get("secondary_color", workspace.secondary_color)
    workspace.background_color = snapshot.get("background_color", workspace.background_color)
    workspace.text_color = snapshot.get("text_color", workspace.text_color)
    workspace.button_style = snapshot.get("button_style", workspace.button_style)

    # Restore products
    if "products" in snapshot:
        await db.execute(delete(ProductService).where(ProductService.workspace_id == workspace.id))
        for p in snapshot["products"]:
            db.add(ProductService(
                workspace_id=workspace.id,
                name=p["name"],
                description=p.get("description"),
                category=p.get("category", "General"),
                price=p.get("price", 0.0),
                currency=p.get("currency", "INR"),
                image_url=p.get("image_url"),
                sku=p.get("sku"),
                is_available=p.get("is_available", True),
                tags=p.get("tags"),
                order_index=p.get("order_index", 0)
            ))

    # Restore quick replies
    if "quick_replies" in snapshot:
        await db.execute(delete(QuickReply).where(QuickReply.workspace_id == workspace.id))
        for qr in snapshot["quick_replies"]:
            db.add(QuickReply(
                workspace_id=workspace.id,
                shortcut=qr["shortcut"],
                title=qr["title"],
                message=qr["message"],
                category=qr.get("category", "General")
            ))

    await db.commit()
    return {"message": f"Successfully rolled back to version {ver.version_tag}"}
