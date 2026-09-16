import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace
from backend.app.models.workspace import Workspace
from backend.app.models.contact import Contact
from backend.app.models.conversation import Conversation, ConversationMode, ConversationStatus
from backend.app.models.message import Message, MessageDirection, MessageOrigin, MessageDeliveryStatus, MessageType
from backend.app.automation.engine import AutomationEngine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class SandboxMessageRequest(BaseModel):
    phone: str = "+919876543210"
    name: str = "Rahul Sharma"
    message: str = "Hi"

class SandboxMessageResponse(BaseModel):
    conversation_id: str
    inbound_message_id: str
    contact_name: str
    contact_phone: str
    mode: str
    status: str
    reply_received: bool
    latest_reply: Optional[str] = None
    buttons: Optional[List[str]] = None
    is_handover: bool = False

@router.post("/simulate-message", response_model=SandboxMessageResponse)
async def simulate_sandbox_message(
    payload: SandboxMessageRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    ws_id = workspace.id
    from_phone = payload.phone.strip()
    profile_name = payload.name.strip()
    body_text = payload.message.strip()
    meta_message_id = f"wamid.HBg{uuid.uuid4().hex[:16]}="

    # 1. Find or create Contact
    c_stmt = select(Contact).where(Contact.workspace_id == ws_id, Contact.phone == from_phone)
    c_res = await db.execute(c_stmt)
    contact = c_res.scalars().first()
    now_utc = datetime.now(timezone.utc)

    if not contact:
        contact = Contact(
            workspace_id=ws_id,
            whatsapp_id=from_phone,
            phone=from_phone,
            name=profile_name,
            conversation_count=1,
            last_active_at=now_utc
        )
        db.add(contact)
        await db.flush()
    else:
        contact.conversation_count += 1
        contact.last_active_at = now_utc

    # 2. Find or create Conversation
    conv_stmt = select(Conversation).where(Conversation.workspace_id == ws_id, Conversation.contact_id == contact.id)
    conv_res = await db.execute(conv_stmt)
    conv = conv_res.scalars().first()

    if not conv:
        conv = Conversation(
            workspace_id=ws_id,
            contact_id=contact.id,
            mode=ConversationMode.BOT,
            status=ConversationStatus.OPEN,
            unread_count=1,
            last_message_preview=body_text[:100],
            last_message_at=now_utc,
            last_customer_message_at=now_utc,
            window_expires_at=now_utc + timedelta(hours=settings.WHATSAPP_WINDOW_HOURS)
        )
        db.add(conv)
        await db.flush()
    else:
        conv.unread_count += 1
        conv.last_message_preview = body_text[:100]
        conv.last_message_at = now_utc
        conv.last_customer_message_at = now_utc
        conv.window_expires_at = now_utc + timedelta(hours=settings.WHATSAPP_WINDOW_HOURS)

    # 3. Store Inbound Message
    inbound_msg = Message(
        conversation_id=conv.id,
        meta_message_id=meta_message_id,
        direction=MessageDirection.INBOUND,
        origin=MessageOrigin.CUSTOMER,
        status=MessageDeliveryStatus.DELIVERED,
        message_type=MessageType.TEXT,
        body=body_text,
        delivered_at=now_utc
    )
    db.add(inbound_msg)
    await db.commit()
    await db.refresh(inbound_msg)
    await db.refresh(conv)

    # Broadcast inbound event
    await ws_manager.broadcast_to_workspace(
        workspace_id=ws_id,
        event_type="NEW_MESSAGE",
        data={
            "message_id": inbound_msg.id,
            "conversation_id": conv.id,
            "direction": inbound_msg.direction.value,
            "origin": inbound_msg.origin.value,
            "body": inbound_msg.body,
            "created_at": inbound_msg.created_at.isoformat()
        }
    )

    # 4. Trigger Automation Engine
    engine = AutomationEngine(db)
    processed = await engine.process_incoming_message(
        conversation=conv,
        message=inbound_msg
    )

    # 5. Fetch latest outbound reply if generated
    latest_stmt = (
        select(Message)
        .where(Message.conversation_id == conv.id, Message.direction == MessageDirection.OUTBOUND)
        .order_by(Message.created_at.desc())
    )
    l_res = await db.execute(latest_stmt)
    latest_outbound = l_res.scalars().first()

    buttons = None
    if latest_outbound and latest_outbound.buttons_json:
        try:
            buttons = json.loads(latest_outbound.buttons_json)
        except Exception:
            pass

    await db.refresh(conv)

    return SandboxMessageResponse(
        conversation_id=conv.id,
        inbound_message_id=inbound_msg.id,
        contact_name=contact.name or contact.phone,
        contact_phone=contact.phone,
        mode=conv.mode.value,
        status=conv.status.value,
        reply_received=latest_outbound is not None,
        latest_reply=latest_outbound.body if latest_outbound else None,
        buttons=buttons,
        is_handover=conv.mode == ConversationMode.HUMAN
    )
