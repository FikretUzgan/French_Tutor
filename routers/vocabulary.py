"""
Vocabulary Routes: Vocabulary management and learning
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import db_srs
import db_utils
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class VocabularyCheckRequest(BaseModel):
    """Request model for vocabulary check."""
    word_id: int
    user_answer: str
    user_id: Optional[int] = 1


class VocabularyPracticeRequest(BaseModel):
    """Request model for vocabulary practice session."""
    lesson_id: Optional[str] = None
    mode: str = "daily"  # daily, review, challenge
    user_id: Optional[int] = 1


@router.get("/api/vocabulary")
async def list_vocabulary(user_id: int = 1):
    """List vocabulary learned by user."""
    try:
        words = db_srs.get_learned_vocabulary(user_id=user_id)
        return {
            "user_id": user_id,
            "total_learned": len(words),
            "words": words
        }
    except Exception as e:
        logger.error(f"Failed to get vocabulary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vocabulary/practice")
async def get_vocabulary_practice(
    lesson_id: Optional[str] = None,
    mode: str = "daily",
    user_id: int = 1
):
    """Get vocabulary practice words (daily/review/challenge)."""
    try:
        # Get practice vocabulary based on mode
        if mode == "daily":
            words = db_srs.get_daily_vocabulary(user_id=user_id)
        elif mode == "review":
            words = db_srs.get_srs_due(user_id=user_id, limit=20)
        elif mode == "challenge":
            words = db_srs.get_challenging_vocabulary(user_id=user_id)
        else:
            words = db_srs.get_daily_vocabulary(user_id=user_id)
        
        return {
            "user_id": user_id,
            "mode": mode,
            "lesson_id": lesson_id,
            "words_count": len(words),
            "words": words,
            "message": f"{len(words)} vocabulary items ready for {mode} practice"
        }
    except Exception as e:
        logger.error(f"Failed to get vocabulary practice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/vocabulary/check")
async def check_vocabulary(request: VocabularyCheckRequest):
    """Check user's vocabulary answer and return feedback."""
    try:
        # Get the word from vocabulary
        word_info = db_srs.get_vocabulary_by_id(request.word_id)
        if not word_info:
            raise HTTPException(status_code=404, detail="Vocabulary not found")
        
        # Check if answer is correct (case-insensitive)
        correct_answer = word_info.get("word", "").lower()
        user_answer = request.user_answer.lower().strip()
        
        is_correct = user_answer == correct_answer or user_answer in word_info.get("alternate_forms", [])
        
        # If using SRS, schedule the item
        if is_correct:
            quality = 4  # Correct answer
        else:
            quality = 1  # Incorrect answer
        
        db_srs.update_srs_item_sm2(
            srs_id=word_info.get("srs_id"),
            quality=quality,
            user_id=request.user_id
        )
        
        return {
            "user_id": request.user_id,
            "word_id": request.word_id,
            "correct_answer": correct_answer,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "definition": word_info.get("definition"),
            "example": word_info.get("example"),
            "feedback": "Correct!" if is_correct else f"The answer is: {correct_answer}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check vocabulary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vocabulary/stats")
async def get_vocabulary_stats(user_id: int = 1):
    """Get vocabulary learning statistics for user."""
    try:
        stats = db_srs.get_vocabulary_stats(user_id=user_id)
        return {
            "user_id": user_id,
            "total_learned": stats.get("total_learned", 0),
            "learned_today": stats.get("learned_today", 0),
            "items_due": stats.get("items_due", 0),
            "accuracy_rate": stats.get("accuracy_rate", 0),
            "streak_days": stats.get("streak_days", 0),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get vocabulary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/vocabulary/trending")
async def get_trending_vocabulary(user_id: int = 1, limit: int = 10):
    """Get user's most frequently missed vocabulary words."""
    try:
        words = db_srs.get_vocabulary_by_difficulty(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "words": words,
            "total": len(words),
            "message": "Your most challenging vocabulary words"
        }
    except Exception as e:
        logger.error(f"Failed to get trending vocabulary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

