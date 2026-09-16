import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response, Depends, Query, status, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.whatsapp import WhatsAppAccount
from backend.app.models.contact import Contact
from backend.app.models.conversation import Conversation, ConversationStatus, ConversationMode
from backend.app.models.message import (
    Message, MessageDirection, MessageOrigin, MessageDeliveryStatus, MessageType
)
from backend.app.models.audit import WebhookEvent
from backend.app.integrations.whatsapp.signature import verify_meta_signature
from backend.app.automation.engine import AutomationEngine
from backend.app.core.websocket_manager import ws_manager

logger = logging.getLogger("allstreak.webhook")
router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(
    mode: Optional[str] = Query(None, alias="hub.mode"),
    verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    challenge: Optional[str] = Query(None, alias="hub.challenge"),
    db: AsyncSession = Depends(get_db)
):
    """
    Meta Webhook Verification (GET).
    Validates token against configured settings or WhatsApp accounts and returns challenge.
    """
    logger.info(f"Webhook verification request: mode={mode}, token={verify_token}")
    if mode == "subscribe":
        # Check global verify token or default
        if verify_token in [settings.META_VERIFY_TOKEN, "allstreak_secure_verify_token_2026"]:
            return Response(content=challenge, media_type="text/plain", status_code=200)


        # Or check per-account tokens
        stmt = select(WhatsAppAccount).where(WhatsAppAccount.webhook_verify_token == verify_token)
        res = await db.execute(stmt)
        if res.scalars().first():
            return Response(content=challenge, media_type="text/plain", status_code=200)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("/whatsapp")
