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

    # Weakness tracking table (tracks errors by topic)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weakness_tracking (
            weakness_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            topic TEXT NOT NULL,
            error_count INTEGER DEFAULT 1,
            success_count INTEGER DEFAULT 0,
            last_error TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy_percentage REAL DEFAULT 0,
            UNIQUE(user_id, topic)
        )
    """)

    # Exam table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id TEXT PRIMARY KEY UNIQUE,
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
            exam_id TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score REAL,
            passed BOOLEAN,
            answers TEXT,
            feedback TEXT,
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


def save_exam(exam_id: str, level: str, week_number: int, questions: str, user_id: int = 1) -> str:
    """Save an exam to the database.
    
    Args:
        exam_id: Unique exam identifier
        level: CEFR level (e.g., "A1.1")
        week_number: Week number in the course
        questions: JSON string of exam questions
        user_id: User creating the exam
    
    Returns:
        exam_id (the unique identifier)
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


def get_exam(exam_id: str) -> Optional[dict]:
    """Retrieve an exam by ID.
    
    Args:
        exam_id: Unique exam identifier
    
    Returns:
        Dict with exam data or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT exam_id, level, week_number, questions, duration_minutes, created_at
        FROM exams
        WHERE exam_id = ?
    """, (exam_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def save_exam_result(exam_id: str, user_id: int, answers: str, overall_score: float, passed: bool, feedback: str) -> int:
    """Save exam submission results.
    
    Args:
        exam_id: Exam ID (TEXT, not integer)
        user_id: User ID
        answers: JSON string of student answers
        overall_score: Score (0-100)
        passed: Whether exam was passed
        feedback: Grading feedback
    
    Returns:
        exam_submission_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO exam_submissions (exam_id, score, passed, answers, feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (exam_id, overall_score, passed, answers, feedback))
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return submission_id


def track_weakness(user_id: int, topic: str, is_error: bool = True) -> None:
    """Track a weakness in a specific topic.
    
    Args:
        user_id: User ID
        topic: Topic name (e.g., "passé composé", "pronouns y/en")
        is_error: True if this is an error, False if successful
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT weakness_id, error_count, success_count, accuracy_percentage
        FROM weakness_tracking
        WHERE user_id = ? AND topic = ?
    """, (user_id, topic))
    
    row = cursor.fetchone()
    
    if row:
        weakness_id, error_count, success_count, _ = row
        
        if is_error:
            error_count += 1
        else:
            success_count += 1
        
        total = error_count + success_count
        accuracy = (success_count / total * 100) if total > 0 else 0
        
        cursor.execute("""
            UPDATE weakness_tracking
            SET error_count = ?, success_count = ?, accuracy_percentage = ?, last_error = CURRENT_TIMESTAMP
            WHERE weakness_id = ?
        """, (error_count, success_count, accuracy, weakness_id))
    else:
        # New weakness entry
        accuracy = 0 if is_error else 100
        error_c = 1 if is_error else 0
        success_c = 0 if is_error else 1
        
        cursor.execute("""
            INSERT INTO weakness_tracking (user_id, topic, error_count, success_count, accuracy_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, topic, error_c, success_c, accuracy))
    
    conn.commit()
    conn.close()


