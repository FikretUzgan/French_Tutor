"""
Pydantic Schemas
Shared data models for the application
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class LessonResponse(BaseModel):
    lesson_id: str
    title: str
    level: str
    description: str
    content: Dict[str, Any]


class HomeworkSubmitRequest(BaseModel):
    lesson_id: str  # Changed to str to match lesson_id type
    homework_text: str
    user_id: Optional[int] = 1


class SpeakingRequest(BaseModel):
    scenario: str
    targets: List[str]
    transcribed_text: str


class TTSRequest(BaseModel):
    text: str
    lang: str = "fr"


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


class SRSReviewRequest(BaseModel):
    srs_id: int
    quality: int  # 0-5
    user_id: Optional[int] = 1


class VocabularyCheckRequest(BaseModel):
    question_id: str
    user_answer: str
    user_id: Optional[int] = 1


class ModeToggleRequest(BaseModel):
    dev_mode: bool


class FirstTimeSetupRequest(BaseModel):
    starting_level: str


class LessonGenerateRequest(BaseModel):
    week: int  # Week number (1-52)
    day: int = 1  # Day number (1-7, default 1)
    student_level: Optional[str] = None  # CEFR level (overrides student profile)
    user_id: Optional[int] = 1
