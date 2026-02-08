"""
Database - Exam Operations
Handles exam creation, submission, and grading
"""

from typing import Optional, Dict, Any, List
import json
from db_core import get_connection


def save_exam(exam_id: str, level: str, week_number: int, questions: str, user_id: int = 1) -> str:
    """Save an exam to the database.
    
    Args:
        exam_id: Unique exam identifier
        level: CEFR level (e.g., "A1.1")
        week_number: Week number in the course
        questions: JSON string of exam questions
        user_id: User creating the exam
    
    Returns:
        exam_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO exams (exam_id, level, week_number, questions)
        VALUES (?, ?, ?, ?)
    """, (exam_id, level, week_number, questions))
    
    conn.commit()
    conn.close()
    
    return exam_id


def get_exam(exam_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an exam by ID.
    
    Args:
        exam_id: The exam identifier
    
    Returns:
        dict with exam data or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT exam_id, level, week_number, questions, created_at
        FROM exams
        WHERE exam_id = ?
    """, (exam_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_exams_by_level_and_week(level: str, week_number: int) -> List[Dict[str, Any]]:
    """Get all exams for a specific level and week."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT exam_id, level, week_number, created_at
        FROM exams
        WHERE level = ? AND week_number = ?
        ORDER BY created_at DESC
    """, (level, week_number))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def save_exam_result(
    exam_id: str,
    user_id: int,
    answers: str,
    overall_score: float,
    passed: bool,
    feedback: str
) -> int:
    """Save exam results after submission and grading.
    
    Args:
        exam_id: The exam identifier
        user_id: Student ID
        answers: JSON string of student answers
        overall_score: Final score (0-100)
        passed: Whether student passed
        feedback: Optional grading feedback
    
    Returns:
        submission_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO exam_submissions
        (exam_id, score, passed, answers, feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (exam_id, overall_score, passed, answers, feedback))
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return submission_id


def get_exam_results(exam_id: str) -> List[Dict[str, Any]]:
    """Get all submitted results for an exam."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT exam_submission_id, exam_id, score, passed, submitted_at, feedback
        FROM exam_submissions
        WHERE exam_id = ?
        ORDER BY submitted_at DESC
    """, (exam_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_user_exam_results(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's exam submission history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT es.exam_submission_id, es.exam_id, es.score, es.passed,
               es.submitted_at, e.level, e.week_number
        FROM exam_submissions es
        JOIN exams e ON es.exam_id = e.exam_id
        ORDER BY es.submitted_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_latest_exam_for_level_week(level: str, week_number: int) -> Optional[Dict[str, Any]]:
    """Get the most recent exam for a level/week combination."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT exam_id, level, week_number, questions, created_at
        FROM exams
        WHERE level = ? AND week_number = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (level, week_number))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None
