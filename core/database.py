import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)

def get_db_path() -> Path:
    """Get the full path to the database file."""
    return settings.BASE_DIR / settings.DB_NAME

def init_db():
    """Initialize the database with schema if it doesn't exist."""
    db_path = get_db_path()
    
    if not db_path.exists():
        logger.info(f"Database not found at {db_path}. Initializing...")
        # Here we would typically run schema creation scripts
        # For now, we rely on the existing logic in db_core.py to handle schema
        pass
    else:
        logger.info(f"Database found at {db_path}")

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures connections are closed even if errors occur.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
            conn.commit()
    """
    conn = None
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row  # Access columns by name
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor():
    """
    Context manager that yields a cursor and handles commit/rollback.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute(...)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
