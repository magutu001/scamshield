from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import FRONTEND_DIR
from app.database import init_db
from app.routes.auth_routes import router as auth_router
from app.routes.analysis_routes import router as analysis_router
from app.routes.admin_routes import router as admin_router

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(title="Job Scam Detection System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(admin_router)

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()

# ── Serve frontend ─────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/admin-login")
def serve_admin_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin-login.html"))

@app.get("/admin-panel")
def serve_admin_panel():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin-panel.html"))

@app.get("/{path:path}")
def serve_pages(path: str):
    fp = os.path.join(FRONTEND_DIR, path)
    return FileResponse(fp) if os.path.isfile(fp) else FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
