import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import AsyncSessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models import (
    Workspace, WorkspaceMember, RoleEnum, User, WhatsAppAccount,
    Contact, Tag, ContactTag, Conversation, ConversationMode, ConversationStatus,
    Message, MessageDirection, MessageOrigin, MessageDeliveryStatus, MessageType,
    Lead, LeadStatus, LeadStageHistory,
    MessageTemplate, TemplateVariable, TemplateCategory, TemplateStatus, TemplateHeaderType,
    AutomationFlow, AutomationRule, FlowStatus, TriggerType,
    KnowledgeBase, KnowledgeDocument, KnowledgeCategory,
    AISetting, AIMode, AITone
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("allstreak.seed")

async def seed_database():
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        res = await db.execute(select(User).where(User.email == "admin@allstreak.com"))
        if res.scalars().first():
            logger.info("Database already seeded with demo workspace. Skipping.")
            return

        logger.info("Seeding ALLSTREAK demo workspace...")

        # 1. Create Demo Workspace
        workspace = Workspace(
            name="ALLSTREAK Demo",
            slug="allstreak-demo",
            industry="SaaS & E-Commerce",
            timezone="Asia/Kolkata",
            country="IN",
            business_hours_config=json.dumps({
                "monday": {"open": "09:00", "close": "18:00", "enabled": True},
                "tuesday": {"open": "09:00", "close": "18:00", "enabled": True},
                "wednesday": {"open": "09:00", "close": "18:00", "enabled": True},
                "thursday": {"open": "09:00", "close": "18:00", "enabled": True},
                "friday": {"open": "09:00", "close": "18:00", "enabled": True},
                "saturday": {"open": "10:00", "close": "14:00", "enabled": True},
                "sunday": {"open": "00:00", "close": "00:00", "enabled": False}
            })
        )
        db.add(workspace)
        await db.flush()

        # 2. Create Users
        admin_user = User(
            email="admin@allstreak.com",
            hashed_password=get_password_hash("Allstreak@2026"),
            full_name="Surya (Architect)",
            phone_number="+919800000001",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)

        agent_user = User(
            email="agent@allstreak.com",
            hashed_password=get_password_hash("Allstreak@2026"),
            full_name="Sarah Jenkins (Senior Agent)",
            phone_number="+919800000002",
            is_active=True
        )
        db.add(agent_user)
        await db.flush()

        # Memberships
        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=admin_user.id, role=RoleEnum.OWNER))
        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=agent_user.id, role=RoleEnum.AGENT))

        # 3. WhatsApp Account (Sandbox / Cloud API Ready)
        whatsapp_acc = WhatsAppAccount(
            workspace_id=workspace.id,
            phone_number_id="sandbox_phone_12345",
            waba_id="waba_demo_882910",
            business_id="biz_meta_449201",
            display_phone_number="+1 (555) 019-2834",
            verified_name="ALLSTREAK Demo Official",
            access_token="EAAX_ALLSTREAK_SANDBOX_DEMO_TOKEN_XYZ123",
            webhook_verify_token="allstreak_secure_verify_token_2026",
            quality_rating="GREEN"
        )
        db.add(whatsapp_acc)

        # 4. Tags
        tags = [
            Tag(workspace_id=workspace.id, name="Hot Lead", color="#EF4444"),
            Tag(workspace_id=workspace.id, name="VIP", color="#F59E0B"),
            Tag(workspace_id=workspace.id, name="Support", color="#3B82F6"),
            Tag(workspace_id=workspace.id, name="Pricing", color="#10B981"),
        ]
        db.add_all(tags)
        await db.flush()

        # 5. Contacts (Rahul, Priya, Arun, Meena)
        now = datetime.now(timezone.utc)
        rahul = Contact(
            workspace_id=workspace.id,
            whatsapp_id="919876543210",
            phone="+919876543210",
            name="Rahul Sharma",
            email="rahul.sharma@example.com",
            conversation_count=3,
            last_active_at=now - timedelta(minutes=5)
        )
        priya = Contact(
            workspace_id=workspace.id,
            whatsapp_id="919812345678",
            phone="+919812345678",
            name="Priya Patel",
            email="priya.patel@acme-corp.in",
            conversation_count=4,
            last_active_at=now - timedelta(minutes=15)
        )
        arun = Contact(
            workspace_id=workspace.id,
            whatsapp_id="919845012345",
            phone="+919845012345",
            name="Arun Kumar",
            email="arun.k@techsphere.io",
            conversation_count=6,
            last_active_at=now - timedelta(hours=2)
        )
        meena = Contact(
            workspace_id=workspace.id,
            whatsapp_id="919899887766",
            phone="+919899887766",
            name="Meena Sundaram",
            email="meena.s@innovate.co",
            conversation_count=2,
            last_active_at=now - timedelta(hours=5)
        )
        db.add_all([rahul, priya, arun, meena])
        await db.flush()

        # Associate tags
        db.add(ContactTag(contact_id=rahul.id, tag_id=tags[0].id))  # Hot Lead
        db.add(ContactTag(contact_id=priya.id, tag_id=tags[1].id))  # VIP
        db.add(ContactTag(contact_id=arun.id, tag_id=tags[2].id))   # Support
        db.add(ContactTag(contact_id=meena.id, tag_id=tags[3].id))  # Pricing

        # 6. Leads across Kanban stages
        lead1 = Lead(
            workspace_id=workspace.id,
            contact_id=rahul.id,
            name="Rahul Sharma",
            phone=rahul.phone,
            email=rahul.email,
            company="Sharma Logistics",
            source="WHATSAPP_AUTOMATION",
            status=LeadStatus.QUALIFIED,
            value=12000.0,
            score=85,
            notes="Interested in 50k WhatsApp monthly messages plan.",
            assigned_agent_id=admin_user.id,
            last_contact_at=now - timedelta(minutes=5)
        )
        lead2 = Lead(
            workspace_id=workspace.id,
            contact_id=priya.id,
            name="Priya Patel",
            phone=priya.phone,
            email=priya.email,
            company="Acme Corp India",
            source="WEBSITE_QR",
            status=LeadStatus.PROPOSAL,
            value=35000.0,
            score=95,
            notes="Demo completed. Proposal shared for Enterprise Tier.",
            assigned_agent_id=agent_user.id,
            last_contact_at=now - timedelta(minutes=15)
        )
        lead3 = Lead(
            workspace_id=workspace.id,
            contact_id=meena.id,
            name="Meena Sundaram",
            phone=meena.phone,
            email=meena.email,
            company="Innovate Retail",
            source="WHATSAPP_INBOUND",
            status=LeadStatus.NEW,
            value=5000.0,
            score=45,
            notes="Asked for pricing brochure via automated keyword.",
            assigned_agent_id=agent_user.id,
            last_contact_at=now - timedelta(hours=5)
        )
        lead4 = Lead(
            workspace_id=workspace.id,
            contact_id=arun.id,
            name="Arun Kumar",
            phone=arun.phone,
            email=arun.email,
            company="Techsphere Global",
            source="PARTNER",
            status=LeadStatus.CONVERTED,
            value=48000.0,
            score=100,
            notes="Signed 1-year annual contract.",
            assigned_agent_id=admin_user.id,
            last_contact_at=now - timedelta(hours=2)
        )
        db.add_all([lead1, lead2, lead3, lead4])
        await db.flush()

        # Add Lead Stage History
        db.add(LeadStageHistory(lead_id=lead1.id, from_stage=LeadStatus.NEW, to_stage=LeadStatus.QUALIFIED, notes="Automated score threshold reached"))
        db.add(LeadStageHistory(lead_id=lead2.id, from_stage=LeadStatus.QUALIFIED, to_stage=LeadStatus.PROPOSAL, notes="Sent custom quotation"))
        db.add(LeadStageHistory(lead_id=lead4.id, from_stage=LeadStatus.NEGOTIATION, to_stage=LeadStatus.CONVERTED, notes="Contract executed!"))

        # 7. Conversations
        # Conv 1: Rahul (Active BOT conversation with buttons)
        conv1 = Conversation(
            workspace_id=workspace.id,
            contact_id=rahul.id,
            lead_id=lead1.id,
            mode=ConversationMode.BOT,
            status=ConversationStatus.OPEN,
            unread_count=0,
            last_message_preview="Hello! 👋 How can I help you?",
            last_message_at=now - timedelta(minutes=5),
            last_customer_message_at=now - timedelta(minutes=6),
            window_expires_at=now + timedelta(hours=23, minutes=54)
        )
        # Conv 2: Priya (Human Handover mode!)
        conv2 = Conversation(
            workspace_id=workspace.id,
            contact_id=priya.id,
            lead_id=lead2.id,
            assigned_agent_id=agent_user.id,
            mode=ConversationMode.HUMAN,
            status=ConversationStatus.OPEN,
            unread_count=1,
            handover_reason="Customer requested: 'I want to speak to an enterprise account manager'",
            handover_at=now - timedelta(minutes=15),
            last_message_preview="Can someone walk me through enterprise SLA and custom data retention?",
            last_message_at=now - timedelta(minutes=15),
            last_customer_message_at=now - timedelta(minutes=15),
            window_expires_at=now + timedelta(hours=23, minutes=45)
        )
        # Conv 3: Arun (AI Mode)
        conv3 = Conversation(
            workspace_id=workspace.id,
            contact_id=arun.id,
            lead_id=lead4.id,
            mode=ConversationMode.AI,
            status=ConversationStatus.OPEN,
            unread_count=0,
            last_message_preview="Our business hours are Mon-Fri 9:00 AM to 6:00 PM IST.",
            last_message_at=now - timedelta(hours=2),
            last_customer_message_at=now - timedelta(hours=2, minutes=2),
            window_expires_at=now + timedelta(hours=21, minutes=58)
        )
        # Conv 4: Meena (Resolved)
        conv4 = Conversation(
            workspace_id=workspace.id,
            contact_id=meena.id,
            lead_id=lead3.id,
            mode=ConversationMode.BOT,
            status=ConversationStatus.RESOLVED,
            unread_count=0,
            last_message_preview="Thank you! Let us know if you need anything else.",
            last_message_at=now - timedelta(hours=5),
            last_customer_message_at=now - timedelta(hours=5, minutes=10),
            window_expires_at=now + timedelta(hours=18, minutes=50)
        )
        db.add_all([conv1, conv2, conv3, conv4])
        await db.flush()

        # Messages for Rahul (Conv 1)
        db.add(Message(
            conversation_id=conv1.id,
            meta_message_id="wamid.HBgRahul01=",
            direction=MessageDirection.INBOUND,
            origin=MessageOrigin.CUSTOMER,
            status=MessageDeliveryStatus.READ,
            message_type=MessageType.TEXT,
            body="Hi",
            created_at=now - timedelta(minutes=6),
            delivered_at=now - timedelta(minutes=6),
            read_at=now - timedelta(minutes=5)
        ))
        db.add(Message(
            conversation_id=conv1.id,
            meta_message_id="wamid.HBgBot01=",
            direction=MessageDirection.OUTBOUND,
            origin=MessageOrigin.BOT,
            status=MessageDeliveryStatus.READ,
            message_type=MessageType.TEXT,
            body="Hello! 👋 Welcome to ALLSTREAK. How can we help you accelerate your business today?",
            buttons_json=json.dumps(["Sales", "Support", "Pricing", "Talk to Human"]),
            created_at=now - timedelta(minutes=5),
            sent_at=now - timedelta(minutes=5),
            delivered_at=now - timedelta(minutes=5),
            read_at=now - timedelta(minutes=5)
        ))

        # Messages for Priya (Conv 2 - Handover)
        db.add(Message(
            conversation_id=conv2.id,
            meta_message_id="wamid.HBgPriya01=",
            direction=MessageDirection.INBOUND,
            origin=MessageOrigin.CUSTOMER,
            status=MessageDeliveryStatus.READ,
            message_type=MessageType.TEXT,
            body="I want to speak with a human agent regarding enterprise deployment.",
            created_at=now - timedelta(minutes=16),
            delivered_at=now - timedelta(minutes=16)
        ))
        db.add(Message(
            conversation_id=conv2.id,
            meta_message_id="wamid.HBgBot02=",
            direction=MessageDirection.OUTBOUND,
            origin=MessageOrigin.BOT,
            status=MessageDeliveryStatus.DELIVERED,
            message_type=MessageType.TEXT,
            body="Connecting you to our team specialist immediately. A human agent will assist you shortly! 👨‍💼",
            created_at=now - timedelta(minutes=15)
        ))
        db.add(Message(
            conversation_id=conv2.id,
            meta_message_id="wamid.HBgPriya02=",
            direction=MessageDirection.INBOUND,
            origin=MessageOrigin.CUSTOMER,
            status=MessageDeliveryStatus.DELIVERED,
            message_type=MessageType.TEXT,
            body="Can someone walk me through enterprise SLA and custom data retention?",
            created_at=now - timedelta(minutes=15)
        ))

        # 8. Templates
        tpl1 = MessageTemplate(
            workspace_id=workspace.id,
            meta_template_id="meta_tpl_welcome_001",
            name="welcome_greeting",
            category=TemplateCategory.UTILITY,
            language="en_US",
            status=TemplateStatus.APPROVED,
            header_type=TemplateHeaderType.TEXT,
            header_content="Welcome to {{1}}",
            body_text="Hello {{2}}, thank you for connecting with us on WhatsApp! Our team is excited to assist you.",
            footer_text="Reply STOP to opt out"
        )
        tpl2 = MessageTemplate(
            workspace_id=workspace.id,
            meta_template_id="meta_tpl_order_002",
            name="order_confirmation",
            category=TemplateCategory.UTILITY,
            language="en_US",
            status=TemplateStatus.APPROVED,
            header_type=TemplateHeaderType.NONE,
            body_text="Hi {{1}}, your order #{{2}} has been confirmed and is being packed. Track your shipment anytime by replying TRACK.",
            footer_text="ALLSTREAK Verified Updates"
        )
        tpl3 = MessageTemplate(
            workspace_id=workspace.id,
            meta_template_id="meta_tpl_promo_003",
            name="flash_sale_offer",
            category=TemplateCategory.MARKETING,
            language="en_US",
            status=TemplateStatus.APPROVED,
            header_type=TemplateHeaderType.TEXT,
            header_content="Special Deal Just For You!",
            body_text="Hey {{1}}, get 25% off our annual growth automation plan today using promo code {{2}}.",
            footer_text="Valid for 48 hours only"
        )
        db.add_all([tpl1, tpl2, tpl3])
        await db.flush()

        db.add(TemplateVariable(template_id=tpl1.id, variable_index=1, variable_name="business_name", mapping_source="workspace.name"))
        db.add(TemplateVariable(template_id=tpl1.id, variable_index=2, variable_name="customer_name", mapping_source="contact.name"))
        db.add(TemplateVariable(template_id=tpl2.id, variable_index=1, variable_name="customer_name", mapping_source="contact.name"))
        db.add(TemplateVariable(template_id=tpl2.id, variable_index=2, variable_name="order_id", mapping_source="custom.order_id"))

        # 9. Automation Rules (Simplified No-Code Rules)
        rule_handover = AutomationRule(
            workspace_id=workspace.id,
            name="Human Request Escalation",
            priority=1,  # Highest priority
            trigger_keyword="human",
            match_type="contains",
            action_reply_text="Connecting you to our team specialist immediately. A human agent will assist you shortly! 👨‍💼",
            action_handover=True,
            is_active=True
        )
        rule_pricing = AutomationRule(
            workspace_id=workspace.id,
            name="Pricing Inquiries",
            priority=2,
            trigger_keyword="pricing",
            match_type="contains",
            action_reply_text="Here are our WhatsApp automation plans:\n\n• Starter: $49/mo (5,000 msgs)\n• Growth: $149/mo (25,000 msgs)\n• Enterprise: Custom\n\nWould you like a sales specialist to reach out?",
            action_buttons_json=json.dumps(["Talk to Sales", "View Full Plans", "Start Free Trial"]),
            action_create_lead=True,
            action_add_tag="Pricing",
            is_active=True
        )
        rule_greeting = AutomationRule(
            workspace_id=workspace.id,
            name="Default Welcome Greeting",
            priority=3,
            trigger_keyword="hi",
            match_type="contains",
            action_reply_text="Hello! 👋 Welcome to ALLSTREAK. How can we help you accelerate your business today?",
            action_buttons_json=json.dumps(["Sales", "Support", "Pricing", "Talk to Human"]),
            action_create_lead=True,
            action_add_tag="Hot Lead",
            is_active=True
        )
        db.add_all([rule_handover, rule_pricing, rule_greeting])

        # 10. Visual Automation Flow (React Flow structure)
        demo_nodes = [
            {"id": "node-trigger", "type": "triggerNode", "position": {"x": 250, "y": 50}, "data": {"label": "Message Received: 'hi'", "triggerType": "KEYWORD", "keyword": "hi"}},
            {"id": "node-cond", "type": "conditionNode", "position": {"x": 250, "y": 180}, "data": {"label": "Check If New Contact", "condition": "is_new_contact"}},
            {"id": "node-reply", "type": "actionNode", "position": {"x": 100, "y": 320}, "data": {"label": "Send Welcome Menu", "actionType": "SEND_TEXT", "text": "Hello! 👋 Welcome to ALLSTREAK.", "buttons": ["Sales", "Support", "Pricing", "Talk to Human"]}},
            {"id": "node-lead", "type": "actionNode", "position": {"x": 100, "y": 460}, "data": {"label": "Capture Lead in CRM", "actionType": "CREATE_LEAD"}},
            {"id": "node-handover", "type": "actionNode", "position": {"x": 400, "y": 320}, "data": {"label": "Handover to Human Queue", "actionType": "HUMAN_HANDOVER"}}
        ]
        demo_edges = [
            {"id": "e1-2", "source": "node-trigger", "target": "node-cond", "animated": True},
            {"id": "e2-3", "source": "node-cond", "target": "node-reply", "label": "Yes"},
            {"id": "e3-4", "source": "node-reply", "target": "node-lead"},
            {"id": "e2-5", "source": "node-cond", "target": "node-handover", "label": "No"}
        ]
        visual_flow = AutomationFlow(
            workspace_id=workspace.id,
            name="Main Customer Welcome Journey",
            description="Autonomous onboarding flow with lead generation and human handover option.",
            priority=1,
            version=1,
            status=FlowStatus.PUBLISHED,
            trigger_type=TriggerType.KEYWORD,
            trigger_config=json.dumps({"keyword": "hi", "match_type": "contains"}),
            nodes_json=json.dumps(demo_nodes),
            edges_json=json.dumps(demo_edges),
            triggered_count=1240,
            completed_count=1198,
            leads_generated_count=322,
            handovers_count=88,
            is_active=True
        )
        db.add(visual_flow)

        # 11. Knowledge Base & Documents
        kb = KnowledgeBase(
            workspace_id=workspace.id,
            name="Company Official Knowledge Base",
            description="Core FAQs, pricing packages, working hours, and operational policies.",
            is_active=True
        )
        db.add(kb)
        await db.flush()

        docs = [
            KnowledgeDocument(
                knowledge_base_id=kb.id,
                title="Business Working Hours",
                category=KnowledgeCategory.HOURS,
                question="What are your support and working hours?",
                answer_or_content="Our team is actively available Monday to Friday from 9:00 AM to 6:00 PM IST. Weekend support is active for emergency enterprise incidents.",
                keywords="hours, timing, schedule, open, working days"
            ),
            KnowledgeDocument(
                knowledge_base_id=kb.id,
                title="Subscription Pricing & Tiers",
                category=KnowledgeCategory.PRICING,
                question="What are your subscription pricing options?",
                answer_or_content="We offer Starter ($49/month including 5,000 WhatsApp conversations), Growth ($149/month including 25,000 conversations with visual flow builder), and Enterprise (custom volume with dedicated account manager and 99.9% SLA).",
                keywords="price, cost, pricing, plans, subscription, billing"
            ),
            KnowledgeDocument(
                knowledge_base_id=kb.id,
                title="Meta WhatsApp Cloud API Connection",
                category=KnowledgeCategory.FAQ,
                question="How does ALLSTREAK connect to WhatsApp?",
                answer_or_content="ALLSTREAK connects directly via official Meta WhatsApp Cloud API v21.0 using your Phone Number ID and System User Access Token. No third-party unofficial bridges.",
                keywords="meta, cloud api, connect, official, api token"
            ),
            KnowledgeDocument(
                knowledge_base_id=kb.id,
                title="Refund and Cancellation Policy",
                category=KnowledgeCategory.POLICY,
                question="What is your cancellation or refund policy?",
                answer_or_content="Subscriptions can be canceled anytime with a single click from Settings. We offer a no-questions-asked 14-day money-back guarantee.",
                keywords="refund, cancel, guarantee, money back"
            )
        ]
        db.add_all(docs)

        # 12. AI Settings
        ai_setting = AISetting(
            workspace_id=workspace.id,
            ai_name="Streak AI",
            business_name="ALLSTREAK Inc.",
            business_description="Next-generation WhatsApp automation and lead conversion platform.",
            tone=AITone.PROFESSIONAL,
            instructions="You are Streak AI, an intelligent, helpful WhatsApp assistant. Answer concisely and accurately based on company policies. If unable to answer with confidence or if customer expresses frustration, politely transfer to a human specialist.",
            fallback_message="I'm not completely certain about that specific detail. Let me immediately connect you with our human specialist! 👋",
            mode=AIMode.AUTO,
            auto_handover_on_fallback=True,
            confidence_threshold=0.7
        )
        db.add(ai_setting)

        await db.commit()
        logger.info("Successfully seeded ALLSTREAK demo workspace with complete dataset!")

if __name__ == "__main__":
    asyncio.run(seed_database())
