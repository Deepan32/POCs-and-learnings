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
from backend.app.models.conversation import Conversation, ConversationStatus, ConversationMode, ConversationAssignment
from backend.app.models.contact import Contact
from backend.app.models.message import Message, MessageOrigin, MessageType
from backend.app.schemas.conversation import (
    ConversationResponse, ConversationUpdate, HandoverRequest, ReturnToBotRequest, AssignAgentRequest, StartConversationRequest
)
from backend.app.schemas.message import MessageResponse, SendMessageRequest, SendTemplateRequest
from backend.app.integrations.whatsapp.service import WhatsAppMessageService
from backend.app.core.websocket_manager import ws_manager
from backend.app.schemas.auth import UserResponse
from backend.app.schemas.contact import ContactResponse, TagResponse

router = APIRouter()


def format_conversation(conv: Conversation) -> ConversationResponse:
    contact_res = None
    if conv.contact:
        tags_list = []
        if "tags" in conv.contact.__dict__:
            for ct in conv.contact.tags:
                if hasattr(ct, "tag") and ct.tag:
                    tags_list.append(TagResponse(id=ct.tag.id, name=ct.tag.name, color=ct.tag.color))
        contact_res = ContactResponse(
            id=conv.contact.id,
            workspace_id=conv.contact.workspace_id,
            whatsapp_id=conv.contact.whatsapp_id,
            phone=conv.contact.phone,
            name=conv.contact.name,
            email=conv.contact.email,
            avatar_url=conv.contact.avatar_url,
            conversation_count=conv.contact.conversation_count,
            last_active_at=conv.contact.last_active_at,
            created_at=conv.contact.created_at,
            tags=tags_list
        )
    return ConversationResponse(
        id=conv.id,
        workspace_id=conv.workspace_id,
        contact_id=conv.contact_id,
        assigned_agent_id=conv.assigned_agent_id,
        mode=conv.mode,
        status=conv.status,
        unread_count=conv.unread_count,
        last_message_preview=conv.last_message_preview,
        last_message_at=conv.last_message_at,
        last_customer_message_at=conv.last_customer_message_at,
        window_expires_at=conv.window_expires_at,
        is_window_open=conv.is_window_open,
        handover_reason=conv.handover_reason,
        handover_at=conv.handover_at,
        lead_id=conv.lead_id,
        created_at=conv.created_at,
        contact=contact_res,
        assigned_agent=UserResponse.model_validate(conv.assigned_agent) if conv.assigned_agent else None
    )

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    tab: Optional[str] = Query("all"),  # all, unread, assigned_to_me, unassigned, bot, ai, human
    conv_status: Optional[str] = Query(None),  # OPEN, RESOLVED
    search: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.contact),
            selectinload(Conversation.assigned_agent)
        )
        .where(Conversation.workspace_id == workspace.id)
    )

    if tab == "unread":
        stmt = stmt.where(Conversation.unread_count > 0)
    elif tab == "assigned_to_me":
        stmt = stmt.where(Conversation.assigned_agent_id == user.id)
    elif tab == "unassigned":
        stmt = stmt.where(Conversation.assigned_agent_id == None)
    elif tab == "bot":
        stmt = stmt.where(Conversation.mode == ConversationMode.BOT)
    elif tab == "ai":
        stmt = stmt.where(Conversation.mode == ConversationMode.AI)
    elif tab == "human":
        stmt = stmt.where(Conversation.mode == ConversationMode.HUMAN)

    if conv_status:
        stmt = stmt.where(Conversation.status == conv_status.upper())

    if search:
        # Join contact to filter by name or phone
        stmt = stmt.join(Contact).where(
            (Contact.name.ilike(f"%{search}%")) |
            (Contact.phone.ilike(f"%{search}%")) |
            (Conversation.last_message_preview.ilike(f"%{search}%"))
        )

    stmt = stmt.order_by(Conversation.last_message_at.desc().nullslast())
    res = await db.execute(stmt)
    conversations = res.scalars().all()

    return [format_conversation(c) for c in conversations]

