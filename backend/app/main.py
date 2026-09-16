import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.api.v1.router import api_router
from backend.app.api.webhook import whatsapp as webhook_whatsapp
from backend.app.core.websocket_manager import ws_manager
from backend.app.seed.seed_data import seed_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("allstreak.main")

def _sync_migrate_db(sync_conn):
    try:
        from sqlalchemy import text
        dialect = sync_conn.dialect.name
        if dialect == "sqlite":
            res = sync_conn.execute(text("PRAGMA table_info(workspaces)"))
            existing_cols = {row[1] for row in res.fetchall()}
            cols = [
                ("phone", "VARCHAR(50)"),
                ("email", "VARCHAR(100)"),
                ("website", "VARCHAR(255)"),
                ("address", "TEXT"),
                ("city", "VARCHAR(100)"),
                ("instagram", "VARCHAR(100)"),
                ("facebook", "VARCHAR(100)"),
                ("description", "TEXT"),
                ("logo_url", "VARCHAR(500)"),
                ("primary_color", "VARCHAR(20) DEFAULT '#25D366'"),
                ("secondary_color", "VARCHAR(20) DEFAULT '#128C7E'"),
                ("background_color", "VARCHAR(20) DEFAULT '#0B141A'"),
                ("text_color", "VARCHAR(20) DEFAULT '#E9EDEF'"),
                ("button_style", "VARCHAR(50) DEFAULT 'rounded'"),
            ]
            for col_name, col_type in cols:
                if col_name not in existing_cols:
                    sync_conn.execute(text(f"ALTER TABLE workspaces ADD COLUMN {col_name} {col_type}"))
    except Exception as err:
        logger.warning(f"Schema migration notice: {err}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ALLSTREAK database and models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_sync_migrate_db)

    # Automatically seed demo workspace and initial data on startup
    if settings.DEMO_MODE_ENABLED:
        try:
            await seed_database()
        except Exception as e:
            logger.error(f"Error during auto-seeding: {e}")

    logger.info(f"ALLSTREAK Backend initialized successfully in {settings.ENVIRONMENT} mode.")
    yield
    logger.info("Shutting down ALLSTREAK Backend...")
    await engine.dispose()

app = FastAPI(
    title="ALLSTREAK API",
    description="Production-Grade WhatsApp Automation & AI SaaS Backend API. Automate. Engage. Convert.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits all for development & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Meta Webhook Gateway
app.include_router(webhook_whatsapp.router, prefix="/webhook", tags=["Meta WhatsApp Webhook"])

# Mount REST API v1
app.include_router(api_router, prefix="/api/v1")

# WebSocket Realtime Gateway
@app.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await ws_manager.connect(websocket, workspace_id)
    try:
        while True:
            # Keep-alive ping / pong or client message reception
            data = await websocket.receive_text()
            # Echo heartbeat if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, workspace_id)
    except Exception as e:
        logger.warning(f"WebSocket connection error: {e}")
        ws_manager.disconnect(websocket, workspace_id)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }
