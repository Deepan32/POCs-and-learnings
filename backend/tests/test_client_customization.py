import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_client_setup_overview_and_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Overview
        res = await ac.get("/api/v1/client-setup/overview", headers=headers)
        assert res.status_code == 200
        overview = res.json()
        assert "workspace_id" in overview
        assert "name" in overview
        assert "primary_color" in overview

        # 2. Update Profile
        up_res = await ac.put("/api/v1/client-setup/profile", headers=headers, json={
            "phone": "+91 98765 43210",
            "city": "Bengaluru",
            "description": "Wings Flower flagship boutique"
        })
        assert up_res.status_code == 200

        # 3. Update Branding
        brand_res = await ac.put("/api/v1/client-setup/branding", headers=headers, json={
            "primary_color": "#E11D48",
            "button_style": "pill"
        })
        assert brand_res.status_code == 200

@pytest.mark.asyncio
async def test_product_catalog_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create
        create_res = await ac.post("/api/v1/client-setup/products", headers=headers, json={
            "name": "Red Velvet Rose Bouquet",
            "category": "Flowers",
            "price": 1299.0,
            "currency": "INR",
            "sku": "WF-ROSE-01"
        })
        assert create_res.status_code == 200
        prod = create_res.json()
        prod_id = prod["id"]
        assert prod["name"] == "Red Velvet Rose Bouquet"

        # List
        list_res = await ac.get("/api/v1/client-setup/products", headers=headers)
        assert list_res.status_code == 200
        assert any(p["id"] == prod_id for p in list_res.json())

        # Update
        update_res = await ac.put(f"/api/v1/client-setup/products/{prod_id}", headers=headers, json={
            "price": 1499.0
        })
        assert update_res.status_code == 200
        assert update_res.json()["price"] == 1499.0

        # Delete
        del_res = await ac.delete(f"/api/v1/client-setup/products/{prod_id}", headers=headers)
        assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_quick_replies_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create
        create_res = await ac.post("/api/v1/client-setup/quick-replies", headers=headers, json={
            "shortcut": "/timing",
            "title": "Store Hours",
            "message": "We are open 9am to 9pm daily!",
            "category": "Hours"
        })
        assert create_res.status_code == 200
        qr = create_res.json()
        qr_id = qr["id"]
        assert qr["shortcut"] == "/timing"

        # List
        list_res = await ac.get("/api/v1/client-setup/quick-replies", headers=headers)
        assert list_res.status_code == 200
        assert any(r["id"] == qr_id for r in list_res.json())

        # Delete
        del_res = await ac.delete(f"/api/v1/client-setup/quick-replies/{qr_id}", headers=headers)
        assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_industry_templates_and_apply():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List templates
        tpl_res = await ac.get("/api/v1/client-setup/templates", headers=headers)
        assert tpl_res.status_code == 200
        templates = tpl_res.json()
        assert len(templates) >= 8
        assert any(t["id"] == "florist-wings-flower" for t in templates)

        # Apply template
        apply_res = await ac.post("/api/v1/client-setup/templates/florist-wings-flower/apply", headers=headers)
        assert apply_res.status_code == 200
        data = apply_res.json()
        assert data["products_added"] > 0
        assert data["quick_replies_added"] > 0

@pytest.mark.asyncio
async def test_client_clone_engine():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        clone_res = await ac.post("/api/v1/client-setup/clone", headers=headers, json={
            "target_name": "Wings Flower - Indiranagar Branch",
            "industry": "Florist",
            "copy_branding": True,
            "copy_products": True,
            "copy_quick_replies": True,
            "copy_flows": True
        })
        assert clone_res.status_code == 200
        cloned = clone_res.json()
        assert "new_workspace_id" in cloned
        assert cloned["new_workspace_name"] == "Wings Flower - Indiranagar Branch"
        assert cloned["copied_items"]["products"] >= 0

@pytest.mark.asyncio
async def test_debugger_and_simulation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@allstreak.com",
            "password": "Allstreak@2026"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Traces
        traces_res = await ac.get("/api/v1/debugger/traces", headers=headers)
        assert traces_res.status_code == 200

        # Simulate webhook pipeline
        sim_res = await ac.post("/api/v1/debugger/simulate-webhook", headers=headers, json={
            "sender_phone": "919988776655",
            "message_text": "What is the price of bouquet?",
            "sender_name": "Rahul Verma"
        })
        assert sim_res.status_code == 200
        sim_data = sim_res.json()
        assert sim_data["status"] == "SIMULATION_SUCCESS"
        assert "trace" in sim_data
