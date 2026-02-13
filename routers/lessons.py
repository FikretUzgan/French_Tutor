"""
Lesson Routes: Generate, retrieve, and list lessons
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
import json
import logging
from core.schemas import LessonResponse, LessonGenerateRequest
from services import ai_service
import db_core
import db_lessons
import db_utils
import curriculum_parser
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class LoadLessonRequest(BaseModel):
    """Request model for loading a lesson."""
    week: int = 1
    day: int = 1
    user_id: int = 1

# Level progression order
LEVEL_ORDER = [
    "A1.1", "A1.2", "A2.1", "A2.2",
    "B1.1", "B1.2", "B2.1", "B2.2"
]


def get_current_level() -> str:
    """Get the current learning level for the user."""
    level = db_core.get_app_setting("current_level")
    if level in LEVEL_ORDER:
        return level
    starting_level = db_core.get_app_setting("starting_level")
    if starting_level in LEVEL_ORDER:
        return starting_level
    return "A1.1"


def build_lesson_response(lesson: dict) -> LessonResponse:
    """Convert database lesson or curriculum lesson to API response format."""
    
    # Handle curriculum format (from curriculum_parser)
    if lesson.get('is_curriculum'):
        content = {
            "grammar": lesson.get("grammar", {}),
            "vocabulary": lesson.get("vocabulary", []),
            "speaking": lesson.get("speaking", {}),
            "homework": lesson.get("homework", {}),
            "quiz": lesson.get("quiz", {}),
        }
        # #region agent log
        try:
            from pathlib import Path as _Path
            _gram = content.get("grammar") or {}
            _exp = _gram.get("explanation") or ""
            _log = {"id": "lessons_build", "timestamp": __import__("time").time() * 1000, "location": "routers.lessons.build_lesson_response", "message": "grammar explanation in response", "data": {"len": len(_exp), "tail": _exp[-200:] if len(_exp) > 200 else _exp}, "hypothesisId": "A"}
            _logpath = _Path(__file__).resolve().parent.parent / ".cursor" / "debug.log"
            _logpath.parent.mkdir(parents=True, exist_ok=True)
            with open(_logpath, "a", encoding="utf-8") as _f:
                _f.write(__import__("json").dumps(_log, ensure_ascii=False) + "\n")
        except Exception:
            pass
        # #endregion
    else:
        # Handle database format
        content = {
            "grammar": json.loads(lesson.get("grammar_explanation", "{}")) if lesson.get("grammar_explanation") else {},
            "vocabulary": json.loads(lesson.get("vocabulary", "[]")) if lesson.get("vocabulary") else [],
            "speaking": json.loads(lesson.get("speaking_prompt", "{}")) if lesson.get("speaking_prompt") else {},
            "homework": lesson.get("homework_prompt", ""),
            "quiz": json.loads(lesson.get("quiz_questions", "{}")) if lesson.get("quiz_questions") else {},
        }

    return LessonResponse(
        lesson_id=lesson["lesson_id"],
        title=lesson.get("theme", "Untitled Lesson"),
        level=lesson.get("level", "Unknown"),
        description=f"Week {lesson.get('week_number', lesson.get('week', 'N/A'))} - {lesson.get('theme', '')}",
        content=content,
    )


@router.post("/api/lessons/load")
async def load_lesson(request: LoadLessonRequest):
    """Load lesson directly from redesigned curriculum (no AI generation)."""
    try:
        week = request.week
        day = request.day
        user_id = request.user_id
        
        logger.info(f"Loading lesson: week={week}, day={day}, user={user_id}")

        # Load lesson directly from curriculum files (NO AI)
        lesson_dict = curriculum_parser.load_redesigned_curriculum_day(
            week=week,
            day=day
        )
        
        logger.info(f"Loaded lesson from curriculum: {lesson_dict['lesson_id']}")

        # Save to database for tracking
        lesson_id = lesson_dict.get('lesson_id')
        if not lesson_id:
            raise HTTPException(status_code=500, detail="Lesson missing lesson_id")
        
        # Try to save to DB (but don't fail if it doesn't work)
        try:
            db_utils.store_generated_lesson(
                user_id=user_id,
                lesson_id=lesson_id,
                week=week,
                day=day,
                curriculum_file=f'Week_{week}_{lesson_dict["level"]}.md',
                status='loaded',
                api_duration_seconds=0
            )
        except Exception as db_err:
            logger.warning(f"Failed to log lesson load to history: {db_err}")
        
        # Try to save lesson content to lessons table
        try:
            db_lessons.save_lesson(
                lesson_id=lesson_dict.get('lesson_id'),
                level=lesson_dict.get('level', 'Unknown'),
                theme=lesson_dict.get('theme', 'Unknown'),
                week_number=lesson_dict.get('week', 0),
                grammar_explanation=json.dumps(lesson_dict.get('grammar', {})),
                vocabulary=json.dumps(lesson_dict.get('vocabulary', [])),
                speaking_prompt=json.dumps(lesson_dict.get('speaking', {})),
                homework_prompt=json.dumps(lesson_dict.get('homework', {})),
                quiz_questions=json.dumps(lesson_dict.get('quiz', {}))
            )
            logger.info(f"Saved lesson {lesson_id} to database")
        except Exception as save_err:
            logger.warning(f"Failed to save lesson to DB: {save_err}")
        
        # Retrieve from DB to ensure we have consistent formatting
        saved_lesson = db_lessons.get_lesson_by_id(lesson_id)
        
        if saved_lesson:
            lesson_response = build_lesson_response(saved_lesson)
        else:
            # If not in DB, use the loaded lesson directly
            lesson_response = build_lesson_response(lesson_dict)
        
        return {
            "success": True,
            "lesson": lesson_response.dict(),
            "is_new": True,
            "source": "curriculum"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lesson loading failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/lessons/generate", response_model=LessonResponse)
async def generate_lesson_endpoint(request: LessonGenerateRequest):
    """Generate a lesson using AI Service."""
    try:
        user_id = request.user_id or 1
        level = request.student_level or get_current_level()

        # Use AI Service to generate lesson
        lesson_dict, is_new = ai_service.generate_lesson_from_curriculum(
            week_number=request.week,
            day_number=request.day,
            student_level=level,
            user_id=user_id
        )

        # Retrieve the saved lesson from database
        lesson_id = lesson_dict.get('lesson_id')
        saved_lesson = db_lessons.get_lesson_by_id(lesson_id)

        if not saved_lesson:
            raise HTTPException(status_code=500, detail="Lesson generated but could not be retrieved")

        return build_lesson_response(saved_lesson)

    except Exception as e:
        logger.error(f"Lesson generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str):
    """Retrieve a specific lesson by ID."""
    try:
        lesson = db_lessons.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return build_lesson_response(lesson)
    except Exception as e:
        logger.error(f"Failed to retrieve lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lessons", response_model=List[Dict[str, Any]])
async def list_lessons():
    """List available lessons optimized for UI."""
    try:
        return db_lessons.get_available_lessons_for_ui()
    except Exception as e:
        logger.error(f"Failed to list lessons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lessons/available-weeks")
async def get_available_weeks():
    """Get list of available curriculum weeks from redesigned curriculum."""
    try:
        from pathlib import Path
        curriculum_dir = Path(__file__).parent.parent / "Research" / "NEW_CURRICULUM_REDESIGNED"
        
        available_weeks = {}
        for week_num in range(1, 53):
            for level in ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2.1", "B2.2"]:
                filename = f"Week_{week_num}_{level}.md"
                filepath = curriculum_dir / filename
                if filepath.exists():
                    available_weeks[week_num] = level
                    break
        
        return {
            "success": True,
            "available_weeks": sorted(available_weeks.keys()),
            "total_weeks": len(available_weeks),
            "weeks_map": available_weeks
        }
    except Exception as e:
        logger.error(f"Failed to get available weeks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lessons/selection-ui")
async def get_lessons_for_selection_ui(user_id: int = 1):
    """Get lessons in format suitable for UI selection dropdown."""
    try:
        weeks = await get_available_weeks()
        return {
            "weeks": weeks['weeks_map'],
            "days_per_week": 5,
            "total_content": f"{len(weeks['weeks_map'])} weeks available"
        }
    except Exception as e:
        logger.error(f"Failed to get lessons for UI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/lessons/{lesson_id}/start")
async def start_lesson(lesson_id: str, user_id: int = 1):
    """Mark lesson as started when user opens it."""
    try:
        db_lessons.mark_lesson_started(lesson_id, user_id)
        return {
            "success": True,
            "lesson_id": lesson_id,
            "message": "Lesson started"
        }
    except Exception as e:
        logger.error(f"Failed to start lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/lessons/history")
async def get_lesson_generation_history(user_id: int = 1, limit: int = 20):
    """Get lesson generation history for a student."""
    try:
        history = db_utils.get_lesson_generation_history(user_id=user_id, limit=limit)
        return {
            "success": True,
            "user_id": user_id,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/lessons/{lesson_id}/schedule-srs")
async def schedule_lesson_srs(lesson_id: str, user_id: int = 1):
    """Schedule vocabulary from a lesson for SRS review."""
    try:
        import db_srs
        count = db_srs.schedule_lesson_vocabulary(
            lesson_id=lesson_id,
            vocabulary_count=3,
            user_id=user_id
        )
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "srs_items_created": count,
            "message": f"Scheduled {count} vocabulary items for spaced repetition"
        }
    except Exception as e:
        logger.error(f"Failed to schedule SRS: {e}")
        raise HTTPException(status_code=500, detail=str(e))
