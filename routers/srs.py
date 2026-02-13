"""
SRS Routes: Spaced Repetition System (SM-2 algorithm)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import db_srs
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class SRSReviewRequest(BaseModel):
    """Request model for SRS review submission."""
    srs_id: int
    quality: int  # 0-5: quality of response
    user_id: Optional[int] = 1


@router.get("/api/srs/due")
async def get_srs_due(user_id: int = 1, limit: int = 50):
    """Get vocabulary items due for review (SM-2 spaced repetition)."""
    try:
        items = db_srs.get_srs_due(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "items_due": len(items),
            "items": items,
            "message": f"{len(items)} items due for review"
        }
    except Exception as e:
        logger.error(f"Failed to get SRS items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/srs/items")
async def get_srs_items(user_id: int = 1, limit: Optional[int] = None):
    """Get all SRS items with lesson metadata."""
    try:
        items = db_srs.get_srs_items(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "items": items,
            "items_count": len(items)
        }
    except Exception as e:
        logger.error(f"Failed to get SRS items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/srs/review")
async def submit_srs_review(request: SRSReviewRequest):
    """Submit a review response for an SRS item and update using SM-2 algorithm."""
    try:
        # Get current SRS item details
        srs_item = db_srs.get_srs_item(request.srs_id)
        if not srs_item:
            raise HTTPException(status_code=404, detail="SRS item not found")
        
        # Update using SM-2 algorithm
        updated_item = db_srs.update_srs_item_sm2(
            srs_id=request.srs_id,
            quality=request.quality,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "srs_id": request.srs_id,
            "quality": request.quality,
            "next_review_date": updated_item.get("next_review_date"),
            "interval": updated_item.get("interval_days"),
            "ease_factor": updated_item.get("ease_factor"),
            "message": "SRS item updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit SRS review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/srs/stats")
async def get_srs_stats(user_id: int = 1):
    """Get SRS statistics for a user."""
    try:
        stats = db_srs.get_srs_stats(user_id=user_id)
        return stats
    except Exception as e:
        logger.error(f"Failed to get SRS stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
