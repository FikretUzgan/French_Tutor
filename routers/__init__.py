"""
API Routers Package

Imports all router modules for main.py to include.
"""

from .system import router as system_router
from .lessons import router as lessons_router
from .speaking import router as speaking_router
from .homework import router as homework_router
from .vocabulary import router as vocabulary_router
from .srs import router as srs_router
from .exams import router as exams_router

__all__ = [
    "system_router",
    "lessons_router",
    "speaking_router",
    "homework_router",
    "vocabulary_router",
    "srs_router",
    "exams_router",
]
