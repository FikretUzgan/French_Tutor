"""
Database - Lesson and Progress Operations
Handles lesson storage, retrieval, and progress tracking
"""

from typing import Optional, List, Dict, Any
from db_core import get_connection


def save_lesson(
    lesson_id: str,
    level: str,
    theme: str,
    week_number: Optional[int] = None,
    grammar_explanation: Optional[str] = None,
    vocabulary: Optional[str] = None,
    speaking_prompt: Optional[str] = None,
    homework_prompt: Optional[str] = None,
    quiz_questions: Optional[str] = None,
) -> None:
    """Save a lesson to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO lessons
        (lesson_id, level, theme, week_number, grammar_explanation,
         vocabulary, speaking_prompt, homework_prompt, quiz_questions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (lesson_id, level, theme, week_number, grammar_explanation,
          vocabulary, speaking_prompt, homework_prompt, quiz_questions))
    
    conn.commit()
    conn.close()


def get_lesson_by_id(lesson_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a lesson by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT lesson_id, level, theme, week_number,
               grammar_explanation, vocabulary, speaking_prompt,
               homework_prompt, quiz_questions
        FROM lessons
        WHERE lesson_id = ?
    """, (lesson_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_all_lessons() -> List[Dict[str, Any]]:
    """Retrieve all lessons from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT lesson_id, level, theme, week_number,
               grammar_explanation, vocabulary, speaking_prompt,
               homework_prompt, quiz_questions
        FROM lessons
        ORDER BY level, lesson_id
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_lessons_by_level(level: str) -> List[Dict[str, Any]]:
    """Get all lessons for a specific CEFR level."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT lesson_id, level, theme, week_number
        FROM lessons
        WHERE level = ?
        ORDER BY week_number, lesson_id
    """, (level,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ===== Lesson Progress Operations =====

def init_lesson_progress(lesson_id: str) -> None:
    """Initialize progress tracking for a lesson."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO lesson_progress (lesson_id, completed, homework_submitted)
        VALUES (?, FALSE, FALSE)
    """, (lesson_id,))
    
    conn.commit()
    conn.close()


def mark_lesson_started(lesson_id: str) -> None:
    """Mark a lesson as started when user opens it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO lesson_progress 
        (lesson_id, completed, homework_submitted, date_started)
        VALUES (?, FALSE, FALSE, CURRENT_TIMESTAMP)
    """, (lesson_id,))
    
    conn.commit()
    conn.close()


def get_lesson_status(lesson_id: str) -> str:
    """Get the status of a specific lesson: 'completed', 'in_progress', or 'not_started'."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT completed, date_started
        FROM lesson_progress
        WHERE lesson_id = ?
    """, (lesson_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return 'not_started'
    
    if row['completed']:
        return 'completed'
    elif row['date_started']:
        return 'in_progress'
    else:
        return 'not_started'


def get_available_lessons_for_ui(user_id: int = 1) -> List[Dict[str, Any]]:
    """Get all available lessons with their progress status for lesson selection UI.
    
    Returns:
        List of lessons with status: 'completed', 'in_progress', or 'not_started'
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all lessons
    cursor.execute("""
        SELECT lesson_id, level, theme, week_number
        FROM lessons
        ORDER BY week_number, lesson_id
    """)
    all_lessons = cursor.fetchall()
    
    # Get progress for started/completed lessons
    cursor.execute("""
        SELECT lesson_id, completed, date_started
        FROM lesson_progress
        WHERE date_started IS NOT NULL
    """)
    progress_rows = cursor.fetchall()
    conn.close()
    
    progress_map = {row['lesson_id']: row for row in progress_rows}
    
    result = []
    for lesson in all_lessons:
        lesson_dict = dict(lesson)
        
        if lesson['lesson_id'] in progress_map:
            progress = progress_map[lesson['lesson_id']]
            lesson_dict['status'] = 'completed' if progress['completed'] else 'in_progress'
        else:
            lesson_dict['status'] = 'not_started'
        
        result.append(lesson_dict)
    
    return result


def get_user_progress(user_id: int) -> List[Dict[str, Any]]:
    """Get progress for a specific user.
    
    Returns only lessons that have been started or completed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            progress_id,
            lesson_id,
            completed,
            homework_submitted,
            homework_passed,
            date_started,
            date_completed
        FROM lesson_progress
        WHERE date_started IS NOT NULL
        ORDER BY date_started DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    progress_list = []
    for row in rows:
        row_dict = dict(row)
        # Compute status based on actual lesson state
        if row_dict['completed']:
            row_dict['status'] = 'completed'
            row_dict['completion_percentage'] = 100
        else:
            row_dict['status'] = 'in_progress'
            row_dict['completion_percentage'] = 50
        progress_list.append(row_dict)
    
    return progress_list


def mark_lesson_complete(lesson_id: str, homework_passed: bool = True) -> None:
    """Mark a lesson as completed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE lesson_progress
        SET completed = TRUE, homework_submitted = TRUE, homework_passed = ?,
            date_completed = CURRENT_TIMESTAMP
        WHERE lesson_id = ?
    """, (homework_passed, lesson_id))
    
    conn.commit()
    conn.close()


def update_lesson_homework_progress(lesson_id: str, homework_passed: bool) -> None:
    """Update lesson progress after homework submission."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE lesson_progress
        SET homework_submitted = TRUE,
            homework_passed = ?
        WHERE lesson_id = ?
    """, (homework_passed, lesson_id))
    
    conn.commit()
    conn.close()


def is_lesson_blocked(lesson_id: str, user_id: int = 1) -> bool:
    """Check if a lesson is blocked (e.g., due to homework requirement)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT homework_passed
        FROM lesson_progress
        WHERE lesson_id = ?
    """, (lesson_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    # Lesson is blocked if homework was required but not passed
    homework_passed = row['homework_passed']
    return homework_passed is False  # Explicitly not passed (None means not submitted yet)
