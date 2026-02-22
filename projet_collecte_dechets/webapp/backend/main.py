"""
CyberCollect – FastAPI Backend
Serves both the REST API for all 5 optimization levels and the static frontend.
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Make the project root importable so level modules resolve correctly
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from webapp.backend.api import level1, level2, level3, level4, level5, chat

app = FastAPI(title="CyberCollect API", version="1.0.0")

# CORS – allow all origins so the SPA can call the API regardless of port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers
app.include_router(level1.router, prefix="/api/level1", tags=["Level 1 – Road Graph"])
app.include_router(level2.router, prefix="/api/level2", tags=["Level 2 – Truck Assignment"])
app.include_router(level3.router, prefix="/api/level3", tags=["Level 3 – Weekly Schedule"])
app.include_router(level4.router, prefix="/api/level4", tags=["Level 4 – VRP Optimization"])
app.include_router(level5.router, prefix="/api/level5", tags=["Level 5 – Real-time Simulation"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])


@app.get("/health")
def health():
    return {"status": "online", "version": "1.0.0"}


# Serve the static frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        target = FRONTEND_DIR / full_path
        if target.exists() and target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
