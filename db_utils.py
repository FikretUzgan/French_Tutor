"""
Database - Utility Functions
Weakness tracking, student profile, generation history, and app settings
"""

from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta
from core.database import get_db_cursor
from db_core import get_app_setting, set_app_setting


# ===== Weakness Tracking =====

def track_weakness(user_id: int, topic: str, is_error: bool = True) -> None:
    """Track a student weakness/error in a topic."""
    with get_db_cursor() as cursor:
        if is_error:
            cursor.execute("""
                INSERT INTO weakness_tracking (user_id, topic, error_count, success_count)
                VALUES (?, ?, 1, 0)
                ON CONFLICT(user_id, topic) DO UPDATE SET
                    error_count = error_count + 1,
                    last_error = CURRENT_TIMESTAMP
            """, (user_id, topic))
        else:
            cursor.execute("""
                INSERT INTO weakness_tracking (user_id, topic, success_count, error_count)
                VALUES (?, ?, 1, 0)
                ON CONFLICT(user_id, topic) DO UPDATE SET
                    success_count = success_count + 1
            """, (user_id, topic))


def get_user_weaknesses(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Get user's weakest topics by error frequency."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT weakness_id, topic, error_count, success_count,
                   ROUND(100.0 * success_count / (success_count + error_count), 1) as accuracy_percentage,
                   last_error
            FROM weakness_tracking
            WHERE user_id = ?
            ORDER BY error_count DESC, last_error DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_weakness_report(user_id: int) -> Dict[str, Any]:
    """Get comprehensive weakness report for a user."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as total_tracked FROM weakness_tracking WHERE user_id = ?
        """, (user_id,))
        total = cursor.fetchone()["total_tracked"]
        
        cursor.execute("""
            SELECT SUM(error_count) as total_errors FROM weakness_tracking WHERE user_id = ?
        """, (user_id,))
        errors = cursor.fetchone()["total_errors"] or 0
        
        weaknesses = get_user_weaknesses(user_id)
        
        return {
            "total_topics_tracked": total,
            "total_errors": errors,
            "weakest_topics": weaknesses[:3]
        }


# ===== Student Profile =====

def get_student_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get student profile."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT user_id, current_level, completed_weeks, started_at, last_updated
            FROM student_profile
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            row_dict = dict(row)
            try:
                row_dict['completed_weeks'] = json.loads(row_dict.get('completed_weeks', '[]'))
            except json.JSONDecodeError:
                row_dict['completed_weeks'] = []
            return row_dict
        
        return None


def get_student_level(user_id: int = 1) -> str:
    """Get current student level."""
    profile = get_student_profile(user_id)
    if profile:
        return profile.get('current_level', 'A1.1')
    
    # Fallback to app setting
    return get_app_setting("starting_level", "A1.1")


def update_student_level(user_id: int, new_level: str) -> None:
    """Update student's current level."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT OR REPLACE INTO student_profile (user_id, current_level)
            VALUES (?, ?)
        """, (user_id, new_level))


def get_completed_weeks(user_id: int = 1) -> List[int]:
    """Get list of completed week numbers."""
    profile = get_student_profile(user_id)
    if profile:
        return profile.get('completed_weeks', [])
    return []


def add_completed_week(user_id: int, week_number: int) -> None:
    """Mark a week as completed."""
    with get_db_cursor() as cursor:
        # Get current completed weeks
        cursor.execute("""
            SELECT completed_weeks FROM student_profile WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        completed = []
        if row and row["completed_weeks"]:
            try:
                completed = json.loads(row["completed_weeks"])
            except json.JSONDecodeError:
                completed = []
        
        if week_number not in completed:
            completed.append(week_number)
            completed.sort()
        
        cursor.execute("""
            INSERT OR REPLACE INTO student_profile
            (user_id, completed_weeks, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, json.dumps(completed)))


# ===== Lesson Generation History =====

def store_generated_lesson(
    user_id: int,
    lesson_id: str,
    week: int,
    day: int,
    curriculum_file: str,
    status: str = 'generated',
    error_message: Optional[str] = None,
    api_duration_seconds: Optional[float] = None
) -> int:
    """Store a lesson generation record."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO lesson_generation_history
            (user_id, lesson_id, week, day, curriculum_file, status, error_message, api_duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, lesson_id, week, day, curriculum_file, status, error_message, api_duration_seconds))
        
        record_id = cursor.lastrowid
        return record_id


def get_lesson_generation_history(user_id: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """Get lesson generation history."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, lesson_id, week, day, timestamp, status, error_message, api_duration_seconds
            FROM lesson_generation_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_student_weaknesses(user_id: int = 1, limit: int = 5) -> List[Dict[str, Any]]:
    """Alias for get_user_weaknesses for compatibility."""
    return get_user_weaknesses(user_id, limit)


# ===== Vocabulary Dashboard Statistics =====

def get_vocab_stats(user_id: int = 1) -> Dict[str, Any]:
    """Get vocabulary dashboard statistics."""
    from db_lessons import get_all_lessons
    from db_srs import get_srs_stats
    
    lessons = get_all_lessons()
    total_vocab = 0
    lessons_with_vocab = 0
    vocab_by_level: Dict[str, int] = {}
    vocab_by_week: Dict[int, int] = {}

    for lesson in lessons:
        raw_vocab = lesson.get("vocabulary") or "[]"
        try:
            vocab_list = json.loads(raw_vocab) if isinstance(raw_vocab, str) else raw_vocab
        except json.JSONDecodeError:
            vocab_list = []

        if not isinstance(vocab_list, list):
            vocab_list = []

        vocab_count = len(vocab_list)
        if vocab_count > 0:
            lessons_with_vocab += 1
        total_vocab += vocab_count

        level = lesson.get("level", "Unknown")
        vocab_by_level[level] = vocab_by_level.get(level, 0) + vocab_count

        week_number = lesson.get("week_number")
        if isinstance(week_number, int):
            vocab_by_week[week_number] = vocab_by_week.get(week_number, 0) + vocab_count

    srs_stats = get_srs_stats(user_id=user_id)
    weak_topics = get_user_weaknesses(user_id=user_id, limit=5)

    weeks = sorted(vocab_by_week.keys())
    average_per_week = round(total_vocab / len(weeks), 1) if weeks else 0

    return {
        "user_id": user_id,
        "total_vocab": total_vocab,
        "lessons_with_vocab": lessons_with_vocab,
        "vocab_by_level": vocab_by_level,
        "vocab_by_week": vocab_by_week,
        "average_vocab_per_week": average_per_week,
        "due_today": srs_stats.get("due_today", 0),
        "status_breakdown": srs_stats.get("status_breakdown", {}),
        "average_ease": srs_stats.get("average_ease", 2.5),
        "average_interval_days": srs_stats.get("average_interval_days", 0),
        "weak_topics": weak_topics
    }


# ===== App Settings Batch Retrieval =====

def get_app_settings(keys: List[str]) -> Dict[str, Optional[str]]:
    """Get multiple app settings at once."""
    if not keys:
        return {}
    
    with get_db_cursor() as cursor:
        placeholders = ",".join("?" for _ in keys)
        cursor.execute(
            f"SELECT key, value FROM app_settings WHERE key IN ({placeholders})",
            keys,
        )
        rows = cursor.fetchall()
        
    data = {key: None for key in keys}
    for row in rows:
        data[row["key"]] = row["value"]
    
    return data
