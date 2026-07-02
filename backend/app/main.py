from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.controllers import (
    cup_controller,
    history_controller,
    league_controller,
    match_controller,
    player_controller,
)
from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.models import models
from backend.app.services.league_simulation import ensure_league_teams
from backend.app.db.database import SessionLocal


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
project_dir = Path(__file__).resolve().parents[2]
assets_dir = project_dir / "assets"
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

_ = models
app.include_router(match_controller.router, prefix=settings.api_prefix)
app.include_router(player_controller.router, prefix=settings.api_prefix)
app.include_router(history_controller.router, prefix=settings.api_prefix)
app.include_router(league_controller.router, prefix=settings.api_prefix)
app.include_router(cup_controller.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        ensure_league_teams(db)
        db.commit()
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(project_dir / "index.html")


@app.get(f"{settings.api_prefix}/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "database": "configured",
    }
