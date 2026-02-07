"""
Database module for French Tutor.

Handles SQLite schema initialization and CRUD operations for:
- Lessons and lesson progress
- Homework submissions
- AI feedback and grading
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Any


DB_PATH = Path(__file__).parent / "french_tutor.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Lessons table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            lesson_id TEXT PRIMARY KEY,
            level TEXT NOT NULL,
            theme TEXT NOT NULL,
            week_number INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            grammar_explanation TEXT,
            vocabulary TEXT,
            speaking_prompt TEXT,
            homework_prompt TEXT,
            quiz_questions TEXT
        )
    """)

    # Lesson progress table (tracks learner progress)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT NOT NULL UNIQUE,
            completed BOOLEAN DEFAULT FALSE,
            homework_submitted BOOLEAN DEFAULT FALSE,
            homework_passed BOOLEAN DEFAULT NULL,
            date_started TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_completed TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
        )
    """)

    # Homework submissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homework_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT NOT NULL,
            text_content TEXT NOT NULL,
            audio_file_path TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            character_count INTEGER,
            audio_size_kb REAL,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
        )
    """)

    # AI feedback and grading table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS homework_feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL UNIQUE,
            text_score REAL,
            audio_score REAL,
            passed BOOLEAN,
            grammar_feedback TEXT,
            vocabulary_feedback TEXT,
            pronunciation_feedback TEXT,
            overall_feedback TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (submission_id) REFERENCES homework_submissions(submission_id)
        )
    """)

    # SRS (Spaced Repetition System) schedule table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS srs_schedule (
            srs_id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT NOT NULL,
            next_review_date TIMESTAMP,
            interval_days INTEGER DEFAULT 1,
            ease_factor REAL DEFAULT 2.5,
            repetitions INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            last_reviewed TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
        )
    """)

    # Exam table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_number INTEGER NOT NULL,
            level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            questions TEXT,
            duration_minutes INTEGER DEFAULT 45
        )
    """)

    # Exam submissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_submissions (
            exam_submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score REAL,
            passed BOOLEAN,
            answers TEXT,
            FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
        )
    """)

    conn.commit()
    conn.close()


def save_homework_submission(
    lesson_id: str,
    text_content: str,
    audio_file_path: Optional[str] = None,
    character_count: int = 0,
    audio_size_kb: float = 0.0,
) -> int:
    """Save a homework submission to the database.
    
    Args:
        lesson_id: ID of the lesson
        text_content: Text submission from learner
        audio_file_path: Path to uploaded audio file
        character_count: Number of characters in text
        audio_size_kb: Size of audio file in KB
    
    Returns:
        submission_id of the saved submission
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO homework_submissions 
        (lesson_id, text_content, audio_file_path, character_count, audio_size_kb, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (lesson_id, text_content, audio_file_path, character_count, audio_size_kb))
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return submission_id


def get_homework_submission(submission_id: int) -> Optional[dict]:
    """Retrieve a homework submission by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM homework_submissions WHERE submission_id = ?", (submission_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def update_homework_status(submission_id: int, status: str) -> None:
    """Update the status of a homework submission."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE homework_submissions SET status = ? WHERE submission_id = ?",
        (status, submission_id)
    )
    conn.commit()
    conn.close()


def save_homework_feedback(
    submission_id: int,
    text_score: float,
    audio_score: float,
    passed: bool,
    grammar_feedback: Optional[str] = None,
    vocabulary_feedback: Optional[str] = None,
    pronunciation_feedback: Optional[str] = None,
    overall_feedback: Optional[str] = None,
) -> int:
    """Save AI-generated homework feedback.
    
    Args:
        submission_id: ID of the homework submission
        text_score: Text evaluation score (0-100)
        audio_score: Pronunciation evaluation score (0-100)
        passed: Whether submission passed (text_score >= 70 AND audio_score >= 60)
        grammar_feedback: Feedback on grammar
        vocabulary_feedback: Feedback on vocabulary usage
        pronunciation_feedback: Feedback on pronunciation (from audio)
        overall_feedback: Overall feedback message
    
    Returns:
        feedback_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO homework_feedback
        (submission_id, text_score, audio_score, passed, grammar_feedback, vocabulary_feedback,
         pronunciation_feedback, overall_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (submission_id, text_score, audio_score, passed, grammar_feedback, vocabulary_feedback,
          pronunciation_feedback, overall_feedback))
    
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return feedback_id


def get_homework_feedback(submission_id: int) -> Optional[dict]:
    """Retrieve feedback for a homework submission."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM homework_feedback WHERE submission_id = ?", (submission_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


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


def is_lesson_blocked(lesson_id: str) -> bool:
    """Check if lesson is blocked (homework not submitted)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT homework_submitted FROM lesson_progress WHERE lesson_id = ?",
        (lesson_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return not row[0]  # Blocked if homework not submitted
    return False  # New lesson not blocked


def get_lesson_by_id(lesson_id: str) -> Optional[dict]:
    """Retrieve lesson metadata by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM lessons WHERE lesson_id = ?", (lesson_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


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


def get_all_lessons() -> list[dict]:
    """Retrieve all lessons from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            lesson_id, 
            level, 
            theme,
            week_number,
            grammar_explanation,
            vocabulary,
            speaking_prompt,
            homework_prompt,
            quiz_questions
        FROM lessons
        ORDER BY level, lesson_id
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_user_progress(user_id: int) -> list[dict]:
    """Get progress for a specific user."""
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
        ORDER BY lesson_id
    """)
    rows = cursor.fetchall()
    conn.close()
    
    progress_list = []
    for row in rows:
        row_dict = dict(row)
        # Add computed fields
        row_dict['status'] = 'completed' if row_dict['completed'] else ('submitted' if row_dict['homework_submitted'] else 'started')
        row_dict['completion_percentage'] = 100 if row_dict['completed'] else (50 if row_dict['homework_submitted'] else 25)
        progress_list.append(row_dict)
    
    return progress_list


if __name__ == "__main__":
    # Initialize database
    init_db()
    print(f"Database initialized at {DB_PATH}")
