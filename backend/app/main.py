import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .middleware.error_handler import GlobalErrorMiddleware
from .api.routes import billing

# ── Routers existentes ────────────────────────
from .api.routes import (
    auth,
    account,
    sessions,
    operations,
    reports,
    projections,
    goals,
    withdrawals,
    goal_reports,
    admin
)
# Routers del módulo Goals
from .api.routes import goals, withdrawals, goal_reports

# ── Logging básico ────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── App ───────────────────────────────────────
app = FastAPI(
    title="Binary Options Capital Manager",
    version="1.1.0",
    description="API — Capital Manager SaaS",
)

# ── CORS RESTRICTIVO ──────────────────────────
# Solo los orígenes en CORS_ORIGINS (.env) son permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# ── Middleware de errores globales ────────────
# Captura HTTPException y Exception → JSON uniforme
app.add_middleware(GlobalErrorMiddleware)

# ── Routers ───────────────────────────────────
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(sessions.router)
app.include_router(operations.router)
app.include_router(reports.router)
app.include_router(projections.router)
app.include_router(goals.router)
app.include_router(withdrawals.router)
app.include_router(goal_reports.router)
app.include_router(admin.router)
app.include_router(billing.router)

# ── Health / Root ─────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Binary Options Capital Manager API", "version": "1.1.0"}


@app.get("/health")
def health():
    """Endpoint de salud para load-balancers."""
    return {"status": "ok"}