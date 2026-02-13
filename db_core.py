"""
Database Core Module - Connection and Schema Management
Handles SQLite connection pooling and database initialization
"""

import sqlite3
import logging
from typing import Optional
from core.database import get_db_connection

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database schema with all tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Core lessons table
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
        
        # Lesson progress tracking
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
        
        # Homework submissions
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
        
        # Homework feedback
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
        
        # SRS scheduling
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
        
        # Weakness tracking
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
        
        # Exam submissions
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
        
        # App settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lesson generation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                lesson_id TEXT NOT NULL,
                week INTEGER NOT NULL,
                day INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                curriculum_file TEXT,
                status TEXT DEFAULT 'generated',
                error_message TEXT,
                api_duration_seconds REAL,
                UNIQUE(user_id, lesson_id)
            )
        """)
        
        # Student profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                user_id INTEGER PRIMARY KEY,
                current_level TEXT DEFAULT 'A1.1',
                completed_weeks TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize default settings
        cursor.execute("SELECT COUNT(*) as count FROM app_settings WHERE key = 'homework_blocking_enabled'")
        if cursor.fetchone()["count"] == 0:
            cursor.execute(
                "INSERT INTO app_settings (key, value) VALUES ('homework_blocking_enabled', 'false')"
            )
        
        cursor.execute("SELECT COUNT(*) as count FROM app_settings WHERE key = 'dev_mode'")
        if cursor.fetchone()["count"] == 0:
            cursor.execute(
                "INSERT INTO app_settings (key, value) VALUES ('dev_mode', 'false')"
            )

def check_db_connection() -> bool:
    """Check if the database connection is working."""
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

def get_app_setting(key: str, default: str = "") -> str:
    """Get an app setting value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def set_app_setting(key: str, value: str) -> None:
    """Set an app setting value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value)
            VALUES (?, ?)
        """, (key, value))
