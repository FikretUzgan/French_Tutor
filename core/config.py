import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "French Tutor API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATE_DIR: Path = BASE_DIR / "templates"
    SUBMISSIONS_DIR: Path = BASE_DIR / "submissions"
    AUDIO_DIR: Path = SUBMISSIONS_DIR / "audio"
    TTS_DIR: Path = SUBMISSIONS_DIR / "tts"

    # Database
    DB_NAME: str = "french_tutor.db"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # App Settings
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()

# Ensure directories exist
settings.STATIC_DIR.mkdir(exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
settings.TTS_DIR.mkdir(parents=True, exist_ok=True)
