"""
Homework Routes: Submission and grading
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import db_homework
import db_utils
import db_lessons
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class HomeworkSubmitRequest(BaseModel):
    """Request model for homework submission."""
    lesson_id: str
    homework_text: str
    user_id: Optional[int] = 1


class HomeworkCheckRequest(BaseModel):
    """Request model for homework check."""
    lesson_id: str
    homework_text: str
    user_id: Optional[int] = 1


@router.post("/api/homework/submit")
async def submit_homework(request: HomeworkSubmitRequest):
    """Submit homework for a lesson."""
    try:
        submission_id = db_homework.save_homework_submission(
            lesson_id=request.lesson_id,
            text_content=request.homework_text,
            user_id=request.user_id
        )

        # Get feedback from AI (async would be better but synchronous for now)
        feedback = db_homework.get_homework_feedback(
            homework_text=request.homework_text,
            lesson_id=request.lesson_id
        )
        
        return {
            "status": "submitted",
            "submission_id": submission_id,
            "lesson_id": request.lesson_id,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
            "message": "Homework submitted successfully"
        }

    except Exception as e:
        logger.error(f"Homework submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/homework/status/{lesson_id}")
async def get_homework_status(lesson_id: str, user_id: int = 1):
    """Get submission status for a lesson's homework."""
    try:
        submission = db_homework.get_submission_by_lesson(
            lesson_id=lesson_id,
            user_id=user_id
        )
        
        if not submission:
            return {
                "lesson_id": lesson_id,
                "user_id": user_id,
                "status": "not_submitted",
                "message": "No homework submitted for this lesson"
            }
        
        return {
            "lesson_id": lesson_id,
            "user_id": user_id,
            "status": "submitted",
            "submission_id": submission.get("submission_id"),
            "submitted_at": submission.get("submitted_at"),
            "feedback": submission.get("feedback"),
            "grade": submission.get("grade")
        }
    except Exception as e:
        logger.error(f"Failed to get homework status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/homework/history")
async def get_homework_history(user_id: int = 1, limit: int = 50):
    """Get all submitted homework for a user."""
    try:
        submissions = db_homework.get_user_submissions(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "total_submissions": len(submissions),
            "submissions": submissions,
            "message": f"{len(submissions)} homework submissions found"
        }
    except Exception as e:
        logger.error(f"Failed to get homework history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/homework/pending")
async def get_pending_homework(user_id: int = 1):
    """Get lessons that have pending homework."""
    try:
        lessons = db_lessons.get_lessons(user_id=user_id)
        pending = []
        
        for lesson in lessons:
            submission = db_homework.get_submission_by_lesson(
                lesson_id=lesson.get("lesson_id"),
                user_id=user_id
            )
            if not submission:
                pending.append(lesson)
        
        return {
            "user_id": user_id,
            "pending_count": len(pending),
            "pending_lessons": pending,
            "message": f"{len(pending)} lessons with pending homework"
        }
    except Exception as e:
        logger.error(f"Failed to get pending homework: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/homework/check")
async def check_homework(request: HomeworkCheckRequest):
    """Check homework content for errors and improvements (AI feedback)."""
    try:
        # Get AI feedback on the homework
        feedback = db_homework.get_homework_feedback(
            homework_text=request.homework_text,
            lesson_id=request.lesson_id
        )
        
        return {
            "user_id": request.user_id,
            "lesson_id": request.lesson_id,
            "feedback": feedback,
            "suggestions": feedback.get("suggestions", []),
            "corrections": feedback.get("corrections", []),
            "overall_assessment": feedback.get("overall_assessment", "Good effort!"),
            "message": "Homework checked successfully"
        }
    except Exception as e:
        logger.error(f"Failed to check homework: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/homework/stats")
async def get_homework_stats(user_id: int = 1):
    """Get homework completion statistics for a user."""
    try:
        submissions = db_homework.get_user_submissions(user_id=user_id, limit=1000)
        lessons = db_lessons.get_lessons(user_id=user_id)
        
        stats = {
            "user_id": user_id,
            "total_lessons": len(lessons),
            "submitted": len(submissions),
            "pending": len(lessons) - len(submissions),
            "completion_rate": round((len(submissions) / len(lessons) * 100) if lessons else 0, 2),
            "average_grade": db_utils.calculate_average([s.get("grade", 0) for s in submissions]) if submissions else 0
        }
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get homework stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