@router.post("/start", response_model=ConversationResponse)
async def start_conversation(
    payload: StartConversationRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually add/start a new WhatsApp conversation with any phone number.
    Creates or retrieves the contact, initializes the chat thread, and dispatches an initial message/template if provided.
    """
    clean_phone = "".join(filter(str.isdigit, payload.phone))
    if not clean_phone or len(clean_phone) < 7:
        raise HTTPException(status_code=400, detail="Please provide a valid WhatsApp phone number with country code.")
    if len(clean_phone) == 10 and clean_phone[0] in "6789":
        clean_phone = "91" + clean_phone

    # 1. Look up or create contact
    stmt = select(Contact).where(
        Contact.workspace_id == workspace.id,
        Contact.phone == clean_phone
    )
    res = await db.execute(stmt)
    contact = res.scalars().first()
    now_utc = datetime.now(timezone.utc)
    
    if not contact:
        contact = Contact(
            workspace_id=workspace.id,
            whatsapp_id=clean_phone,
            phone=clean_phone,
            name=payload.name.strip() if payload.name and payload.name.strip() else f"WhatsApp Contact {clean_phone[-4:]}",
            conversation_count=1,
            last_active_at=now_utc
        )
        db.add(contact)
        await db.flush()
    else:
        if payload.name and payload.name.strip():
            contact.name = payload.name.strip()
        contact.last_active_at = now_utc

    # 2. Look up or create conversation
    conv_stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.contact),
            selectinload(Conversation.assigned_agent)
        )
        .where(
            Conversation.workspace_id == workspace.id,
            Conversation.contact_id == contact.id
        )
    )
    conv_res = await db.execute(conv_stmt)
    conv = conv_res.scalars().first()

    preview_text = payload.initial_message or (f"[Template: {payload.template_name}]" if payload.template_name else "Manual chat initialized")
    if not conv:
        conv = Conversation(
            workspace_id=workspace.id,
            contact_id=contact.id,
            assigned_agent_id=user.id,
            mode=payload.mode or ConversationMode.HUMAN,
            status=ConversationStatus.OPEN,
            unread_count=0,
            last_message_preview=preview_text[:100],
            last_message_at=now_utc,
            created_at=now_utc
        )
        db.add(conv)
        await db.flush()
    else:
        conv.status = ConversationStatus.OPEN
        conv.assigned_agent_id = user.id
        if payload.mode:
            conv.mode = payload.mode
        conv.last_message_at = now_utc

    await db.commit()
    await db.refresh(conv)

    # 3. If initial message or template requested, dispatch it immediately via WhatsApp service
    msg_service = WhatsAppMessageService(db)
    if payload.template_name:
        await msg_service.send_message(
            conversation=conv,
            origin=MessageOrigin.HUMAN,
            sender_id=user.id,
            message_type=MessageType.TEMPLATE,
            template_name=payload.template_name,
            template_variables={"1": contact.name or "Customer", "2": "#1001"},
            bypass_window_check=True
        )
    elif payload.initial_message and payload.initial_message.strip():
        await msg_service.send_message(
            conversation=conv,
            body=payload.initial_message.strip(),
            origin=MessageOrigin.HUMAN,
            sender_id=user.id,
            message_type=MessageType.TEXT,
            bypass_window_check=True
        )

    # Re-fetch formatted conversation with relationships
    refetch_stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.contact),
            selectinload(Conversation.assigned_agent)
        )
        .where(Conversation.id == conv.id)
    )
    refetch_res = await db.execute(refetch_stmt)
    final_conv = refetch_res.scalars().first()
    return format_conversation(final_conv)

@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.contact),
            selectinload(Conversation.assigned_agent)
        )
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Mark as read
    if conv.unread_count > 0:
        conv.unread_count = 0
        await db.commit()

    return format_conversation(conv)


@router.get("/{id}/messages", response_model=List[MessageResponse])
async def list_messages(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    # Verify conversation belongs to workspace
    stmt = select(Conversation).where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    c_res = await db.execute(stmt)
    if not c_res.scalars().first():
        raise HTTPException(status_code=404, detail="Conversation not found")

    m_stmt = (
        select(Message)
        .options(selectinload(Message.attachments))
        .where(Message.conversation_id == id)
        .order_by(Message.created_at.asc())
    )
    res = await db.execute(m_stmt)
    messages = res.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]

@router.post("/{id}/reply", response_model=MessageResponse)
async def reply_message(
    id: str,
    payload: SendMessageRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_service = WhatsAppMessageService(db)
    msg = await msg_service.send_message(
        conversation=conv,
        body=payload.body,
        origin=MessageOrigin.HUMAN,
        sender_id=user.id,
        buttons=payload.buttons,
        message_type=payload.message_type,
        media_url=payload.media_url,
        media_filename=payload.media_filename
    )
    return MessageResponse.model_validate(msg)

@router.post("/{id}/reply-template", response_model=MessageResponse)
async def reply_template(
    id: str,
    payload: SendTemplateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_service = WhatsAppMessageService(db)
    msg = await msg_service.send_message(
        conversation=conv,
        origin=MessageOrigin.HUMAN,
        sender_id=user.id,
        template_name=payload.template_name,
        template_language=payload.language_code,
        template_variables=payload.variable_values,
        bypass_window_check=True  # Templates are specifically permitted outside 24h window
    )
    return MessageResponse.model_validate(msg)

@router.post("/{id}/handover", response_model=ConversationResponse)
async def handover_to_human(
    id: str,
    payload: HandoverRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact), selectinload(Conversation.assigned_agent))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.mode = ConversationMode.HUMAN
    conv.handover_reason = payload.reason
    conv.handover_at = datetime.now(timezone.utc)
    conv.returned_to_bot_at = None
    if payload.assigned_agent_id:
        conv.assigned_agent_id = payload.assigned_agent_id
    elif not conv.assigned_agent_id:
        conv.assigned_agent_id = user.id

    await db.commit()
    await db.refresh(conv)

    await ws_manager.broadcast_to_workspace(
        workspace_id=workspace.id,
        event_type="HANDOVER_ALERT",
        data={"conversation_id": conv.id, "reason": payload.reason, "agent_id": conv.assigned_agent_id}
    )
    return format_conversation(conv)

@router.post("/{id}/return-to-automation", response_model=ConversationResponse)
async def return_to_automation(
    id: str,
    payload: ReturnToBotRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact), selectinload(Conversation.assigned_agent))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.mode = payload.target_mode
    conv.returned_to_bot_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(conv)

    await ws_manager.broadcast_to_workspace(
        workspace_id=workspace.id,
        event_type="CONVERSATION_UPDATED",
        data={"conversation_id": conv.id, "mode": conv.mode.value}
    )
    return format_conversation(conv)

@router.post("/{id}/assign", response_model=ConversationResponse)
async def assign_agent(
    id: str,
    payload: AssignAgentRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact), selectinload(Conversation.assigned_agent))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.assigned_agent_id = payload.agent_id
    assignment = ConversationAssignment(
        conversation_id=conv.id,
        agent_id=payload.agent_id,
        assigned_by_id=user.id,
        reason=payload.reason
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(conv)
    return format_conversation(conv)

@router.post("/{id}/resolve", response_model=ConversationResponse)
async def resolve_conversation(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.contact), selectinload(Conversation.assigned_agent))
        .where(Conversation.id == id, Conversation.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.status = ConversationStatus.RESOLVED
    conv.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(conv)
    return format_conversation(conv)

