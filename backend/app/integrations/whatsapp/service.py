import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.models.workspace import Workspace
from backend.app.models.whatsapp import WhatsAppAccount
from backend.app.models.conversation import Conversation, ConversationMode
from backend.app.models.message import (
    Message, MessageDirection, MessageOrigin, MessageDeliveryStatus, MessageType
)
from backend.app.models.contact import Contact
from backend.app.integrations.whatsapp.provider import WhatsAppProvider, SendMessageResult
from backend.app.integrations.whatsapp.meta_provider import MetaWhatsAppProvider
from backend.app.integrations.whatsapp.sandbox_provider import SandboxWhatsAppProvider
from backend.app.core.websocket_manager import ws_manager

logger = logging.getLogger("allstreak.whatsapp.service")

class WhatsAppMessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_provider(self, workspace_id: str) -> WhatsAppProvider:
        """Resolve either real Meta provider or sandbox provider based on workspace configuration."""
        stmt = select(WhatsAppAccount).where(
            WhatsAppAccount.workspace_id == workspace_id,
            WhatsAppAccount.is_active == True
        )
        res = await self.db.execute(stmt)
        account = res.scalars().first()

        if account and account.access_token and account.phone_number_id and not account.phone_number_id.startswith("sandbox"):
            return MetaWhatsAppProvider(
                phone_number_id=account.phone_number_id,
                access_token=account.access_token,
                waba_id=account.waba_id,
                graph_url=settings.META_GRAPH_URL,
                api_version=settings.META_API_VERSION
            )
        return SandboxWhatsAppProvider(phone_number_id=account.phone_number_id if account else "sandbox_default")

    async def send_message(
        self,
        conversation: Conversation,
        body: Optional[str] = None,
        origin: MessageOrigin = MessageOrigin.HUMAN,
        sender_id: Optional[str] = None,
        buttons: Optional[List[str]] = None,
        message_type: MessageType = MessageType.TEXT,
        media_url: Optional[str] = None,
        media_filename: Optional[str] = None,
        template_name: Optional[str] = None,
        template_language: str = "en_US",
        template_variables: Optional[Dict[str, str]] = None,
        bypass_window_check: bool = False
    ) -> Message:
        contact: Contact = conversation.contact
        if not contact:
            c_stmt = select(Contact).where(Contact.id == conversation.contact_id)
            c_res = await self.db.execute(c_stmt)
            contact = c_res.scalar_one()

        is_template = (message_type == MessageType.TEMPLATE or template_name is not None)

        # Meta 24-hour customer service window enforcement
        if not is_template and not bypass_window_check:
            if not conversation.is_window_open:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="WhatsApp 24-hour customer service window is closed. A Meta-approved template message is required to initiate contact."
                )

        provider = await self.get_provider(conversation.workspace_id)

        # Create local message record
        msg = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            direction=MessageDirection.OUTBOUND,
            origin=origin,
            status=MessageDeliveryStatus.PENDING,
            message_type=message_type if not is_template else MessageType.TEMPLATE,
            body=body or f"[Template: {template_name}]",
            buttons_json=json.dumps(buttons) if buttons else None,
            template_name=template_name,
            template_language=template_language if is_template else None,
            is_from_template=is_template,
            sent_at=datetime.now(timezone.utc)
        )
        self.db.add(msg)
        await self.db.flush()

        # Send via Provider
        result: SendMessageResult
        if is_template:
            # Build template components if variables provided
            components = []
            if template_variables:
                parameters = []
                for var_idx, var_val in sorted(template_variables.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
                    parameters.append({"type": "text", "text": str(var_val)})
                components.append({"type": "body", "parameters": parameters})
            result = await provider.send_template(
                to_phone=contact.phone,
                template_name=template_name,
                language_code=template_language,
                components=components
            )
        elif message_type in [MessageType.IMAGE, MessageType.VIDEO, MessageType.DOCUMENT] and media_url:
            media_kind = message_type.value.lower()
            result = await provider.send_media(
                to_phone=contact.phone,
                media_type=media_kind,
                media_url=media_url,
                caption=body,
                filename=media_filename
            )
        else:
            result = await provider.send_text(
                to_phone=contact.phone,
                text=body or "",
                buttons=buttons
            )

        # Update message with result
        if result.success:
            msg.status = MessageDeliveryStatus.SENT
            msg.meta_message_id = result.meta_message_id
            if result.raw_response:
                msg.raw_payload = json.dumps(result.raw_response)
        else:
            msg.status = MessageDeliveryStatus.FAILED
            msg.error_message = result.error_message
            msg.failed_at = datetime.now(timezone.utc)

        # Update conversation preview
        conversation.last_message_preview = body[:100] if body else f"[{msg.message_type.value}]"
        conversation.last_message_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(msg)

        # Real-time WebSocket broadcast
        await ws_manager.broadcast_to_workspace(
            workspace_id=conversation.workspace_id,
            event_type="NEW_MESSAGE",
            data={
                "message_id": msg.id,
                "conversation_id": conversation.id,
                "direction": msg.direction.value,
                "origin": msg.origin.value,
                "status": msg.status.value,
                "body": msg.body,
                "meta_message_id": msg.meta_message_id,
                "created_at": msg.created_at.isoformat()
            }
        )

        return msg
