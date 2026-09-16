from fastapi import APIRouter
from backend.app.api.v1 import (
    auth, workspace, dashboard, conversations, leads, contacts,
    automations, templates, knowledge, ai, team, integrations, search, system, sandbox,
    client_setup, clone, industry_templates, ai_suggest, debugger
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["Workspace"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(automations.router, prefix="/automations", tags=["Automations"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Settings"])
api_router.include_router(team.router, prefix="/team", tags=["Team"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(sandbox.router, prefix="/sandbox", tags=["Sandbox Simulator"])
api_router.include_router(client_setup.router, prefix="/client-setup", tags=["Client Setup Studio"])
api_router.include_router(clone.router, prefix="/client-setup", tags=["Client Clone"])
api_router.include_router(industry_templates.router, prefix="/client-setup", tags=["Industry Templates"])
api_router.include_router(ai_suggest.router, prefix="/inbox", tags=["AI Suggestions"])
api_router.include_router(debugger.router, prefix="/debugger", tags=["Automation Debugger"])
