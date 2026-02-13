"""
Exam Routes: Assessment and exam generation
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import db_exams
import db_utils
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ExamGenerateRequest(BaseModel):
    """Request model for exam generation."""
    level: str  # A1.1, A1.2, A2.1, B1.1, etc.
    topics: Optional[List[str]] = None
    num_questions: int = 20
    user_id: Optional[int] = 1


class ExamSubmitRequest(BaseModel):
    """Request model for exam submission."""
    exam_id: str
    answers: dict  # question_id -> answer
    user_id: Optional[int] = 1


@router.post("/api/exam/generate")
async def generate_exam(request: ExamGenerateRequest):
    """Generate a new exam for a user at a specific level."""
    try:
        # Generate exam with questions
        exam = db_exams.generate_exam(
            level=request.level,
            topics=request.topics or [],
            num_questions=request.num_questions,
            user_id=request.user_id
        )
        
        if not exam:
            raise HTTPException(status_code=500, detail="Failed to generate exam")
        
        return {
            "success": True,
            "exam_id": exam.get("exam_id"),
            "level": exam.get("level"),
            "num_questions": len(exam.get("questions", [])),
            "questions": exam.get("questions", []),
            "message": f"Exam generated with {len(exam.get('questions', []))} questions"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate exam: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/exam/submit")
async def submit_exam(request: ExamSubmitRequest):
    """Submit completed exam responses and get grading."""
    try:
        # Get exam details
        exam = db_exams.get_exam(request.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Grade the exam
        grading_result = db_exams.grade_exam(
            exam_id=request.exam_id,
            answers=request.answers,
            user_id=request.user_id
        )
        
        # Save exam result
        result = db_exams.save_exam_result(
            exam_id=request.exam_id,
            user_id=request.user_id,
            answers=request.answers,
            grading_result=grading_result
        )
        
        return {
            "success": True,
            "exam_id": request.exam_id,
            "score": grading_result.get("score"),
            "percentage": grading_result.get("percentage"),
            "passed": grading_result.get("passed"),
            "details": grading_result.get("details"),
            "message": f"Exam graded: {grading_result.get('percentage')}%"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit exam: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/exam/results")
async def get_exam_results(user_id: int = 1):
    """Get all exam results for a user."""
    try:
        results = db_exams.get_exam_results(user_id=user_id)
        return {
            "user_id": user_id,
            "results": results,
            "total_exams": len(results),
            "average_score": db_utils.calculate_average([r.get("percentage", 0) for r in results]) if results else 0
        }
    except Exception as e:
        logger.error(f"Failed to get exam results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
