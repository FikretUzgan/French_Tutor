"""
French Tutor - FastAPI Backend
High-performance web application for French language learning
Refactored to use modular architecture (Routers, Services, Core)
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Database
import db_core

# Routers
from routers import (
    system_router,
    lessons_router,
    speaking_router,
    homework_router,
    vocabulary_router,
    srs_router,
    exams_router
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="French Tutor API",
    description="Fast French language learning platform with AI tutoring",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Routers Registration
# ============================================================================

# System routes (health, settings, setup)
app.include_router(system_router)

# Lesson routes (generate, retrieve, list)
app.include_router(lessons_router)

# Speaking routes (feedback, transcription, TTS)
app.include_router(speaking_router)

# Homework routes (submission, grading)
app.include_router(homework_router)

# Vocabulary routes (learning management)
app.include_router(vocabulary_router)

# SRS routes (spaced repetition system)
app.include_router(srs_router)

# Exam routes (assessment)
app.include_router(exams_router)


# ============================================================================
# Static Files & Frontend
# ============================================================================

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info("French Tutor API starting...")
    
    # Initialize database
    try:
        db_core.init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
    
    # Check if Gemini API key is configured
    if not os.getenv('GEMINI_API_KEY'):
        logger.warning("⚠️  GEMINI_API_KEY environment variable not set. AI features will fail gracefully.")
    else:
        logger.info("✅ GEMINI_API_KEY is configured")
    
    # Load Whisper model in background if needed
    # audio_service.load_whisper_model()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
