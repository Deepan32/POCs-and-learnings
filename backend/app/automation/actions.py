import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.conversation import Conversation, ConversationMode
from backend.app.models.contact import Contact, Tag, ContactTag
from backend.app.models.lead import Lead, LeadStatus, LeadStageHistory
from backend.app.models.message import MessageOrigin, MessageType
from backend.app.integrations.whatsapp.service import WhatsAppMessageService
from backend.app.core.websocket_manager import ws_manager

logger = logging.getLogger("allstreak.automation.actions")

class ActionExecutor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.msg_service = WhatsAppMessageService(db)

    async def execute_send_reply(
        self,
        conversation: Conversation,
        text: str,
        buttons: Optional[List[str]] = None,
        origin: MessageOrigin = MessageOrigin.BOT
    ):
        await self.msg_service.send_message(
            conversation=conversation,
            body=text,
            origin=origin,
            buttons=buttons,
            message_type=MessageType.TEXT,
            bypass_window_check=True
        )

    async def execute_create_or_update_lead(
        self,
        conversation: Conversation,
        source: str = "WHATSAPP_AUTOMATION",
        score_increment: int = 20
    ) -> Lead:
        contact: Contact = conversation.contact
        if not contact:
            c_stmt = select(Contact).where(Contact.id == conversation.contact_id)
            c_res = await self.db.execute(c_stmt)
            contact = c_res.scalar_one()

        # Check existing lead
        stmt = select(Lead).where(
            Lead.workspace_id == conversation.workspace_id,
            Lead.contact_id == contact.id
        )
        res = await self.db.execute(stmt)
        lead = res.scalars().first()

        if not lead:
            lead = Lead(
                workspace_id=conversation.workspace_id,
                contact_id=contact.id,
                name=contact.name or f"WhatsApp Lead {contact.phone[-4:]}",
                phone=contact.phone,
                email=contact.email,
                source=source,
                status=LeadStatus.NEW,
                score=min(score_increment, 100),
                last_contact_at=datetime.now(timezone.utc)
            )
            self.db.add(lead)
            await self.db.flush()

            # Record history
            history = LeadStageHistory(
                lead_id=lead.id,
                from_stage=None,
                to_stage=LeadStatus.NEW,
                notes="Automated lead capture via WhatsApp"
            )
            self.db.add(history)
            conversation.lead_id = lead.id
        else:
            lead.score = min(lead.score + score_increment, 100)
            lead.last_contact_at = datetime.now(timezone.utc)

        await self.db.commit()

        # Broadcast lead event
        await ws_manager.broadcast_to_workspace(
            workspace_id=conversation.workspace_id,
            event_type="LEAD_UPDATED",
            data={"lead_id": lead.id, "name": lead.name, "score": lead.score, "status": lead.status.value}
        )
        return lead

    async def execute_add_tag(self, conversation: Conversation, tag_name: str):
        # Find or create tag
        stmt = select(Tag).where(Tag.workspace_id == conversation.workspace_id, Tag.name == tag_name)
        res = await self.db.execute(stmt)
        tag = res.scalars().first()
        if not tag:
            tag = Tag(workspace_id=conversation.workspace_id, name=tag_name, color="#10B981")
            self.db.add(tag)
            await self.db.flush()

        # Associate with contact if not already tagged
        ct_stmt = select(ContactTag).where(ContactTag.contact_id == conversation.contact_id, ContactTag.tag_id == tag.id)
        ct_res = await self.db.execute(ct_stmt)
        if not ct_res.scalars().first():
            ct = ContactTag(contact_id=conversation.contact_id, tag_id=tag.id)
            self.db.add(ct)
            await self.db.commit()

    async def execute_human_handover(
        self,
        conversation: Conversation,
        reason: str = "Customer requested human assistance",
        send_ack_message: bool = True
    ):
        conversation.mode = ConversationMode.HUMAN
        conversation.handover_reason = reason
        conversation.handover_at = datetime.now(timezone.utc)
        conversation.returned_to_bot_at = None

        if send_ack_message:
            await self.msg_service.send_message(
                conversation=conversation,
                body="Connecting you to our team specialist immediately. A human agent will assist you shortly! 👨‍💼",
                origin=MessageOrigin.BOT,
                bypass_window_check=True
            )

        await self.db.commit()

        # Broadcast handover alert
        await ws_manager.broadcast_to_workspace(
            workspace_id=conversation.workspace_id,
            event_type="HANDOVER_ALERT",
            data={
                "conversation_id": conversation.id,
                "reason": reason,
                "timestamp": conversation.handover_at.isoformat()
            }
        )
