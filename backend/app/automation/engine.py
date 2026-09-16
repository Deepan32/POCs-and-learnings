import json
import time
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.conversation import Conversation, ConversationMode
from backend.app.models.message import Message, MessageOrigin
from backend.app.models.contact import Contact
from backend.app.models.automation import (
    AutomationRule, AutomationFlow, AutomationExecution, FlowStatus, ExecutionStatus
)
from backend.app.models.ai import AISetting, AIMode
from backend.app.automation.loop_guard import LoopGuard
from backend.app.automation.conditions import ConditionEvaluator
from backend.app.automation.actions import ActionExecutor
from backend.app.automation.priority import PriorityResolver
from backend.app.ai.agent import AIAgentEngine

logger = logging.getLogger("allstreak.automation.engine")

class AutomationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.action_executor = ActionExecutor(db)
        self.ai_engine = AIAgentEngine(db)

    async def process_incoming_message(
        self,
        conversation: Conversation,
        message: Message
    ) -> bool:
        start_time = time.time()
        
        # 1. Loop Guard
        if not LoopGuard.is_loop_safe(message):
            logger.info("Message bypassed by LoopGuard")
            return False

        # 2. Conversation Mode Check
        if conversation.mode == ConversationMode.HUMAN:
            logger.info(f"Conversation {conversation.id} is in HUMAN mode. Suppressing automation.")
            return False

        message_text = (message.body or "").strip()
        if not message_text:
            return False

        contact: Contact = conversation.contact
        if not contact:
            c_stmt = select(Contact).where(Contact.id == conversation.contact_id)
            c_res = await self.db.execute(c_stmt)
            contact = c_res.scalar_one()

        # 3. Check for Global Human Handover Keywords (Priority 1)
        handover_keywords = ["human", "agent", "support person", "talk to someone", "talk to human", "representative", "helpdesk"]
        if any(hk in message_text.lower() for hk in handover_keywords):
            logger.info(f"Triggering priority human handover for conversation {conversation.id}")
            await self.action_executor.execute_human_handover(
                conversation=conversation,
                reason=f"Customer keyword trigger: '{message_text}'"
            )
            return True

        # 4. If conversation is in AI mode, route directly to AI agent
        if conversation.mode == ConversationMode.AI:
            answer, conf, should_handover = await self.ai_engine.generate_response(
                workspace_id=conversation.workspace_id,
                user_message=message_text
            )
            if should_handover:
                await self.action_executor.execute_human_handover(
                    conversation=conversation,
                    reason="AI Agent triggered handover"
                )
            elif answer:
                await self.action_executor.execute_send_reply(
                    conversation=conversation,
                    text=answer,
                    origin=MessageOrigin.AI
                )
            return True

        # 5. Evaluate Workspace Automation Rules in Priority Order
        rules_stmt = select(AutomationRule).where(
            AutomationRule.workspace_id == conversation.workspace_id,
            AutomationRule.is_active == True
        )
        rules_res = await self.db.execute(rules_stmt)
        rules = rules_res.scalars().all()
        sorted_rules = PriorityResolver.sort_rules(list(rules))

        matched_rule: Optional[AutomationRule] = None
        for rule in sorted_rules:
            # Check text condition
            if ConditionEvaluator.match_text(message_text, rule.trigger_keyword, rule.match_type):
                # Check optional condition: is new contact
                if rule.condition_contact_is_new and not ConditionEvaluator.is_new_contact(contact):
                    continue
                matched_rule = rule
                break  # Priority resolver: first highest priority match wins

        if matched_rule:
            logger.info(f"Matched rule: '{matched_rule.name}' for message: '{message_text}'")
            buttons = None
            if matched_rule.action_buttons_json:
                try:
                    buttons = json.loads(matched_rule.action_buttons_json)
                except Exception:
                    pass

            # Execute actions
            if matched_rule.action_handover:
                await self.action_executor.execute_human_handover(
                    conversation=conversation,
                    reason=f"Rule '{matched_rule.name}' triggered handover"
                )
            else:
                await self.action_executor.execute_send_reply(
                    conversation=conversation,
                    text=matched_rule.action_reply_text,
                    buttons=buttons,
                    origin=MessageOrigin.BOT
                )

            if matched_rule.action_create_lead:
                await self.action_executor.execute_create_or_update_lead(
                    conversation=conversation,
                    source=f"RULE_{matched_rule.name.upper()}"
                )

            if matched_rule.action_add_tag:
                await self.action_executor.execute_add_tag(
                    conversation=conversation,
                    tag_name=matched_rule.action_add_tag
                )

            return True

        # 6. Fallback: If AI setting is configured to AUTO, invoke AI
        ai_setting = await self.ai_engine.get_settings(conversation.workspace_id)
        if ai_setting and ai_setting.mode == AIMode.AUTO:
            answer, conf, should_handover = await self.ai_engine.generate_response(
                workspace_id=conversation.workspace_id,
                user_message=message_text
            )
            if should_handover:
                await self.action_executor.execute_human_handover(
                    conversation=conversation,
                    reason="Low confidence AI triggered handover"
                )
            elif answer:
                await self.action_executor.execute_send_reply(
                    conversation=conversation,
                    text=answer,
                    origin=MessageOrigin.AI
                )
            return True

        logger.info(f"No automation rule or AI fallback matched for message '{message_text}'")
        return False
