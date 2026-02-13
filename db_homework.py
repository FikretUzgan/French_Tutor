"""
Database - Homework Operations
Handles homework submissions, feedback, and grading
"""

from typing import Optional, Dict, Any, List
from core.database import get_db_cursor


def save_homework_submission(
    lesson_id: str,
    text_content: str,
    audio_file_path: Optional[str] = None,
    character_count: int = 0,
    audio_size_kb: float = 0.0,
) -> int:
    """Save a homework submission to the database.
    
    Returns:
        submission_id of the saved submission
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO homework_submissions 
            (lesson_id, text_content, audio_file_path, character_count, audio_size_kb, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (lesson_id, text_content, audio_file_path, character_count, audio_size_kb))
        
        submission_id = cursor.lastrowid
        return submission_id


def get_homework_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a homework submission by ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT submission_id, lesson_id, text_content, audio_file_path,
                   submitted_at, status, character_count, audio_size_kb
            FROM homework_submissions
            WHERE submission_id = ?
        """, (submission_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None


def update_homework_status(submission_id: int, status: str) -> None:
    """Update the status of a homework submission.
    
    Args:
        status: 'pending', 'graded', 'needs_revision', etc.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE homework_submissions
            SET status = ?
            WHERE submission_id = ?
        """, (status, submission_id))


def save_homework_feedback(
    submission_id: int,
    text_score: float,
    audio_score: Optional[float],
    passed: bool,
    grammar_feedback: str,
    vocabulary_feedback: str,
    pronunciation_feedback: Optional[str],
    overall_feedback: str
) -> int:
    """Save AI-generated feedback for a homework submission.
    
    Returns:
        feedback_id
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO homework_feedback
            (submission_id, text_score, audio_score, passed,
             grammar_feedback, vocabulary_feedback, pronunciation_feedback, overall_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (submission_id, text_score, audio_score, passed,
              grammar_feedback, vocabulary_feedback, pronunciation_feedback, overall_feedback))
        
        feedback_id = cursor.lastrowid
        return feedback_id


def get_homework_feedback(submission_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve feedback for a homework submission."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT feedback_id, submission_id, text_score, audio_score, passed,
                   grammar_feedback, vocabulary_feedback, pronunciation_feedback,
                   overall_feedback, generated_at
            FROM homework_feedback
            WHERE submission_id = ?
        """, (submission_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None


def get_homework_submissions_for_lesson(lesson_id: str) -> List[Dict[str, Any]]:
    """Get all homework submissions for a lesson."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT submission_id, lesson_id, text_content, submitted_at, status
            FROM homework_submissions
            WHERE lesson_id = ?
            ORDER BY submitted_at DESC
        """, (lesson_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_latest_homework_for_lesson(lesson_id: str) -> Optional[Dict[str, Any]]:
    """Get the most recent homework submission for a lesson."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT submission_id, lesson_id, text_content, audio_file_path,
                   submitted_at, status
            FROM homework_submissions
            WHERE lesson_id = ?
            ORDER BY submitted_at DESC
            LIMIT 1
        """, (lesson_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
