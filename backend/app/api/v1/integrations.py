from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.whatsapp import WhatsAppAccount
from backend.app.schemas.whatsapp import (
    WhatsAppConnectRequest, WhatsAppAccountResponse, WhatsAppTestResponse,
    WhatsAppSendTestRequest, WhatsAppWebhookInfoResponse
)
from backend.app.integrations.whatsapp.service import WhatsAppMessageService
from backend.app.core.env_manager import sync_env_file, read_meta_from_env

router = APIRouter()

@router.get("/whatsapp", response_model=Optional[WhatsAppAccountResponse])
async def get_whatsapp_integration(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppAccount).where(
        WhatsAppAccount.workspace_id == workspace.id,
        WhatsAppAccount.is_active == True
    )
    res = await db.execute(stmt)
    account = res.scalars().first()
    if not account:
        # Check if credentials exist in .env and auto-provision DB account
        env_meta = read_meta_from_env()
        if env_meta.get("access_token") and env_meta.get("phone_number_id"):
            account = WhatsAppAccount(
                workspace_id=workspace.id,
                phone_number_id=env_meta["phone_number_id"],
                waba_id=env_meta.get("waba_id") or "",
                business_id=env_meta.get("business_id") or None,
                access_token=env_meta["access_token"],
                webhook_verify_token=env_meta.get("webhook_verify_token") or settings.META_VERIFY_TOKEN,
                display_phone_number="+1 (555) 019-2834",
                verified_name=workspace.name,
                is_active=True
            )
            db.add(account)
            await db.commit()
            await db.refresh(account)
        else:
            return None
    return WhatsAppAccountResponse.model_validate(account)

@router.get("/whatsapp/webhook-info", response_model=WhatsAppWebhookInfoResponse)
async def get_whatsapp_webhook_info(
    request: Request,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppAccount).where(WhatsAppAccount.workspace_id == workspace.id)
    res = await db.execute(stmt)
    account = res.scalars().first()

    base_url = str(request.base_url).rstrip("/")
    callback_url = f"{base_url}/webhook/whatsapp"
    
    # Fallback to .env if DB account not yet created
    env_meta = read_meta_from_env()
    is_connected = bool(account and account.access_token) or bool(env_meta.get("access_token") and env_meta.get("phone_number_id"))
    phone_number_id = account.phone_number_id if account else env_meta.get("phone_number_id")
    waba_id = account.waba_id if account else env_meta.get("waba_id")
    verify_token = account.webhook_verify_token if account else (env_meta.get("webhook_verify_token") or settings.META_VERIFY_TOKEN)

    return WhatsAppWebhookInfoResponse(
        is_connected=is_connected,
        phone_number_id=phone_number_id,
        waba_id=waba_id,
        display_phone_number=account.display_phone_number if account else None,
        verified_name=account.verified_name if account else None,
        quality_rating=account.quality_rating if account else "UNKNOWN",
        webhook_verify_token=verify_token,
        callback_url=callback_url,
        saved_to_env=True,
        meta_dashboard_url="https://developers.facebook.com/apps"
    )

