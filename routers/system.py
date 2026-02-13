"""
System Routes: Health checks, settings, and first-time setup
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from core.schemas import ModeToggleRequest, FirstTimeSetupRequest
import db_core
import db_utils
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# CEFR level progression
LEVEL_ORDER = [
    "A1.1", "A1.2", "A2.1", "A2.2",
    "B1.1", "B1.2", "B2.1", "B2.2"
]


def get_dev_mode() -> bool:
    """Check if dev mode is enabled."""
    return db_core.get_app_setting("dev_mode", "false") == "true"


@router.get("/")
async def root():
    """Root endpoint - Serve the index.html."""
    return FileResponse("templates/index.html", media_type="text/html")


@router.get("/api/health")
async def health_check():
    """Check API and database health."""
    api_key_loaded = os.getenv("GEMINI_API_KEY") is not None
    return {
        "status": "ok",
        "database": "connected",
        "api_key_loaded": api_key_loaded,
        "message": "API running"
    }


@router.get("/api/mode")
async def get_app_mode():
    """Get current application mode and user setup state."""
    dev_mode = get_dev_mode()
    starting_level = db_core.get_app_setting("starting_level")
    current_level = db_core.get_app_setting("current_level")
    homework_blocking = db_core.get_app_setting("homework_blocking_enabled", "true") == "true"
    return {
        "mode": "dev" if dev_mode else "production",
        "starting_level": starting_level,
        "current_level": current_level,
        "homework_blocking_enabled": homework_blocking
    }


@router.post("/api/mode/toggle")
async def toggle_app_mode(request: ModeToggleRequest):
    """Toggle development mode on or off."""
    db_core.set_app_setting("dev_mode", "true" if request.dev_mode else "false")
    return {
        "status": "success",
        "mode": "dev" if request.dev_mode else "production"
    }


@router.post("/api/settings/mode")
async def toggle_mode(request: ModeToggleRequest):
    """Toggle development mode (alias for /api/mode/toggle)."""
    return await toggle_app_mode(request)


@router.post("/api/settings/homework-blocking")
async def toggle_homework_blocking(enabled: bool = True):
    """Toggle homework blocking on or off.
    
    Args:
        enabled: True to enable blocking (production mode), False to disable (dev mode)
    
    When disabled, all lessons are accessible regardless of homework completion.
    When enabled, next lesson is blocked until current homework is submitted and passed.
    """
    db_core.set_app_setting("homework_blocking_enabled", "true" if enabled else "false")
    return {
        "status": "success",
        "homework_blocking_enabled": enabled,
        "message": "Homework blocking " + ("enabled" if enabled else "disabled")
    }


@router.get("/api/curriculum/plan")
async def get_curriculum_plan():
    """Return the curriculum plan markdown."""
    plan_path = Path(__file__).parent.parent / "French_Course_Weekly_Plan.md"
    if not plan_path.exists():
        raise HTTPException(status_code=404, detail="Curriculum plan not found")
    return {"plan": plan_path.read_text(encoding="utf-8")}


@router.post("/api/setup/first-time")
async def first_time_setup(request: FirstTimeSetupRequest):
    """Initial user setup with starting level selection."""
    try:
        if request.starting_level not in LEVEL_ORDER:
            raise HTTPException(status_code=400, detail="Invalid starting level")
        
        db_core.set_app_setting("starting_level", request.starting_level)
        db_core.set_app_setting("current_level", request.starting_level)
        db_core.set_app_setting("setup_completed", "true")
        
        # Initialize student profile
        db_utils.update_student_level(1, request.starting_level)
        
        return {
            "status": "success",
            "starting_level": request.starting_level,
            "current_level": db_core.get_app_setting("current_level")
        }
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
