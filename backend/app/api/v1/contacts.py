from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace
from backend.app.models.workspace import Workspace
from backend.app.models.contact import Contact, Tag, ContactTag
from backend.app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, TagResponse

router = APIRouter()

@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Contact)
        .options(
            selectinload(Contact.tags).selectinload(ContactTag.tag)
        )
        .where(Contact.workspace_id == workspace.id)
    )

    if search:
        stmt = stmt.where(
            (Contact.name.ilike(f"%{search}%")) |
            (Contact.phone.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        )

    stmt = stmt.order_by(Contact.last_active_at.desc().nullslast())
    res = await db.execute(stmt)
    contacts = res.scalars().all()

    output = []
    for c in contacts:
        tags = [TagResponse(id=ct.tag.id, name=ct.tag.name, color=ct.tag.color) for ct in c.tags if ct.tag]
        cr = ContactResponse(
            id=c.id,
            workspace_id=c.workspace_id,
            whatsapp_id=c.whatsapp_id,
            phone=c.phone,
            name=c.name,
            email=c.email,
            avatar_url=c.avatar_url,
            conversation_count=c.conversation_count,
            last_active_at=c.last_active_at,
            created_at=c.created_at,
            tags=tags
        )
        output.append(cr)
    return output

@router.post("", response_model=ContactResponse)
async def create_contact(
    payload: ContactCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Contact).where(Contact.workspace_id == workspace.id, Contact.phone == payload.phone)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Contact with this phone number already exists")

    contact = Contact(
        workspace_id=workspace.id,
        whatsapp_id=payload.phone,
        phone=payload.phone,
        name=payload.name,
        email=payload.email,
        avatar_url=payload.avatar_url
    )
    db.add(contact)
    await db.flush()

    # Add tags if provided
    tags_out = []
    if payload.tags:
        for t_name in payload.tags:
            t_stmt = select(Tag).where(Tag.workspace_id == workspace.id, Tag.name == t_name)
            t_res = await db.execute(t_stmt)
            tag = t_res.scalars().first()
            if not tag:
                tag = Tag(workspace_id=workspace.id, name=t_name, color="#3B82F6")
                db.add(tag)
                await db.flush()
            ct = ContactTag(contact_id=contact.id, tag_id=tag.id)
            db.add(ct)
            tags_out.append(TagResponse(id=tag.id, name=tag.name, color=tag.color))

    await db.commit()
    await db.refresh(contact)

    return ContactResponse(
        id=contact.id,
        workspace_id=contact.workspace_id,
        whatsapp_id=contact.whatsapp_id,
        phone=contact.phone,
        name=contact.name,
        email=contact.email,
        avatar_url=contact.avatar_url,
        conversation_count=contact.conversation_count,
        last_active_at=contact.last_active_at,
        created_at=contact.created_at,
        tags=tags_out
    )

@router.get("/{id}", response_model=ContactResponse)
async def get_contact(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Contact)
        .options(selectinload(Contact.tags).selectinload(ContactTag.tag))
        .where(Contact.id == id, Contact.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    contact = res.scalars().first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    tags = [TagResponse(id=ct.tag.id, name=ct.tag.name, color=ct.tag.color) for ct in contact.tags if ct.tag]
    return ContactResponse(
        id=contact.id,
        workspace_id=contact.workspace_id,
        whatsapp_id=contact.whatsapp_id,
        phone=contact.phone,
        name=contact.name,
        email=contact.email,
        avatar_url=contact.avatar_url,
        conversation_count=contact.conversation_count,
        last_active_at=contact.last_active_at,
        created_at=contact.created_at,
        tags=tags
    )

@router.put("/{id}", response_model=ContactResponse)
async def update_contact(
    id: str,
    payload: ContactUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Contact)
        .options(selectinload(Contact.tags).selectinload(ContactTag.tag))
        .where(Contact.id == id, Contact.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    contact = res.scalars().first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if payload.name is not None:
        contact.name = payload.name
    if payload.email is not None:
        contact.email = payload.email
    if payload.avatar_url is not None:
        contact.avatar_url = payload.avatar_url

    await db.commit()
    await db.refresh(contact)

    tags = [TagResponse(id=ct.tag.id, name=ct.tag.name, color=ct.tag.color) for ct in contact.tags if ct.tag]
    return ContactResponse(
        id=contact.id,
        workspace_id=contact.workspace_id,
        whatsapp_id=contact.whatsapp_id,
        phone=contact.phone,
        name=contact.name,
        email=contact.email,
        avatar_url=contact.avatar_url,
        conversation_count=contact.conversation_count,
        last_active_at=contact.last_active_at,
        created_at=contact.created_at,
        tags=tags
    )
