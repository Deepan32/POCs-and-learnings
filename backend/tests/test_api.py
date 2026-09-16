import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.config import settings

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["app"] == "ALLSTREAK"
        assert data["status"] == "online"

@pytest.mark.asyncio
async def test_auth_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@allstreak.com"

@pytest.mark.asyncio
async def test_webhook_verification():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=allstreak_secure_verify_token_2026&hub.challenge=987654321"
        )
        assert res.status_code == 200
        assert res.text == "987654321"

@pytest.mark.asyncio
async def test_webhook_invalid_verification():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=987654321"
        )
        assert res.status_code == 403

@pytest.mark.asyncio
async def test_dashboard_metrics():
    # Login first
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        dash_res = await ac.get("/api/v1/dashboard", headers=headers)
        assert dash_res.status_code == 200
        metrics = dash_res.json()
        assert metrics["total_conversations"] >= 4
        assert len(metrics["cards"]) == 9

@pytest.mark.asyncio
async def test_flow_simulation_runner():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test greeting simulation
        sim_res = await ac.post("/api/v1/automations/test-simulation", headers=headers, json={
            "message_text": "hi there"
        })
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert sim_data["matched"] is True
        assert "Welcome to ALLSTREAK" in sim_data["response_preview"]
        assert sim_data["buttons_preview"] is not None

        # Test human handover simulation
        handover_res = await ac.post("/api/v1/automations/test-simulation", headers=headers, json={
            "message_text": "I want to talk to a human agent"
        })
        assert handover_res.status_code == 200
        h_data = handover_res.json()
        assert h_data["triggered_handover"] is True

@pytest.mark.asyncio
async def test_lead_kanban_and_stage_update():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        kanban_res = await ac.get("/api/v1/leads/kanban", headers=headers)
        assert kanban_res.status_code == 200
        kanban = kanban_res.json()
        assert len(kanban["columns"]) == 7

        # Grab first lead from any non-empty column
        lead_id = None
        for col in kanban["columns"]:
            if col.get("leads") and len(col["leads"]) > 0:
                lead_id = col["leads"][0]["id"]
                break
        assert lead_id is not None, "At least one lead should be present in kanban"
        
        # Advance stage
        update_res = await ac.put(f"/api/v1/leads/{lead_id}/stage", headers=headers, json={
            "status": "QUALIFIED",
            "notes": "Verified high budget intent"
        })
        assert update_res.status_code == 200
        assert update_res.json()["status"] == "QUALIFIED"

@pytest.mark.asyncio
async def test_sandbox_simulator_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Send simulated message
        res = await ac.post("/api/v1/sandbox/simulate-message", headers=headers, json={
            "phone": "+919988776655",
            "name": "Kavitha",
            "message": "Hi"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["reply_received"] is True
        assert data["latest_reply"] is not None
        assert "Welcome" in data["latest_reply"]

@pytest.mark.asyncio
async def test_whatsapp_connect_and_env_sync():
    from backend.app.core.env_manager import get_env_path
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Connect with new Meta credentials
        connect_res = await ac.post("/api/v1/integrations/whatsapp/connect", headers=headers, json={
            "access_token": "EAAG_TEST_TOKEN_2026",
            "phone_number_id": "1000999888777",
            "waba_id": "9000888777666",
            "webhook_verify_token": "allstreak_custom_verify_token_999"
        })
        assert connect_res.status_code == 200
        data = connect_res.json()
        assert data["phone_number_id"] == "1000999888777"
        assert data["waba_id"] == "9000888777666"
        assert data["webhook_verify_token"] == "allstreak_custom_verify_token_999"

        # Check webhook info
        wh_info_res = await ac.get("/api/v1/integrations/whatsapp/webhook-info", headers=headers)
        assert wh_info_res.status_code == 200
        wh_data = wh_info_res.json()
        assert wh_data["is_connected"] is True
        assert wh_data["webhook_verify_token"] == "allstreak_custom_verify_token_999"
        assert "/webhook/whatsapp" in wh_data["callback_url"]

        # Verify .env file was actually created/updated!
        env_file = get_env_path()
        assert env_file.exists()
        env_content = env_file.read_text(encoding="utf-8")
        assert "META_ACCESS_TOKEN=EAAG_TEST_TOKEN_2026" in env_content
        assert "META_PHONE_NUMBER_ID=1000999888777" in env_content
        assert "META_WABA_ID=9000888777666" in env_content
        assert "META_VERIFY_TOKEN=allstreak_custom_verify_token_999" in env_content

@pytest.mark.asyncio
async def test_start_conversation_manual_number():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start a new conversation with a manual number
        res = await ac.post("/api/v1/conversations/start", headers=headers, json={
            "phone": "919944883322",
            "name": "Kavitha Jewellers",
            "initial_message": "Hello Kavitha, thanks for connecting with us!",
            "mode": "HUMAN"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["contact"]["phone"] == "919944883322"
        assert data["contact"]["name"] == "Kavitha Jewellers"
        assert data["mode"] == "HUMAN"
        assert data["status"] == "OPEN"


