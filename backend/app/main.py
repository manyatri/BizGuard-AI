from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db

# Phase 1 routers
from app.api.v1 import catalog, orders, workflows

# Phase 2 — Bug Detection & Simulation
from app.api.v1 import bug_detection, simulation

# Phase 3 — Recovery & Approvals
from app.api.v1 import recovery, approvals

# Phase 4 — Analytics, War Room, Extended Inventory, Shipments, Returns
from app.api.v1 import analytics, war_room, inventory_extended, shipments, returns

# Switch Integration
from app.api.v1 import switch_integration

# WebSocket
from app.api.v1 import websocket as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all database tables on startup
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "BizGuard AI — Autonomous Business Reliability and Recovery Platform "
        "for Clothing E-Commerce. Detects, investigates and recovers from business "
        "logic incidents using multi-agent AI coordination."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Next.js dev server and any localhost origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Phase 1 — Core business operations
# ---------------------------------------------------------------------------
app.include_router(catalog.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(workflows.router, prefix=settings.API_V1_STR)

# ---------------------------------------------------------------------------
# Phase 2 — Bug detection & simulation
# ---------------------------------------------------------------------------
app.include_router(bug_detection.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)

# ---------------------------------------------------------------------------
# Phase 3 — Recovery engine & human approvals
# ---------------------------------------------------------------------------
app.include_router(recovery.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)

# ---------------------------------------------------------------------------
# Phase 4 — Analytics, AI War Room, Extended modules
# ---------------------------------------------------------------------------
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(war_room.router, prefix=settings.API_V1_STR)
app.include_router(inventory_extended.router, prefix=settings.API_V1_STR)
app.include_router(shipments.router, prefix=settings.API_V1_STR)
app.include_router(returns.router, prefix=settings.API_V1_STR)
app.include_router(switch_integration.router, prefix=settings.API_V1_STR)

# ---------------------------------------------------------------------------
# WebSocket — real-time streaming (no prefix, served at root)
# ---------------------------------------------------------------------------
app.include_router(ws_router.router)


# ---------------------------------------------------------------------------
# Root endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "domain": "Clothing E-Commerce Reliability & Recovery",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "api_v1_docs": "/docs",
        "api_v1_redoc": "/redoc",
        "switch_bus": settings.SWITCH_BUS_URL,
        "modules": [
            "catalog", "orders", "workflows",
            "bugs", "simulation",
            "recovery", "approvals",
            "analytics", "war-room", "inventory", "shipments", "returns",
            "switch"
        ],
        "websockets": ["/ws/workflow/{execution_id}", "/ws/incidents/live"],
    }


@app.get("/health")
async def health():
    from app.core.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "CONNECTED"
    except Exception as e:
        db_status = f"ERROR: {e}"
    finally:
        db.close()
    return {
        "status": "HEALTHY",
        "database": db_status,
        "api_version": "v1",
    }
