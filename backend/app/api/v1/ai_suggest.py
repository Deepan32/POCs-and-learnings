from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace
from backend.app.models.workspace import Workspace
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message, MessageDirection
from backend.app.models.product import ProductService
from backend.app.models.quick_reply import QuickReply
from backend.app.schemas.client_setup import AISuggestRequest, AISuggestResponse, AISuggestionItem

router = APIRouter()

@router.post("/suggest", response_model=AISuggestResponse)
async def get_ai_suggestions(
    payload: AISuggestRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates 3 contextual 1-click agent suggested replies:
    1. Direct Answer
    2. Next-step Qualification / Booking
    3. Product / Catalog recommendation
    """
    # 1. Fetch conversation
    conv_stmt = select(Conversation).where(
        Conversation.id == payload.conversation_id,
        Conversation.workspace_id == workspace.id
    )
    conv = (await db.execute(conv_stmt)).scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Fetch last 5 messages
    msg_stmt = select(Message).where(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at.desc()).limit(5)
    recent_msgs = (await db.execute(msg_stmt)).scalars().all()
    recent_msgs.reverse()

    last_customer_text = ""
    for m in reversed(recent_msgs):
        if m.direction == MessageDirection.INBOUND:
            last_customer_text = m.body or ""
            break

    lower_text = last_customer_text.lower()

    # 3. Fetch products and quick replies for context
    p_stmt = select(ProductService).where(
        ProductService.workspace_id == workspace.id,
        ProductService.is_available == True
    ).limit(3)
    products = (await db.execute(p_stmt)).scalars().all()
    product_names = [p.name for p in products]

    qr_stmt = select(QuickReply).where(QuickReply.workspace_id == workspace.id).limit(2)
    quick_replies = (await db.execute(qr_stmt)).scalars().all()

    suggestions = []

    # Strategy 1: Direct Answer
    if any(w in lower_text for w in ["price", "cost", "rate", "how much"]):
        if products:
            p = products[0]
            ans_text = f"Our {p.name} is priced at ₹{p.price:,.0f}. We also have customized packages depending on your requirements!"
        else:
            ans_text = f"Our pricing starts at affordable rates customized to your exact requirements. Would you like a detailed breakdown?"
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="pricing_answer",
            label="Provide Pricing Info",
            text=ans_text
        ))
    elif any(w in lower_text for w in ["time", "hours", "open", "timing", "when"]):
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="hours_answer",
            label="Share Store/Office Hours",
            text=f"We are open Monday to Sunday from 9:00 AM to 9:00 PM. Would you like to drop by or schedule an appointment?"
        ))
    elif any(w in lower_text for w in ["where", "location", "address", "map"]):
        loc_str = workspace.address or workspace.city or "our flagship location"
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="location_answer",
            label="Send Address & Location",
            text=f"📍 We are located at {loc_str}. Let us know if you need driving directions or parking assistance!"
        ))
    else:
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="direct_greeting",
            label="Friendly Assistance",
            text=f"Hello! Thanks for reaching out to {workspace.name}. I would be delighted to assist you with that right away!"
        ))

    # Strategy 2: Lead Qualification / Next Step
    if any(w in lower_text for w in ["order", "buy", "book", "reserve", "appointment"]):
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="schedule_booking",
            label="Confirm Booking Details",
            text="Wonderful! Please share your preferred date, time, and contact name so I can block your slot right now."
        ))
    else:
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="qualify_requirement",
            label="Qualify Requirements",
            text="Could you share a bit more about your exact requirement and preferred timeline so I can tailor the best options for you?"
        ))

    # Strategy 3: Catalog or Quick Action
    if products and len(products) > 0:
        featured = ", ".join(product_names[:2])
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="recommend_product",
            label=f"Recommend {products[0].name[:20]}...",
            text=f"Our most popular options right now include {featured}. Would you like photos and details for these?"
        ))
    elif quick_replies and len(quick_replies) > 0:
        qr = quick_replies[0]
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="quick_reply_preset",
            label=f"Send {qr.title}",
            text=qr.message
        ))
    else:
        suggestions.append(AISuggestionItem(
            id=str(uuid.uuid4()),
            type="human_escalation",
            label="Senior Specialist Connect",
            text=f"I'll have our specialist call you directly in the next 10 minutes to walk you through everything personally. Is this number good?"
        ))

    return AISuggestResponse(
        conversation_id=conv.id,
        suggestions=suggestions
    )
