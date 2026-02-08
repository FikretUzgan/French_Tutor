"""
API Request/Response Models for French Tutor
Centralized Pydantic models for all endpoints
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# Lesson and Content Models
class LessonResponse(BaseModel):
    lesson_id: str
    title: str
    level: str
    description: str
    content: Dict[str, Any]


# Homework Models
class HomeworkSubmitRequest(BaseModel):
    lesson_id: int
    homework_text: str
    user_id: Optional[int] = 1


# Speaking Models
class SpeakingRequest(BaseModel):
    scenario: str
    targets: List[str]
    transcribed_text: str


# Audio/TTS Models
class TTSRequest(BaseModel):
    text: str
    lang: str = "fr"


# Exam Models
class ExamQuestion(BaseModel):
    question_id: str
    question_type: str  # "mcq", "fill", "translation", "reading", "speaking"
    question_text: str
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: Optional[str] = None  # For validation
    context: Optional[str] = None  # For reading comprehension


class ExamGenerateRequest(BaseModel):
    level: str  # e.g., "A1.1", "A2.1"
    week_number: int
    user_id: Optional[int] = 1


class ExamSubmitRequest(BaseModel):
    exam_id: str
    answers: Dict[str, str]  # question_id -> student_answer
    user_id: Optional[int] = 1


# SRS (Spaced Repetition System) Models
class SRSReviewRequest(BaseModel):
    srs_id: int
    quality: int  # 0-5: 0=complete failure, 1=incorrect, 2=incorrect but close, 3=correct, 4=correct with effort, 5=perfect
    user_id: Optional[int] = 1


# Vocabulary Models
class VocabularyCheckRequest(BaseModel):
    question_id: str
    user_answer: str
    user_id: Optional[int] = 1


# Settings Models
class ModeToggleRequest(BaseModel):
    dev_mode: bool


class FirstTimeSetupRequest(BaseModel):
    starting_level: str


# Lesson Generation Models
class LessonGenerateRequest(BaseModel):
    week: int  # Week number (1-52)
    day: int = 1  # Day number (1-7, default 1)
    student_level: Optional[str] = None  # CEFR level (overrides student profile if provided)
    user_id: Optional[int] = 1  # Student user ID
