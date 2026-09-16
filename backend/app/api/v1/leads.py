from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, get_current_workspace
from backend.app.models.user import User
from backend.app.models.workspace import Workspace
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead, LeadStatus, LeadStageHistory
from backend.app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadStageUpdate, LeadKanbanResponse, LeadKanbanColumn
)
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

@router.get("", response_model=List[LeadResponse])
async def list_leads(
    lead_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.workspace_id == workspace.id)
    )

    if lead_status:
        stmt = stmt.where(Lead.status == lead_status.upper())

    if search:
        stmt = stmt.where(
            (Lead.name.ilike(f"%{search}%")) |
            (Lead.phone.ilike(f"%{search}%")) |
            (Lead.company.ilike(f"%{search}%"))
        )

    stmt = stmt.order_by(Lead.created_at.desc())
    res = await db.execute(stmt)
    leads = res.scalars().all()
    return [LeadResponse.model_validate(l) for l in leads]

@router.get("/kanban", response_model=LeadKanbanResponse)
async def get_lead_kanban(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.workspace_id == workspace.id)
        .order_by(Lead.updated_at.desc())
    )
    res = await db.execute(stmt)
    leads = res.scalars().all()

    # Define standard pipeline stages
    pipeline_stages = [
        (LeadStatus.NEW, "New Leads"),
        (LeadStatus.CONTACTED, "Contacted"),
        (LeadStatus.QUALIFIED, "Qualified"),
        (LeadStatus.PROPOSAL, "Proposal Sent"),
        (LeadStatus.NEGOTIATION, "Negotiation"),
        (LeadStatus.CONVERTED, "Converted 🎉"),
        (LeadStatus.LOST, "Lost")
    ]

    columns = []
    for stage_enum, label in pipeline_stages:
        stage_leads = [LeadResponse.model_validate(l) for l in leads if l.status == stage_enum]
        total_val = sum(l.value for l in stage_leads)
        columns.append(
            LeadKanbanColumn(
                stage=stage_enum,
                label=label,
                count=len(stage_leads),
                total_value=round(total_val, 2),
                leads=stage_leads
            )
        )

    return LeadKanbanResponse(columns=columns)

@router.post("", response_model=LeadResponse)
async def create_lead(
    payload: LeadCreate,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Find or create contact
    contact_id = payload.contact_id
    if not contact_id:
        c_stmt = select(Contact).where(Contact.workspace_id == workspace.id, Contact.phone == payload.phone)
        c_res = await db.execute(c_stmt)
        c = c_res.scalars().first()
        if not c:
            c = Contact(
                workspace_id=workspace.id,
                whatsapp_id=payload.phone,
                phone=payload.phone,
                name=payload.name,
                email=payload.email,
                last_active_at=datetime.now(timezone.utc)
            )
            db.add(c)
            await db.flush()
        contact_id = c.id

    lead = Lead(
        workspace_id=workspace.id,
        contact_id=contact_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        company=payload.company,
        source=payload.source or "MANUAL",
        status=payload.status or LeadStatus.NEW,
        value=payload.value or 0.0,
        score=payload.score or 10,
        notes=payload.notes,
        assigned_agent_id=payload.assigned_agent_id or user.id,
        last_contact_at=datetime.now(timezone.utc)
    )
    db.add(lead)
    await db.flush()

    history = LeadStageHistory(
        lead_id=lead.id,
        changed_by_id=user.id,
        from_stage=None,
        to_stage=lead.status,
        notes="Lead created"
    )
    db.add(history)
    await db.commit()

    # Re-query with relations
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.id == lead.id)
    )
    res = await db.execute(stmt)
    full_lead = res.scalar_one()

    await ws_manager.broadcast_to_workspace(
        workspace_id=workspace.id,
        event_type="LEAD_CREATED",
        data={"lead_id": lead.id, "name": lead.name, "status": lead.status.value}
    )

    return LeadResponse.model_validate(full_lead)

@router.get("/{id}", response_model=LeadResponse)
async def get_lead(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.id == id, Lead.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)

@router.put("/{id}", response_model=LeadResponse)
async def update_lead(
    id: str,
    payload: LeadUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.id == id, Lead.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status

    if payload.name is not None:
        lead.name = payload.name
    if payload.email is not None:
        lead.email = payload.email
    if payload.company is not None:
        lead.company = payload.company
    if payload.value is not None:
        lead.value = payload.value
    if payload.score is not None:
        lead.score = payload.score
    if payload.notes is not None:
        lead.notes = payload.notes
    if payload.assigned_agent_id is not None:
        lead.assigned_agent_id = payload.assigned_agent_id

    if payload.status is not None and payload.status != old_status:
        lead.status = payload.status
        history = LeadStageHistory(
            lead_id=lead.id,
            changed_by_id=user.id,
            from_stage=old_status,
            to_stage=payload.status,
            notes=f"Moved from {old_status.value} to {payload.status.value}"
        )
        db.add(history)

    await db.commit()
    await db.refresh(lead)

    await ws_manager.broadcast_to_workspace(
        workspace_id=workspace.id,
        event_type="LEAD_UPDATED",
        data={"lead_id": lead.id, "name": lead.name, "status": lead.status.value, "score": lead.score}
    )

    return LeadResponse.model_validate(lead)

@router.put("/{id}/stage", response_model=LeadResponse)
async def update_lead_stage(
    id: str,
    payload: LeadStageUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead)
        .options(
            selectinload(Lead.contact),
            selectinload(Lead.assigned_agent),
            selectinload(Lead.stage_history)
        )
        .where(Lead.id == id, Lead.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_stage = lead.status
    lead.status = payload.status
    lead.last_contact_at = datetime.now(timezone.utc)

    # Automatically boost score if advancing stage
    if payload.status in [LeadStatus.QUALIFIED, LeadStatus.PROPOSAL, LeadStatus.NEGOTIATION]:
        lead.score = min(lead.score + 15, 100)
    elif payload.status == LeadStatus.CONVERTED:
        lead.score = 100

    history = LeadStageHistory(
        lead_id=lead.id,
        changed_by_id=user.id,
        from_stage=old_stage,
        to_stage=payload.status,
        notes=payload.notes or f"Kanban drag to {payload.status.value}"
    )
    db.add(history)
    await db.commit()
    await db.refresh(lead)

    await ws_manager.broadcast_to_workspace(
        workspace_id=workspace.id,
        event_type="LEAD_STAGE_CHANGED",
        data={"lead_id": lead.id, "from_stage": old_stage.value, "to_stage": lead.status.value}
    )

    return LeadResponse.model_validate(lead)

@router.post("/{id}/convert", response_model=LeadResponse)
async def convert_lead(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await update_lead_stage(
        id=id,
        payload=LeadStageUpdate(status=LeadStatus.CONVERTED, notes="Successfully closed and converted lead!"),
        workspace=workspace,
        user=user,
        db=db
    )

@router.delete("/{id}")
async def delete_lead(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lead).where(Lead.id == id, Lead.workspace_id == workspace.id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    return {"status": "success", "message": "Lead deleted successfully"}