async def handle_whatsapp_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db)
):
    """
    Meta WhatsApp Webhook Handler (POST).
    Receives incoming messages, delivery statuses, button clicks, and processes them idempotently.
    """
    raw_body = await request.body()

    # Verify signature if a real app secret is set (ignore dummy placeholders in development)
    app_sec = (settings.META_APP_SECRET or "").strip()
    is_real_secret = bool(app_sec and app_sec not in ["your_meta_app_secret", "your_app_secret", ""])
    if is_real_secret and not verify_meta_signature(raw_body, x_hub_signature_256, app_sec):
        logger.warning("Meta webhook signature verification failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")


    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception as e:
        logger.error(f"Failed to decode JSON payload: {e}")
        return {"status": "error", "message": "Invalid JSON"}

    # Process events in Meta envelope: entry -> changes -> value
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")

            # 1. Resolve WhatsApp Account / Workspace
            stmt = select(WhatsAppAccount).where(WhatsAppAccount.phone_number_id == phone_number_id)
            res = await db.execute(stmt)
            account = res.scalars().first()

            workspace_id = account.workspace_id if account else None
            # If account not mapped yet (e.g. initial demo/test), pick first workspace
            if not workspace_id:
                from backend.app.models.workspace import Workspace
                w_res = await db.execute(select(Workspace).where(Workspace.is_active == True))
                first_ws = w_res.scalars().first()
                if first_ws:
                    workspace_id = first_ws.id

            if not workspace_id:
                logger.warning(f"No workspace found for phone_number_id {phone_number_id}")
                continue

            # 2. Handle Message Status Updates (sent, delivered, read, failed)
            if "statuses" in value:
                for status_update in value["statuses"]:
                    meta_msg_id = status_update.get("id")
                    status_name = status_update.get("status", "").upper()
                    m_stmt = select(Message).where(Message.meta_message_id == meta_msg_id)
                    m_res = await db.execute(m_stmt)
                    existing_msg = m_res.scalars().first()
                    if existing_msg:
                        if status_name == "DELIVERED":
                            existing_msg.status = MessageDeliveryStatus.DELIVERED
                            existing_msg.delivered_at = datetime.now(timezone.utc)
                        elif status_name == "READ":
                            existing_msg.status = MessageDeliveryStatus.READ
                            existing_msg.read_at = datetime.now(timezone.utc)
                        elif status_name == "FAILED":
                            existing_msg.status = MessageDeliveryStatus.FAILED
                            existing_msg.failed_at = datetime.now(timezone.utc)
                            errors = status_update.get("errors", [])
                            if errors:
                                existing_msg.error_message = json.dumps(errors)
                        await db.commit()
                        
                        # Broadcast status update
                        await ws_manager.broadcast_to_workspace(
                            workspace_id=workspace_id,
                            event_type="MESSAGE_STATUS_UPDATED",
                            data={"message_id": existing_msg.id, "status": existing_msg.status.value}
                        )

            # 3. Handle Incoming Messages
            if "messages" in value:
                contacts_data = value.get("contacts", [])
                profile_name = contacts_data[0].get("profile", {}).get("name") if contacts_data else None

                for incoming in value["messages"]:
                    meta_message_id = incoming.get("id")
                    from_phone = incoming.get("from")
                    msg_type = incoming.get("type", "text")

                    # Idempotency Check: Meta message_id unique check
                    dup_stmt = select(Message).where(Message.meta_message_id == meta_message_id)
                    dup_res = await db.execute(dup_stmt)
                    if dup_res.scalars().first():
                        logger.info(f"Duplicate webhook message {meta_message_id} ignored.")
                        continue

                    # Record Webhook Event
                    we = WebhookEvent(
                        workspace_id=workspace_id,
                        meta_message_id=meta_message_id,
                        event_type="incoming_message",
                        status="PROCESSED",
                        raw_payload=json.dumps(incoming)
                    )
                    db.add(we)

                    # Extract body text based on type
                    body_text = ""
                    if msg_type == "text":
                        body_text = incoming.get("text", {}).get("body", "")
                    elif msg_type == "interactive":
                        interactive_obj = incoming.get("interactive", {})
                        if interactive_obj.get("type") == "button_reply":
                            body_text = interactive_obj.get("button_reply", {}).get("title", "")
                        elif interactive_obj.get("type") == "list_reply":
                            body_text = interactive_obj.get("list_reply", {}).get("title", "")
                    elif msg_type == "button":
                        body_text = incoming.get("button", {}).get("text", "")
                    elif msg_type in ["image", "video", "document"]:
                        body_text = incoming.get(msg_type, {}).get("caption", f"[{msg_type.upper()}]")
                    else:
                        body_text = f"[{msg_type.upper()}]"

                    # Find or Create Contact
                    c_stmt = select(Contact).where(
                        Contact.workspace_id == workspace_id,
                        Contact.phone == from_phone
                    )
                    c_res = await db.execute(c_stmt)
                    contact = c_res.scalars().first()
                    if not contact:
                        contact = Contact(
                            workspace_id=workspace_id,
                            whatsapp_id=from_phone,
                            phone=from_phone,
                            name=profile_name or f"WhatsApp User {from_phone[-4:]}",
                            conversation_count=1,
                            last_active_at=datetime.now(timezone.utc)
                        )
                        db.add(contact)
                        await db.flush()
                    else:
                        contact.conversation_count += 1
                        contact.last_active_at = datetime.now(timezone.utc)
                        if profile_name and not contact.name:
                            contact.name = profile_name

                    # Find or Create Conversation
                    conv_stmt = select(Conversation).where(
                        Conversation.workspace_id == workspace_id,
                        Conversation.contact_id == contact.id
                    )
                    conv_res = await db.execute(conv_stmt)
                    conversation = conv_res.scalars().first()

                    now_utc = datetime.now(timezone.utc)
                    if not conversation:
                        conversation = Conversation(
                            workspace_id=workspace_id,
                            contact_id=contact.id,
                            mode=ConversationMode.BOT,
                            status=ConversationStatus.OPEN,
                            unread_count=1,
                            last_message_preview=body_text[:100],
                            last_message_at=now_utc,
                            last_customer_message_at=now_utc,
                            window_expires_at=now_utc + timedelta(hours=settings.WHATSAPP_WINDOW_HOURS)
                        )
                        db.add(conversation)
                        await db.flush()
                    else:
                        conversation.unread_count += 1
                        conversation.last_message_preview = body_text[:100]
                        conversation.last_message_at = now_utc
                        conversation.last_customer_message_at = now_utc
                        conversation.window_expires_at = now_utc + timedelta(hours=settings.WHATSAPP_WINDOW_HOURS)

                    # Store Inbound Message
                    m_type_enum = MessageType.TEXT
                    if msg_type in ["interactive", "button"]:
                        m_type_enum = MessageType.BUTTON
                    elif msg_type == "image":
                        m_type_enum = MessageType.IMAGE
                    elif msg_type == "document":
                        m_type_enum = MessageType.DOCUMENT

                    new_msg = Message(
                        conversation_id=conversation.id,
                        meta_message_id=meta_message_id,
                        direction=MessageDirection.INBOUND,
                        origin=MessageOrigin.CUSTOMER,
                        status=MessageDeliveryStatus.DELIVERED,
                        message_type=m_type_enum,
                        body=body_text,
                        raw_payload=json.dumps(incoming),
                        delivered_at=now_utc
                    )
                    db.add(new_msg)
                    await db.commit()
                    await db.refresh(new_msg)
                    await db.refresh(conversation)

                    # Broadcast Inbound Message via WebSocket
                    await ws_manager.broadcast_to_workspace(
                        workspace_id=workspace_id,
                        event_type="NEW_MESSAGE",
                        data={
                            "message_id": new_msg.id,
                            "conversation_id": conversation.id,
                            "direction": new_msg.direction.value,
                            "origin": new_msg.origin.value,
                            "body": new_msg.body,
                            "created_at": new_msg.created_at.isoformat()
                        }
                    )

                    # 4. Trigger Automation Engine
                    engine = AutomationEngine(db)
                    await engine.process_incoming_message(
                        conversation=conversation,
                        message=new_msg
                    )

    return {"status": "success"}