@router.post("/whatsapp/connect", response_model=WhatsAppAccountResponse)
async def connect_whatsapp(
    payload: WhatsAppConnectRequest,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    verify_tok = payload.webhook_verify_token or settings.META_VERIFY_TOKEN

    # 1. Update or create WhatsAppAccount in the database
    stmt = select(WhatsAppAccount).where(WhatsAppAccount.workspace_id == workspace.id)
    res = await db.execute(stmt)
    account = res.scalars().first()

    if not account:
        account = WhatsAppAccount(
            workspace_id=workspace.id,
            phone_number_id=payload.phone_number_id.strip(),
            waba_id=payload.waba_id.strip(),
            business_id=payload.business_id.strip() if payload.business_id else None,
            access_token=payload.access_token.strip(),
            webhook_verify_token=verify_tok.strip(),
            display_phone_number=payload.display_phone_number or "+1 (555) 019-2834",
            verified_name=payload.verified_name or workspace.name,
            is_active=True
        )
        db.add(account)
    else:
        account.phone_number_id = payload.phone_number_id.strip()
        account.waba_id = payload.waba_id.strip()
        account.business_id = payload.business_id.strip() if payload.business_id else None
        account.access_token = payload.access_token.strip()
        account.webhook_verify_token = verify_tok.strip()
        account.is_active = True
        if payload.display_phone_number:
            account.display_phone_number = payload.display_phone_number
        if payload.verified_name:
            account.verified_name = payload.verified_name

    await db.commit()
    await db.refresh(account)

    # 2. Synchronize credentials directly to the .env file!
    try:
        env_updates = {
            "META_ACCESS_TOKEN": payload.access_token.strip(),
            "META_PHONE_NUMBER_ID": payload.phone_number_id.strip(),
            "META_WABA_ID": payload.waba_id.strip(),
            "META_VERIFY_TOKEN": verify_tok.strip(),
        }
        if payload.business_id:
            env_updates["META_BUSINESS_ID"] = payload.business_id.strip()
        sync_env_file(env_updates)
    except Exception as env_err:
        import logging
        logging.getLogger("allstreak.integrations").warning(f"Could not write to .env: {env_err}")

    # 3. Immediately try validating against Meta Graph API to fetch live verified phone and name
    try:
        msg_service = WhatsAppMessageService(db)
        provider = await msg_service.get_provider(workspace.id)
        val = await provider.validate_credentials()
        if val.get("valid"):
            if val.get("display_phone_number"):
                account.display_phone_number = val.get("display_phone_number")
            if val.get("verified_name"):
                account.verified_name = val.get("verified_name")
            if val.get("quality_rating"):
                account.quality_rating = val.get("quality_rating")
            await db.commit()
            await db.refresh(account)
    except Exception as e:
        # Don't fail the connect call if network/rate limit occurred
        pass

    return WhatsAppAccountResponse.model_validate(account)


@router.post("/whatsapp/test", response_model=WhatsAppTestResponse)
async def test_whatsapp_connection(
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    msg_service = WhatsAppMessageService(db)
    provider = await msg_service.get_provider(workspace.id)
    val = await provider.validate_credentials()
    if val.get("valid"):
        return WhatsAppTestResponse(
            success=True,
            phone_number_id=provider.phone_number_id,
            verified_name=val.get("verified_name"),
            quality_rating=val.get("quality_rating"),
            message="WhatsApp Cloud API connection verified successfully with Meta Graph API!"
        )
    return WhatsAppTestResponse(
        success=False,
        phone_number_id=provider.phone_number_id,
        message=val.get("error", "Failed to validate credentials with Meta Graph API. Please check your Access Token and Phone Number ID.")
    )

@router.post("/whatsapp/send-test-message")
async def send_test_whatsapp_message(
    payload: WhatsAppSendTestRequest,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    msg_service = WhatsAppMessageService(db)
    provider = await msg_service.get_provider(workspace.id)
    
    clean_target = "".join(c for c in payload.to_phone if c.isdigit())
    if not clean_target:
        raise HTTPException(status_code=400, detail="Invalid target phone number format")

    # Meta Cloud API requires a pre-approved template message (like 'hello_world')
    # when initiating a conversation with a new phone outside the 24-hour customer window.
    res = await provider.send_template(
        to_phone=clean_target,
        template_name="hello_world",
        language_code="en_US"
    )
    
    # If hello_world template was not used or failed, fallback to plain text
    if not res.success:
        res = await provider.send_text(
            to_phone=clean_target,
            text=payload.message or "Hello from ALLSTREAK! Meta Cloud API test message successful. 🎉"
        )

    if res.success:
        return {
            "success": True,
            "meta_message_id": res.meta_message_id,
            "to": clean_target,
            "message": "WhatsApp test message sent successfully via Meta Cloud API! Check your phone."
        }
    else:
        return {
            "success": False,

            "error": res.error_message,
            "message": f"Meta API error: {res.error_message}. Note: In Meta development sandbox mode, you must first add recipient numbers to your 'To' test list in Meta Dashboard."
        }

@router.delete("/whatsapp")
async def disconnect_whatsapp(
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppAccount).where(WhatsAppAccount.workspace_id == workspace.id)
    res = await db.execute(stmt)
    account = res.scalars().first()
    if account:
        await db.delete(account)
        await db.commit()
    try:
        sync_env_file({
            "META_ACCESS_TOKEN": "",
            "META_PHONE_NUMBER_ID": "",
            "META_WABA_ID": "",
        })
    except Exception:
        pass
    return {"status": "success", "message": "WhatsApp account disconnected and .env updated"}