def get_user_weaknesses(user_id: int, limit: int = 5) -> list[dict]:
    """Get top weakness topics for a user.
    
    Args:
        user_id: User ID
        limit: Number of top weaknesses to return
    
    Returns:
        List of weakness dicts, ordered by accuracy (lowest first)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT topic, error_count, success_count, accuracy_percentage, last_error
        FROM weakness_tracking
        WHERE user_id = ?
        ORDER BY accuracy_percentage ASC, error_count DESC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_weakness_report(user_id: int) -> dict:
    """Generate a comprehensive weakness report for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with weakness analysis and recommendations
    """
    weaknesses = get_user_weaknesses(user_id, limit=10)
    
    if not weaknesses:
        return {
            "user_id": user_id,
            "total_topics_tracked": 0,
            "top_weaknesses": [],
            "average_accuracy": 100,
            "recommendation": "Great job! Keep practicing to maintain your level."
        }
    
    # Calculate statistics
    total_errors = sum(w["error_count"] for w in weaknesses)
    total_successes = sum(w["success_count"] for w in weaknesses)
    total_attempts = total_errors + total_successes
    average_accuracy = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get top 5 weaknesses
    top_5 = weaknesses[:5]
    
    # Generate recommendation
    if average_accuracy > 80:
        recommendation = "Excellent! You're doing well. Focus on the weak areas below to improve further."
    elif average_accuracy > 60:
        recommendation = "Good progress! Review the weak topics listed below regularly."
    else:
        recommendation = "You have several areas to work on. Consider doing extra practice on the topics below."
    
    return {
        "user_id": user_id,
        "total_topics_tracked": len(weaknesses),
        "top_weaknesses": top_5,
        "average_accuracy": round(average_accuracy, 1),
        "total_attempts": total_attempts,
        "recommendation": recommendation
    }


def save_lesson(lesson_id: str, level: str, theme: str, week_number: int,
                grammar_explanation: str, vocabulary: str, speaking_prompt: str,
                homework_prompt: str, quiz_questions: str) -> str:
    """Save a lesson to the database.
    
    Args:
        lesson_id: Unique lesson ID
        level: CEFR level
        theme: Lesson theme/title
        week_number: Week number in course
        grammar_explanation: JSON string of grammar explanation
        vocabulary: JSON string of vocabulary list
        speaking_prompt: JSON string of speaking prompt
        homework_prompt: Homework instructions
        quiz_questions: JSON string of quiz questions
    
    Returns:
        lesson_id
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO lessons
        (lesson_id, level, theme, week_number, grammar_explanation, vocabulary,
         speaking_prompt, homework_prompt, quiz_questions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (lesson_id, level, theme, week_number, grammar_explanation, vocabulary,
          speaking_prompt, homework_prompt, quiz_questions))
    
    conn.commit()
    conn.close()
    
    return lesson_id


