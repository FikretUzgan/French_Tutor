"""
Database - SRS and Vocabulary Operations
Handles spaced repetition scheduling and vocabulary tracking
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from core.database import get_db_cursor


def schedule_lesson_vocabulary(lesson_id: str, vocabulary_count: int = 3, user_id: int = 1) -> int:
    """Create SRS entries for vocabulary in a lesson.
    
    Args:
        lesson_id: Lesson ID
        vocabulary_count: Number of vocabulary items (typically 3)
        user_id: User ID
    
    Returns:
        Number of SRS entries created
    """
    with get_db_cursor() as cursor:
        # Check if already scheduled
        cursor.execute("""
            SELECT COUNT(*) as count FROM srs_schedule
            WHERE lesson_id = ?
        """, (lesson_id,))
        
        existing = cursor.fetchone()["count"]
        if existing > 0:
            return existing
        
        # Create new SRS entries with initial SM-2 parameters
        entries_created = 0
        for i in range(vocabulary_count):
            # First review after 1 day
            next_review = datetime.now() + timedelta(days=1)
            
            cursor.execute("""
                INSERT INTO srs_schedule
                (lesson_id, next_review_date, interval_days, ease_factor, repetitions, status)
                VALUES (?, ?, ?, ?, ?, 'new')
            """, (lesson_id, next_review.isoformat(), 1, 2.5, 0))
            
            entries_created += 1
        
        return entries_created


def get_srs_due(user_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
    """Get vocabulary items due for SRS review.
    
    Returns items where next_review_date <= now, ordered by most overdue first.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT srs_id, lesson_id, next_review_date, interval_days,
                   ease_factor, repetitions, status
            FROM srs_schedule
            WHERE next_review_date <= CURRENT_TIMESTAMP
            ORDER BY next_review_date ASC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_srs_items(user_id: int = 1, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all SRS items for a user, ordered by next review date."""
    with get_db_cursor() as cursor:
        query = """
            SELECT srs_id, lesson_id, next_review_date, interval_days,
                   ease_factor, repetitions, status
            FROM srs_schedule
            ORDER BY next_review_date ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_srs_review(srs_id: int, quality: int) -> None:
    """Update SRS item after a review using SM-2 algorithm.
    
    Args:
        srs_id: SRS schedule ID
        quality: 0-5 quality rating
                 0=complete failure, 1=incorrect, 2=incorrect but close,
                 3=correct, 4=correct with effort, 5=perfect
    """
    with get_db_cursor() as cursor:
        # Get current SRS state
        cursor.execute("""
            SELECT repetitions, ease_factor, interval_days
            FROM srs_schedule
            WHERE srs_id = ?
        """, (srs_id,))
        
        row = cursor.fetchone()
        if not row:
            return
        
        repetitions = row["repetitions"]
        ease_factor = row["ease_factor"]
        interval_days = row["interval_days"]
        
        # SM-2 Algorithm
        if quality < 3:
            # Failed - reset
            repetitions = 0
            interval_days = 1
        else:
            # Passed
            repetitions += 1
            
            if repetitions == 1:
                interval_days = 1
            elif repetitions == 2:
                interval_days = 3
            else:
                interval_days = int(interval_days * ease_factor)
        
        # Update ease factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)  # Minimum ease factor
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=interval_days)
        
        # Update database
        cursor.execute("""
            UPDATE srs_schedule
            SET repetitions = ?, ease_factor = ?, interval_days = ?,
                next_review_date = ?, last_reviewed = CURRENT_TIMESTAMP, status = 'reviewed'
            WHERE srs_id = ?
        """, (repetitions, ease_factor, interval_days, next_review.isoformat(), srs_id))


def get_srs_stats(user_id: int = 1) -> Dict[str, Any]:
    """Get SRS statistics for a user."""
    with get_db_cursor() as cursor:
        # Count items by status
        cursor.execute("""
            SELECT COUNT(*) as total FROM srs_schedule
        """)
        total = cursor.fetchone()["total"]
        
        cursor.execute("""
            SELECT COUNT(*) as due FROM srs_schedule
            WHERE next_review_date <= CURRENT_TIMESTAMP
        """)
        due = cursor.fetchone()["due"]
        
        cursor.execute("""
            SELECT AVG(ease_factor) as avg_ease FROM srs_schedule
            WHERE status = 'reviewed'
        """)
        avg_ease_row = cursor.fetchone()
        avg_ease = avg_ease_row["avg_ease"] if avg_ease_row["avg_ease"] else 2.5
        
        return {
            "total_items": total,
            "due_for_review": due,
            "average_ease_factor": round(float(avg_ease), 2),
            "completion_percentage": round(100 * (total - due) / max(total, 1), 1) if total > 0 else 0
        }
