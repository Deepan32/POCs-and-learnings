import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.automation import (
    AutomationFlow, AutomationRule, FlowStatus, TriggerType, AutomationExecution, ExecutionStatus
)
from backend.app.schemas.automation import (
    AutomationFlowCreate, AutomationFlowUpdate, AutomationFlowResponse,
    AutomationRuleCreate, AutomationRuleResponse,
    FlowSimulationRequest, FlowSimulationResult
)
from backend.app.automation.conditions import ConditionEvaluator

router = APIRouter()

# --- Visual Flow Builder Endpoints ---

@router.get("/flows", response_model=List[AutomationFlowResponse])
async def list_flows(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AutomationFlow)
        .where(AutomationFlow.workspace_id == workspace.id)
        .order_by(AutomationFlow.priority.asc(), AutomationFlow.created_at.desc())
    )
    res = await db.execute(stmt)
    flows = res.scalars().all()
    return [AutomationFlowResponse.model_validate(f) for f in flows]

@router.post("/flows", response_model=AutomationFlowResponse)
async def create_flow(
    payload: AutomationFlowCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    flow = AutomationFlow(
        workspace_id=workspace.id,
        name=payload.name,
        description=payload.description,
        priority=payload.priority or 10,
        trigger_type=payload.trigger_type,
        trigger_config=payload.trigger_config,
        nodes_json=payload.nodes_json,
        edges_json=payload.edges_json,
        is_active=payload.is_active if payload.is_active is not None else True,
        status=FlowStatus.PUBLISHED,
        version=1
    )
    db.add(flow)
    await db.commit()
    await db.refresh(flow)
    return AutomationFlowResponse.model_validate(flow)

@router.get("/flows/{id}", response_model=AutomationFlowResponse)
async def get_flow(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AutomationFlow).where(AutomationFlow.id == id, AutomationFlow.workspace_id == workspace.id)
    res = await db.execute(stmt)
    flow = res.scalars().first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return AutomationFlowResponse.model_validate(flow)

@router.put("/flows/{id}", response_model=AutomationFlowResponse)
async def update_flow(
    id: str,
    payload: AutomationFlowUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AutomationFlow).where(AutomationFlow.id == id, AutomationFlow.workspace_id == workspace.id)
    res = await db.execute(stmt)
    flow = res.scalars().first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    if payload.name is not None:
        flow.name = payload.name
    if payload.description is not None:
        flow.description = payload.description
    if payload.priority is not None:
        flow.priority = payload.priority
    if payload.is_active is not None:
        flow.is_active = payload.is_active
    if payload.trigger_type is not None:
        flow.trigger_type = payload.trigger_type
    if payload.trigger_config is not None:
        flow.trigger_config = payload.trigger_config
    if payload.nodes_json is not None:
        flow.nodes_json = payload.nodes_json
        flow.version += 1
    if payload.edges_json is not None:
        flow.edges_json = payload.edges_json
    if payload.status is not None:
        flow.status = payload.status

    await db.commit()
    await db.refresh(flow)
    return AutomationFlowResponse.model_validate(flow)

@router.delete("/flows/{id}")
async def delete_flow(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AutomationFlow).where(AutomationFlow.id == id, AutomationFlow.workspace_id == workspace.id)
    res = await db.execute(stmt)
    flow = res.scalars().first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    await db.delete(flow)
    await db.commit()
    return {"status": "success", "message": "Flow deleted"}

@router.post("/test-simulation", response_model=FlowSimulationResult)
async def simulate_flow(
    payload: FlowSimulationRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulation Runner: Simulates incoming message against rules and flows without sending real WhatsApp messages.
    """
    test_msg = payload.message_text.strip().lower()
    steps = [f"1. Ingest simulated message: '{payload.message_text}' from {payload.contact_phone}"]

    # Check for human handover
    if any(hk in test_msg for hk in ["human", "agent", "support person", "talk to someone"]):
        steps.append("2. Priority Handover Rule: Matched keyword for human assistance.")
        steps.append("3. Action: Set conversation_mode = HUMAN. Suppress bot automation.")
        steps.append("4. Action: Route to agent queue.")
        return FlowSimulationResult(
            matched=True,
            flow_name="Emergency Human Handover",
            execution_steps=steps,
            response_preview="Connecting you to our team specialist immediately. A human agent will assist you shortly! 👨‍💼",
            triggered_handover=True
        )

    # Check rules
    stmt = select(AutomationRule).where(
        AutomationRule.workspace_id == workspace.id,
        AutomationRule.is_active == True
    ).order_by(AutomationRule.priority.asc())
    res = await db.execute(stmt)
    rules = res.scalars().all()

    for r in rules:
        steps.append(f"Evaluating rule '{r.name}' (Priority {r.priority}) [WHEN contains '{r.trigger_keyword}']")
        if ConditionEvaluator.match_text(test_msg, r.trigger_keyword, r.match_type):
            steps.append(f"✓ Condition matched on trigger keyword: '{r.trigger_keyword}'")
            buttons = json.loads(r.action_buttons_json) if r.action_buttons_json else []
            if r.action_create_lead:
                steps.append(f"✓ Action: Captured new lead from {payload.contact_phone}")
            if r.action_add_tag:
                steps.append(f"✓ Action: Applied tag '{r.action_add_tag}' to contact")
            if r.action_handover:
                steps.append("✓ Action: Triggered Human Handover")

            return FlowSimulationResult(
                matched=True,
                flow_name=r.name,
                execution_steps=steps,
                response_preview=r.action_reply_text,
                buttons_preview=buttons,
                created_lead=r.action_create_lead,
                triggered_handover=r.action_handover
            )

    steps.append("No active rule or trigger condition matched the simulated message.")
    return FlowSimulationResult(
        matched=False,
        flow_name=None,
        execution_steps=steps,
        response_preview="[Fallback/AI Default Response]"
    )

# --- Simplified No-Code Rules Endpoints ---

@router.get("/rules", response_model=List[AutomationRuleResponse])
async def list_rules(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AutomationRule)
        .where(AutomationRule.workspace_id == workspace.id)
        .order_by(AutomationRule.priority.asc())
    )
    res = await db.execute(stmt)
    rules = res.scalars().all()
    return [AutomationRuleResponse.model_validate(r) for r in rules]

@router.post("/rules", response_model=AutomationRuleResponse)
async def create_rule(
    payload: AutomationRuleCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    rule = AutomationRule(
        workspace_id=workspace.id,
        name=payload.name,
        priority=payload.priority or 10,
        trigger_keyword=payload.trigger_keyword,
        match_type=payload.match_type or "contains",
        condition_contact_is_new=payload.condition_contact_is_new or False,
        action_reply_text=payload.action_reply_text,
        action_buttons_json=payload.action_buttons_json,
        action_create_lead=payload.action_create_lead or False,
        action_add_tag=payload.action_add_tag,
        action_handover=payload.action_handover or False,
        is_active=payload.is_active if payload.is_active is not None else True
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return AutomationRuleResponse.model_validate(rule)

@router.put("/rules/{id}", response_model=AutomationRuleResponse)
async def update_rule(
    id: str,
    payload: AutomationRuleCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AutomationRule).where(AutomationRule.id == id, AutomationRule.workspace_id == workspace.id)
    res = await db.execute(stmt)
    rule = res.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.name = payload.name
    rule.priority = payload.priority or rule.priority
    rule.trigger_keyword = payload.trigger_keyword
    rule.match_type = payload.match_type or "contains"
    rule.condition_contact_is_new = payload.condition_contact_is_new or False
    rule.action_reply_text = payload.action_reply_text
    rule.action_buttons_json = payload.action_buttons_json
    rule.action_create_lead = payload.action_create_lead or False
    rule.action_add_tag = payload.action_add_tag
    rule.action_handover = payload.action_handover or False
    if payload.is_active is not None:
        rule.is_active = payload.is_active

    await db.commit()
    await db.refresh(rule)
    return AutomationRuleResponse.model_validate(rule)

@router.delete("/rules/{id}")
async def delete_rule(
    id: str,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AutomationRule).where(AutomationRule.id == id, AutomationRule.workspace_id == workspace.id)
    res = await db.execute(stmt)
    rule = res.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
    return {"status": "success", "message": "Rule deleted"}
