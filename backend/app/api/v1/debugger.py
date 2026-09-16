import json
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.automation import AutomationFlow, AutomationExecution, ExecutionStatus
from backend.app.models.audit import WebhookEvent

router = APIRouter()

class TraceItemResponse(BaseModel):
    id: str
    flow_id: str
    flow_name: str
    status: str
    input_text: Optional[str] = None
    execution_time_ms: int
    error_message: Optional[str] = None
    logs: Optional[Any] = None
    created_at: str

class WebhookLogResponse(BaseModel):
    id: str
    meta_message_id: Optional[str] = None
    event_type: str
    status: str
    processing_time_ms: int
    raw_payload: str
    error_message: Optional[str] = None
    created_at: str

class SimulateWebhookRequest(BaseModel):
    sender_phone: str = "919876543210"
    message_text: str = "Hello, I want to see your prices"
    sender_name: Optional[str] = "Test User"

@router.get("/traces", response_model=List[TraceItemResponse])
async def get_debugger_traces(
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AutomationExecution, AutomationFlow.name)
        .join(AutomationFlow, AutomationExecution.flow_id == AutomationFlow.id)
        .where(AutomationFlow.workspace_id == workspace.id)
        .order_by(AutomationExecution.created_at.desc())
        .limit(30)
    )
    res = await db.execute(stmt)
    results = []
    for exec_item, flow_name in res.all():
        logs_parsed = None
        if exec_item.logs_json:
            try:
                logs_parsed = json.loads(exec_item.logs_json)
            except Exception:
                logs_parsed = exec_item.logs_json

        results.append(TraceItemResponse(
            id=exec_item.id,
            flow_id=exec_item.flow_id,
            flow_name=flow_name,
            status=exec_item.status.value if hasattr(exec_item.status, "value") else str(exec_item.status),
            input_text=exec_item.input_text,
            execution_time_ms=exec_item.execution_time_ms,
            error_message=exec_item.error_message,
            logs=logs_parsed,
            created_at=exec_item.created_at.isoformat() if exec_item.created_at else ""
        ))
    return results

@router.get("/webhooks", response_model=List[WebhookLogResponse])
async def get_debugger_webhooks(
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(WebhookEvent)
        .where(WebhookEvent.workspace_id == workspace.id)
        .order_by(WebhookEvent.created_at.desc())
        .limit(30)
    )
    res = await db.execute(stmt)
    events = res.scalars().all()
    return [
        WebhookLogResponse(
            id=ev.id,
            meta_message_id=ev.meta_message_id,
            event_type=ev.event_type,
            status=ev.status,
            processing_time_ms=ev.processing_time_ms,
            raw_payload=ev.raw_payload,
            error_message=ev.error_message,
            created_at=ev.created_at.isoformat() if ev.created_at else ""
        )
        for ev in events
    ]

@router.post("/simulate-webhook")
async def simulate_webhook_test(
    payload: SimulateWebhookRequest,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    start_t = time.time()
    # Find matching rules or flows
    flows_stmt = select(AutomationFlow).where(
        AutomationFlow.workspace_id == workspace.id,
        AutomationFlow.is_active == True
    )
    flows = (await db.execute(flows_stmt)).scalars().all()

    matched_flow = None
    input_lower = payload.message_text.lower()
    for f in flows:
        if f.trigger_config:
            try:
                tc = json.loads(f.trigger_config)
                keywords = tc.get("keywords", [])
                if any(kw.lower() in input_lower for kw in keywords):
                    matched_flow = f
                    break
            except Exception:
                pass

    elapsed_ms = int((time.time() - start_t) * 1000)

    trace = {
        "step_1_receive": {"status": "SUCCESS", "from": payload.sender_phone, "text": payload.message_text},
        "step_2_pipeline_eval": {
            "flows_evaluated": len(flows),
            "matched": matched_flow.name if matched_flow else "Default Auto-Reply / Rule Match"
        },
        "step_3_action": {
            "type": "MESSAGE_REPLY",
            "predicted_response": f"Acknowledged receipt of '{payload.message_text}' from {payload.sender_name}"
        },
        "execution_time_ms": elapsed_ms
    }

    return {
        "status": "SIMULATION_SUCCESS",
        "matched_flow": matched_flow.name if matched_flow else None,
        "trace": trace
    }
