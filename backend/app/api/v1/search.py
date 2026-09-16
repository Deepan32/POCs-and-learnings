from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace
from backend.app.models.workspace import Workspace
from backend.app.models.contact import Contact
from backend.app.models.lead import Lead
from backend.app.models.template import MessageTemplate
from backend.app.models.automation import AutomationRule

router = APIRouter()

@router.get("")
async def global_search(
    q: str = Query(..., min_length=1),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    term = f"%{q.strip()}%"

    # 1. Contacts
    c_stmt = select(Contact).where(
        Contact.workspace_id == workspace.id,
        (Contact.name.ilike(term)) | (Contact.phone.ilike(term)) | (Contact.email.ilike(term))
    ).limit(5)
    contacts = (await db.execute(c_stmt)).scalars().all()

    # 2. Leads
    l_stmt = select(Lead).where(
        Lead.workspace_id == workspace.id,
        (Lead.name.ilike(term)) | (Lead.phone.ilike(term)) | (Lead.company.ilike(term))
    ).limit(5)
    leads = (await db.execute(l_stmt)).scalars().all()

    # 3. Templates
    t_stmt = select(MessageTemplate).where(
        MessageTemplate.workspace_id == workspace.id,
        (MessageTemplate.name.ilike(term)) | (MessageTemplate.body_text.ilike(term))
    ).limit(5)
    templates = (await db.execute(t_stmt)).scalars().all()

    # 4. Automations
    a_stmt = select(AutomationRule).where(
        AutomationRule.workspace_id == workspace.id,
        (AutomationRule.name.ilike(term)) | (AutomationRule.trigger_keyword.ilike(term))
    ).limit(5)
    automations = (await db.execute(a_stmt)).scalars().all()

    return {
        "contacts": [{"id": c.id, "title": c.name or c.phone, "subtitle": c.phone, "link": f"/contacts/{c.id}"} for c in contacts],
        "leads": [{"id": l.id, "title": l.name, "subtitle": f"{l.status.value} • {l.company or l.phone}", "link": f"/leads/{l.id}"} for l in leads],
        "templates": [{"id": t.id, "title": t.name, "subtitle": f"{t.category.value} • {t.status.value}", "link": f"/templates/{t.id}"} for t in templates],
        "automations": [{"id": a.id, "title": a.name, "subtitle": f"Keyword: {a.trigger_keyword}", "link": f"/automations/{a.id}"} for a in automations]
    }