def get_srs_due(user_id: int = 1, limit: int = 10) -> list[dict]:
    """Get vocabulary items due for review today (SM-2 algorithm).
    
    Args:
        user_id: User ID
        limit: Maximum number of items to return (daily cap)
    
    Returns:
        List of vocabulary items due for review
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get items where next_review_date <= today
    cursor.execute("""
        SELECT srs_id, lesson_id, next_review_date, interval_days, ease_factor, 
               repetitions, status, last_reviewed
        FROM srs_schedule
        WHERE next_review_date <= datetime('now')
        AND status != 'buried'
        ORDER BY next_review_date ASC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_srs_item(srs_id: int, quality: int, user_id: int = 1) -> dict:
    """Update an SRS item after a review using the SM-2 algorithm.
    
    SM-2 Algorithm (simplified):
    - quality: 0-5 (0=wrong, 5=perfect)
    - If quality < 3: repetitions = 0, next_interval = 1 day
    - If quality >= 3:
        - If repetitions == 0: next_interval = 1 day
        - If repetitions == 1: next_interval = 3 days
        - If repetitions > 1: next_interval = previous_interval * ease_factor
    - ease_factor = max(1.3, ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    Args:
        srs_id: SRS item ID
        quality: Quality rating (0-5)
        user_id: User ID
    
    Returns:
        Updated SRS item dict
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current SRS state
    cursor.execute("""
        SELECT srs_id, lesson_id, interval_days, ease_factor, repetitions, status
        FROM srs_schedule
        WHERE srs_id = ?
    """, (srs_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"SRS item {srs_id} not found")
    
    current = dict(row)
    
    # SM-2 Algorithm
    if quality < 3:
        # Wrong answer
        new_repetitions = 0
        new_interval = 1
        new_ease = current["ease_factor"]
    else:
        # Correct answer
        if current["repetitions"] == 0:
            new_interval = 1
        elif current["repetitions"] == 1:
            new_interval = 3
        else:
            new_interval = int(current["interval_days"] * current["ease_factor"])
        
        new_repetitions = current["repetitions"] + 1
        
        # Update ease factor
        new_ease = current["ease_factor"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        new_ease = max(1.3, new_ease)  # Minimum ease factor
    
    # Calculate next review date
    from datetime import datetime, timedelta
    next_review = datetime.now() + timedelta(days=new_interval)
    
    # Update database
    cursor.execute("""
        UPDATE srs_schedule
        SET interval_days = ?, 
            ease_factor = ?, 
            repetitions = ?, 
            status = 'active',
            last_reviewed = CURRENT_TIMESTAMP,
            next_review_date = ?
        WHERE srs_id = ?
    """, (new_interval, new_ease, new_repetitions, next_review.isoformat(), srs_id))
    
    conn.commit()
    
    # Fetch updated item
    cursor.execute("""
        SELECT srs_id, lesson_id, next_review_date, interval_days, ease_factor,
               repetitions, status, last_reviewed
        FROM srs_schedule
        WHERE srs_id = ?
    """, (srs_id,))
    
    updated = dict(cursor.fetchone())
    conn.close()
    
    return updated


def get_srs_stats(user_id: int = 1) -> dict:
    """Get SRS statistics for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with SRS statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total items
    cursor.execute("SELECT COUNT(*) as count FROM srs_schedule")
    total_items = cursor.fetchone()["count"]
    
    # Items due today
    cursor.execute("""
        SELECT COUNT(*) as count FROM srs_schedule
        WHERE next_review_date <= datetime('now')
    """)
    due_today = cursor.fetchone()["count"]
    
    # Items by status
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM srs_schedule
        GROUP BY status
    """)
    status_rows = cursor.fetchall()
    status_counts = {row["status"]: row["count"] for row in status_rows}
    
    # Average ease factor
    cursor.execute("SELECT AVG(ease_factor) as avg_ease FROM srs_schedule WHERE status != 'buried'")
    avg_ease_row = cursor.fetchone()
    avg_ease = avg_ease_row["avg_ease"] if avg_ease_row and avg_ease_row["avg_ease"] else 2.5
    
    # Average interval
    cursor.execute("SELECT AVG(interval_days) as avg_interval FROM srs_schedule WHERE status != 'buried'")
    avg_interval_row = cursor.fetchone()
    avg_interval = avg_interval_row["avg_interval"] if avg_interval_row and avg_interval_row["avg_interval"] else 0
    
    conn.close()
    
    return {
        "user_id": user_id,
        "total_items": total_items,
        "due_today": due_today,
        "status_breakdown": status_counts,
        "average_ease": round(avg_ease, 2),
        "average_interval_days": round(avg_interval, 1)
    }


def schedule_lesson_vocabulary(lesson_id: str, vocabulary_count: int = 3, user_id: int = 1) -> int:
    """Create SRS entries for vocabulary in a lesson (called when lesson is started).
    
    Args:
        lesson_id: Lesson ID
        vocabulary_count: Number of vocabulary items (typically 3)
        user_id: User ID
    
    Returns:
        Number of SRS entries created
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if already scheduled
    cursor.execute("""
        SELECT COUNT(*) as count FROM srs_schedule
        WHERE lesson_id = ?
    """, (lesson_id,))
    
    existing = cursor.fetchone()["count"]
    if existing > 0:
        conn.close()
        return existing  # Already scheduled
    
    # Create new SRS entries with initial SM-2 parameters
    from datetime import datetime, timedelta
    
    entries_created = 0
    for i in range(vocabulary_count):
        # First review after 1 day
        next_review = (datetime.now() + timedelta(days=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO srs_schedule
            (lesson_id, next_review_date, interval_days, ease_factor, repetitions, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lesson_id, next_review, 1, 2.5, 0, 'new'))
        
        entries_created += 1
    
    conn.commit()
    conn.close()
    
    return entries_created


if __name__ == "__main__":
    # Initialize database
    init_db()
    print(f"Database initialized at {DB_PATH}")
