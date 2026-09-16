# ALLSTREAK — Production-Grade WhatsApp Automation SaaS

> **Tagline**: *"Automate. Engage. Convert."*  
> A scalable, multi-tenant B2B SaaS platform combining **Meta WhatsApp Cloud API v21.0**, **Visual Workflow Builder**, **WhatsApp-Grade Team Inbox**, **Human Handover Engine**, **Lead CRM with Automated Scoring**, and **AI Agent with RAG Knowledge Base**.

---

## Key Features

1. **Meta WhatsApp Cloud API v21.0 Abstraction**:
   - Direct Graph API calls with signed payloads and media support.
   - Strict enforcement of Meta's **24-hour customer service window** (blocks free-form outbound texts outside 24h window and requires Meta-approved templates).
   - HMAC SHA-256 signature verification (`X-Hub-Signature-256`) and idempotency via unique Meta `message_id`.
   - Sandbox / Simulation mode provider for local zero-config testing.

2. **Visual Workflow Builder (React Flow)**:
   - Drag-and-drop canvas supporting custom Trigger, Condition, Action, and Human Handover nodes.
   - Built-in **Flow Simulation Runner**: test customer responses ("Hi", "pricing", "talk to human") without sending real WhatsApp messages.

3. **No-Code Rule Builder & Priority Engine**:
   - Clean WHEN / IF / THEN / AND rules.
   - Priority engine (P1: Human escalation, P2: Pricing support, P3: General greeting). Suppresses conflicting automation replies.
   - Loop protection guards (prevents bot replying to outbound messages, max execution depth).

4. **Team Inbox & Human Handover Engine**:
   - 3-Pane WhatsApp layout: Filter tabs, chat thread with delivery receipts (`sent`, `delivered`, `read`), 24h window timer banner, smart composer with template picker and button chips.
   - Dynamic mode switching: `BOT` ↔ `AI` ↔ `HUMAN`.
   - "Take Over as Human" stops automation immediately and routes to agent queue. "Return to Automation" safely resumes bot/AI flows.

5. **Lead CRM & Dynamic Lead Scoring (0-100)**:
   - Full Kanban pipeline (`NEW`, `CONTACTED`, `QUALIFIED`, `PROPOSAL`, `NEGOTIATION`, `CONVERTED`, `LOST`) with drag-and-drop stage updates.
   - Dynamic scoring engine based on keyword intent, interactive buttons, and human requests (+10, +20, +25, +15).

6. **Interactive WhatsApp Phone Simulator**:
   - Built directly into the dashboard UI!
   - Test incoming messages, interactive quick-reply buttons, and human handover transitions in a realistic mobile mockup.

7. **Multi-Tenant Architecture & RBAC**:
   - Complete tenant data isolation with indexed `workspace_id`.
   - Owner, Admin, and Agent roles with permission guards.
   - JWT access & refresh token rotation with bcrypt password hashing.

---

## Architecture Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), SQLite / PostgreSQL switchable, Alembic, WebSockets.
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, React Flow, Lucide Icons.
- **Infrastructure**: Docker & Docker Compose (PostgreSQL 16, Redis 7, Backend, Frontend).

---

## Quick Start (Local Run)

### 1. Backend Setup
```bash
# Navigate to project root
pip install -r backend/requirements.txt

# Run backend with auto-seeding (SQLite by default)
python -m uvicorn backend.app.main:app --reload --port 8000
```
- Swagger API Docs: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Open Web App: `http://localhost:3000`

---

## Pre-Seeded Demo Credentials

The database automatically initializes with a complete demo workspace (`ALLSTREAK Demo`), active conversation threads, leads across Kanban stages, templates, and automations:

| Role | Email | Password | Access |
|---|---|---|---|
| **Owner** | `admin@allstreak.com` | `Allstreak@2026` | Full platform access, flows, billing, team |
| **Senior Agent** | `agent@allstreak.com` | `Allstreak@2026` | Team inbox, human handover, leads CRM |

---

## Automated Pytest Suite

Run all automated unit and integration tests:
```bash
python -m pytest backend/tests -v
```
Verified test coverage:
- `test_root`: API health status
- `test_auth_login`: JWT token generation
- `test_webhook_verification`: Meta `hub.challenge` handshake
- `test_webhook_invalid_verification`: Rejection of unauthorized tokens
- `test_dashboard_metrics`: KPI telemetry aggregation
- `test_flow_simulation_runner`: Dry-run execution simulation
- `test_lead_kanban_and_stage_update`: Pipeline stage progression
- `test_sandbox_simulator_endpoint`: Ingestion and automated reply

---

## Production Docker Stack

To launch the full containerized production stack (FastAPI + Next.js + PostgreSQL 16 + Redis 7):
```bash
docker-compose up --build -d
```
Allstreak services will run on:
- Web App: `http://localhost:3000`
- API Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
