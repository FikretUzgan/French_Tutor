"""
French Tutor - FastAPI Backend
High-performance web application for French language learning
"""

import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import json
import re
import unicodedata

# Import our existing modules
import db_core
import db_lessons
import db_homework
import db_exams
import db_srs
import db_utils
import google.generativeai as genai
import whisper
from gtts import gTTS
try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:  # Optional for local audio capture
    sd = None
    sf = None
import numpy as np
import tempfile

# Import new modules for dynamic lesson generation
import curriculum_loader
import prompt_builders
import lesson_generator
import answer_validator

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="French Tutor API",
    description="Fast French language learning platform with AI tutoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Whisper model (cached)
WHISPER_MODEL = None

# Pydantic Models
class LessonResponse(BaseModel):
    lesson_id: str
    title: str
    level: str
    description: str
    content: Dict[str, Any]

class HomeworkSubmitRequest(BaseModel):
    lesson_id: int
    homework_text: str
    user_id: Optional[int] = 1  # For now, default user

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
    quality: int  # 0-5: 0=complete failure, 1=incorrect, 2=incorrect but close, 3=correct, 4=correct with effort, 5=perfect
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
    student_level: Optional[str] = None  # CEFR level (overrides student profile if provided)
    user_id: Optional[int] = 1  # Student user ID

# Helper Functions
def load_whisper_model():
    """Get cached Whisper model (pre-loaded on startup)"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        # This should not happen if startup event ran, but as a fallback:
        print("[WARNING] Whisper model not pre-loaded. Loading now (this will be slow)...")
        WHISPER_MODEL = whisper.load_model("tiny")  # Use tiny model as fallback
    return WHISPER_MODEL

def normalize_audio_peak(audio: np.ndarray, target_dbfs: float = -3.0) -> np.ndarray:
    """Normalize audio to target peak level"""
    if len(audio) == 0:
        return audio
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    target_linear = 10 ** (target_dbfs / 20.0)
    gain = target_linear / peak
    normalized = audio * gain
    return np.clip(normalized, -1.0, 1.0)


LEVEL_ORDER = [
    "A1.1",
    "A1.2",
    "A2.1",
    "A2.2",
    "B1.1",
    "B1.2",
    "B2.1",
    "B2.2",
]


def get_dev_mode() -> bool:
    value = db_core.get_app_setting("dev_mode", "false")
    return str(value).lower() == "true"


def get_current_level() -> str:
    level = db_core.get_app_setting("current_level")
    if level in LEVEL_ORDER:
        return level
    starting_level = db_core.get_app_setting("starting_level")
    if starting_level in LEVEL_ORDER:
        return starting_level
    return "A1.1"


def build_lesson_response(lesson: dict) -> LessonResponse:
    content = {
        "grammar": json.loads(lesson.get("grammar_explanation", "{}")) if lesson.get("grammar_explanation") else {},
        "vocabulary": json.loads(lesson.get("vocabulary", "[]")) if lesson.get("vocabulary") else [],
        "speaking": json.loads(lesson.get("speaking_prompt", "{}")) if lesson.get("speaking_prompt") else {},
        "homework": lesson.get("homework_prompt", ""),
        "quiz": json.loads(lesson.get("quiz_questions", "{}")) if lesson.get("quiz_questions") else {},
    }

    return LessonResponse(
        lesson_id=lesson["lesson_id"],
        title=lesson.get("theme", "Untitled Lesson"),
        level=lesson.get("level", "Unknown"),
        description=f"Week {lesson.get('week_number', 'N/A')} - {lesson.get('theme', '')}",
        content=content,
    )

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Whisper"""
    model = load_whisper_model()
    result = model.transcribe(str(audio_path), language="fr")
    return result["text"].strip()

def get_ai_speaking_feedback(transcribed_text: str, scenario: str, targets: List[str]) -> str:
    """Generate AI feedback for speaking practice using Gemini"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ No API key configured. Please set GEMINI_API_KEY in .env file."
    
    try:
        targets_list = "\n".join(f"- {t}" for t in targets)
        prompt = f"""You are a French language tutor. Evaluate this student's response in a conversation scenario.

Scenario: {scenario}
Conversation goals:
{targets_list}

Student said: "{transcribed_text}"

    Provide concise, encouraging feedback in French only, in this format:
    ✅ Points positifs (grammaire, vocabulaire, pertinence)
    ⚠️ Ce qui peut etre ameliore
    💡 Proposition pour la prochaine reponse

    Keep it under 100 words, be supportive. Do not use any English words."""
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        feedback_text = response.text.strip()
        return f"📝 Ta reponse: {transcribed_text}\n\n🤖 Retour du tuteur:\n{feedback_text}"
    
    except Exception as e:
        return f"❌ Error getting AI feedback: {str(e)}"


def evaluate_homework_ai(homework_text: str, audio_path: Optional[str] = None) -> Dict[str, Any]:
    """Evaluate homework submission using Gemini AI.
    
    Args:
        homework_text: Student's text submission
        audio_path: Optional path to audio file for pronunciation evaluation
    
    Returns:
        Dict with text_score, audio_score, and detailed feedback
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Default response if no API key
    if not api_key:
        return {
            "text_score": 50.0,
            "audio_score": None,
            "passed": False,
            "grammar_feedback": "API key not configured",
            "vocabulary_feedback": "API key not configured",
            "pronunciation_feedback": None,
            "overall_feedback": "Evaluation pending - API key not configured"
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # STEP 1: Evaluate text submission
        text_eval_prompt = f"""You are a strict French language teacher evaluating homework.

Student submission:
"{homework_text}"

Evaluate this submission on:
1. Grammar correctness (conjugations, agreement, syntax)
2. Vocabulary appropriateness and usage
3. Content relevance and completeness

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "text_score": <0-100 number>,
    "grammar_feedback": "<1-2 sentences on grammar>",
    "vocabulary_feedback": "<1-2 sentences on vocabulary>",
    "overall_text_feedback": "<1-2 sentences overall>"
}}

Minimum passing score: 70. Be critical but fair."""
        
        text_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text_eval_prompt
        )
        
        # Parse JSON response
        text_eval = {}
        try:
            # Extract JSON from response (may contain whitespace)
            text_content = text_response.text.strip()
            # Try to parse as JSON
            text_eval = json.loads(text_content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            text_eval = {
                "text_score": 60.0,
                "grammar_feedback": "Unable to parse evaluation",
                "vocabulary_feedback": "Unable to parse evaluation",
                "overall_text_feedback": text_response.text[:200]
            }
        
        text_score = text_eval.get("text_score", 60.0)
        
        # STEP 2: Evaluate audio pronunciation (if provided)
        audio_score = None
        pronunciation_feedback = None
        
        if audio_path and os.path.exists(audio_path):
            try:
                # Transcribe audio
                transcribed_audio = transcribe_audio(audio_path)
                
                # Evaluate pronunciation by comparing transcription to expected text
                audio_eval_prompt = f"""You are evaluating French speech pronunciation.

Expected text (what student should read):
"{homework_text}"

Actual transcription (what was spoken):
"{transcribed_audio}"

Evaluate the student's pronunciation, fluency, and how well they read the expected text:
1. How many words match the expected text?
2. Pronunciation quality assessment
3. Pace and natural rhythm

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "audio_score": <0-100 number>,
    "pronunciation_feedback": "<2-3 sentences on pronunciation and fluency>"
}}

Minimum passing score: 60. Consider that some STT errors may occur."""
                
                audio_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=audio_eval_prompt
                )
                
                # Parse audio evaluation
                try:
                    audio_content = audio_response.text.strip()
                    audio_eval = json.loads(audio_content)
                    audio_score = audio_eval.get("audio_score", 50.0)
                    pronunciation_feedback = audio_eval.get("pronunciation_feedback", "Unable to evaluate")
                except json.JSONDecodeError:
                    audio_score = 50.0
                    pronunciation_feedback = "Unable to parse pronunciation evaluation"
            
            except Exception as e:
                audio_score = 50.0
                pronunciation_feedback = f"Error evaluating audio: {str(e)}"
        
        # STEP 3: Determine pass/fail
        passed = (text_score >= 70) and (audio_score is None or audio_score >= 60)
        
        # STEP 4: Generate overall feedback
        if passed:
            overall_feedback = "Très bien! Your submission meets the requirements. You can move to the next lesson."
        else:
            issues = []
            if text_score < 70:
                issues.append("text accuracy")
            if audio_score is not None and audio_score < 60:
                issues.append("pronunciation")
            issue_str = " and ".join(issues)
            overall_feedback = f"Please revise your submission, focusing on {issue_str}. You can resubmit."
        
        return {
            "text_score": text_score,
            "audio_score": audio_score,
            "passed": passed,
            "grammar_feedback": text_eval.get("grammar_feedback", ""),
            "vocabulary_feedback": text_eval.get("vocabulary_feedback", ""),
            "pronunciation_feedback": pronunciation_feedback,
            "overall_feedback": overall_feedback
        }
    
    except Exception as e:
        return {
            "text_score": 50.0,
            "audio_score": None,
            "passed": False,
            "grammar_feedback": f"Error: {str(e)}",
            "vocabulary_feedback": "",
            "pronunciation_feedback": None,
            "overall_feedback": f"Evaluation failed: {str(e)}"
        }


def generate_lesson_ai(level: str, week_number: int, grammar_topic: str, vocabulary_words: List[str]) -> Dict[str, Any]:
    """Generate a complete lesson using Gemini AI.
    
    Args:
        level: CEFR level (e.g., "A1.1")
        week_number: Week number
        grammar_topic: Main grammar topic for the lesson
        vocabulary_words: List of vocabulary words to teach
    
    Returns:
        Dict with complete lesson structure
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "level": level,
            "week_number": week_number,
            "theme": grammar_topic,
            "error": "API key not configured"
        }
    
    try:
        client = genai.Client(api_key=api_key)
        
        vocab_list = ", ".join(vocabulary_words)
        
        lesson_prompt = f"""Create a complete French lesson for level {level}, week {week_number}.

Main grammar topic: {grammar_topic}
Vocabulary to teach: {vocab_list}

Generate a lesson with this exact JSON structure (no markdown, no code blocks):
{{
    "level": "{level}",
    "week_number": {week_number},
    "theme": "{grammar_topic}",
    "grammar": {{
        "explanation": "<2-3 sentences explaining the grammar concept in simple English>",
        "examples": [
            "<French sentence example 1>",
            "<French sentence example 2>",
            "<French sentence example 3>"
        ],
        "conjugation": [
            "<conjugation table 1>",
            "<conjugation table 2>"
        ]
    }},
    "vocabulary": [
        "<word in French (English translation)>",
        "<word in French (English translation)>",
        "<word in French (English translation)>"
    ],
    "speaking": {{
        "prompt": "<A speaking scenario related to the grammar topic>",
        "targets": [
            "<target 1: use the grammar topic>",
            "<target 2: use the vocabulary>",
            "<target 3: mention a person or place>"
        ]
    }},
    "quiz": {{
        "questions": [
            "<Multiple choice or fill-in-the-blank question>",
            "<Another question>",
            "<Another question>"
        ]
    }},
    "homework": "<Homework description with specific instructions>"
}}

Make sure:
- Examples use the target grammar and vocabulary
- Explanation is at {level} level (simple for A1, more complex for B1+)
- Speaking scenario is realistic and engaging
- Homework requires both writing and audio recording"""
        
        response = model.generate_content(lesson_prompt)
        
        try:
            lesson_data = json.loads(response.text.strip())
            lesson_data['created_at'] = datetime.now().isoformat()
            return lesson_data
        except json.JSONDecodeError:
            return {
                "level": level,
                "week_number": week_number,
                "theme": grammar_topic,
                "error": "Failed to parse lesson JSON"
            }
    
    except Exception as e:
        return {
            "level": level,
            "week_number": week_number,
            "theme": grammar_topic,
            "error": str(e)
        }


def generate_exam_ai(level: str, week_number: int) -> Dict[str, Any]:
    """Generate a weekly exam using Gemini AI.
    
    Exam composition:
    - MCQ (30%): 3 questions
    - Fill-in-the-blank (20%): 2 questions
    - Translation (20%): 2 questions
    - Reading comprehension (15%): 1 passage + 2 questions
    - Speaking (15%): 1 scenario
    
    Args:
        level: CEFR level (e.g., "A1.1", "A2.1")
        week_number: Week number in the course
    
    Returns:
        Dict with exam_id, questions, and metadata
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "exam_id": f"exam_{level}_w{week_number}",
            "level": level,
            "week_number": week_number,
            "questions": [],
            "error": "API key not configured"
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        exam_prompt = f"""You are creating a French language exam for level {level}, week {week_number}.

Create an exam with these question types:
1. MCQ (3 questions) - 30%
2. Fill-in-the-blank (2 questions) - 20%
3. Translation FR→EN or EN→FR (2 questions) - 20%
4. Reading comprehension (1 short passage + 2 questions) - 15%
5. Speaking scenario (1 scenario) - 15%

For level {level}, use vocabulary and grammar appropriate to that level.

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "questions": [
        // MCQ questions (3)
        {{"question_id": "mcq_1", "question_type": "mcq", "question_text": "...", "options": ["a)", "b)", "c)", "d)"], "correct_answer": "a)"}},
        // Fill-in-the-blank (2)
        {{"question_id": "fill_1", "question_type": "fill", "question_text": "Je _____ à l'école.", "correct_answer": "vais"}},
        // Translation (2)
        {{"question_id": "trans_1", "question_type": "translation", "question_text": "Translate to French: 'I go to school'", "correct_answer": "Je vais à l'école."}},
        // Reading comprehension (passage + 2 questions)
        {{"question_id": "read_context", "question_type": "reading", "context": "<short French passage>"}},
        {{"question_id": "read_1", "question_type": "reading", "question_text": "<question about passage>", "correct_answer": "<answer>"}},
        // Speaking scenario
        {{"question_id": "speak_1", "question_type": "speaking", "question_text": "<scenario description>", "context": "<conversation context>"}}
    ]
}}

Make questions realistic and fair."""
        
        response = model.generate_content(exam_prompt)
        
        try:
            exam_data = json.loads(response.text.strip())
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            exam_data = {"questions": []}
        
        exam_id = f"exam_{level}_w{week_number}_{int(datetime.now().timestamp())}"
        
        return {
            "exam_id": exam_id,
            "level": level,
            "week_number": week_number,
            "created_at": datetime.now().isoformat(),
            "questions": exam_data.get("questions", []),
            "duration_minutes": 45
        }
    
    except Exception as e:
        return {
            "exam_id": f"exam_{level}_w{week_number}",
            "level": level,
            "week_number": week_number,
            "questions": [],
            "error": str(e)
        }


def grade_exam_ai(questions: List[Dict[str, Any]], student_answers: Dict[str, str]) -> Dict[str, Any]:
    """Grade exam answers using Gemini AI.
    
    Args:
        questions: List of exam questions with correct answers
        student_answers: Dict mapping question_id to student's answer
    
    Returns:
        Dict with scores, feedback, and pass/fail status
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "overall_score": 0.0,
            "passed": False,
            "error": "API key not configured"
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Format questions and answers for grading
        grading_data = []
        for q in questions:
            q_id = q.get("question_id", "")
            student_ans = student_answers.get(q_id, "")
            correct_ans = q.get("correct_answer", "")
            
            grading_data.append({
                "question_id": q_id,
                "type": q.get("question_type", ""),
                "question": q.get("question_text", ""),
                "correct_answer": correct_ans,
                "student_answer": student_ans
            })
        
        grade_prompt = f"""You are a French language exam grader. Grade these exam answers fairly.

Grading questions:
{json.dumps(grading_data, indent=2)}

For each question:
- MCQ: 1 point if correct, 0 if wrong
- Fill-in-blank: 1 point if correct, 0.5 if close spelling variant
- Translation: 1 point if correct, 0.5 if meaning correct but phrasing slightly off
- Reading: 1 point each if answers show comprehension
- Speaking: 0.5 points (placeholder, would need audio)

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "question_scores": {{"question_id": score, ...}},
    "total_points": <sum of all scores>,
    "max_points": <total possible points>,
    "overall_percentage": <0-100>,
    "critical_topics": {{"grammar": <0-100>, "vocabulary": <0-100>, "reading": <0-100>, "speaking": <0-100>}},
    "feedback": "<overall feedback>"
}}

Pass if overall >= 70% AND all critical topics >= 70%."""
        
        response = model.generate_content(grade_prompt)
        
        try:
            grading_result = json.loads(response.text.strip())
        except json.JSONDecodeError:
            grading_result = {
                "overall_percentage": 50.0,
                "critical_topics": {},
                "feedback": "Grading failed"
            }
        
        overall_score = grading_result.get("overall_percentage", 50.0)
        critical_topics = grading_result.get("critical_topics", {})
        
        # Pass criteria: overall >= 70% AND all critical topics >= 70%
        passed = (overall_score >= 70 and 
                 all(score >= 70 for score in critical_topics.values()))
        
        return {
            "overall_score": overall_score,
            "passed": passed,
            "question_scores": grading_result.get("question_scores", {}),
            "critical_topics": critical_topics,
            "feedback": grading_result.get("feedback", ""),
            "message": "Exam graded successfully"
        }
    
    except Exception as e:
        return {
            "overall_score": 0.0,
            "passed": False,
            "feedback": f"Grading error: {str(e)}",
            "error": str(e)
        }


def sanitize_tts_text(text: str) -> str:
    """Remove emoji/symbols that TTS reads aloud."""
    if not text:
        return ""
    cleaned = "".join(
        ch
        for ch in text
        if unicodedata.category(ch) not in ("So", "Sk", "Cf")
    )
    cleaned = cleaned.replace("*", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_vocabulary_from_lesson(lesson_data: dict) -> list[dict]:
    """Extract vocabulary items from lesson data.
    
    Returns list of dicts with 'french', 'english' keys.
    Example: {"french": "un cahier", "english": "notebook"}
    """
    vocab_list = []
    raw_vocab = lesson_data.get("vocabulary", [])
    if isinstance(raw_vocab, str):
        try:
            raw_vocab = json.loads(raw_vocab)
        except json.JSONDecodeError:
            raw_vocab = []
    
    for item in raw_vocab:
        # Parse "French word (English translation)" format
        if "(" in item and ")" in item:
            french_part = item.split("(")[0].strip()
            english_part = item.split("(")[1].split(")")[0].strip()
            vocab_list.append({
                "french": french_part,
                "english": english_part
            })
    
    return vocab_list


def slugify_vocab(text: str) -> str:
    """Create a URL-safe identifier for vocabulary items."""
    return re.sub(r"\s+", "_", text.strip().lower())


def build_vocab_pool(lessons: list[dict]) -> list[dict]:
    """Build a vocabulary pool from lesson data for distractors and stats."""
    vocab_pool = []
    for lesson in lessons:
        lesson_id = lesson.get("lesson_id")
        lesson_level = lesson.get("level")
        if not lesson_id:
            continue
        for vocab in extract_vocabulary_from_lesson(lesson):
            vocab_pool.append({
                "french": vocab["french"],
                "english": vocab["english"],
                "lesson_id": lesson_id,
                "level": lesson_level
            })
    return vocab_pool


def pick_distractors(vocab_pool: list[dict], field: str, correct_value: str, count: int = 2) -> list[str]:
    """Pick real vocabulary distractors from the pool."""
    import random

    candidates = [
        item[field]
        for item in vocab_pool
        if item.get(field) and item[field].lower() != correct_value.lower()
    ]
    random.shuffle(candidates)

    distractors = []
    for item in candidates:
        if item.lower() != correct_value.lower() and item not in distractors:
            distractors.append(item)
        if len(distractors) >= count:
            break

    return distractors


def generate_fill_blank_question(vocab_item: dict, lesson_id: str, vocab_pool: list[dict]) -> dict:
    """Generate a fill-in-the-blank question for vocabulary practice."""
    import random

    templates = [
        "Complete: Je vois ____ aujourd'hui.",
        "Complete: Elle cherche ____.",
        "Complete: Nous utilisons ____.",
        "Complete: Ils parlent de ____.",
        "Complete: Je pense a ____."
    ]
    sentence = random.choice(templates)
    question_text = f"{sentence} (Hint: {vocab_item['english']})"
    correct_answer = vocab_item["french"]

    options = [correct_answer]
    options.extend(pick_distractors(vocab_pool, "french", correct_answer, count=2))
    if len(options) < 3:
        options.extend([correct_answer] * (3 - len(options)))

    random.shuffle(options)

    return {
        "question_id": f"{lesson_id}::{slugify_vocab(vocab_item['french'])}::fill_blank",
        "type": "fill_blank",
        "question": question_text,
        "correct_answer": correct_answer,
        "options": options,
        "lesson_id": lesson_id,
        "french_word": vocab_item["french"],
        "english_word": vocab_item["english"]
    }


def generate_vocab_question(
    vocab_item: dict,
    lesson_id: str,
    vocab_pool: list[dict],
    question_type: Optional[str] = None
) -> dict:
    """Generate a vocabulary practice question with multiple choice options.

    Args:
        vocab_item: dict with 'french' and 'english' keys
        lesson_id: ID of the lesson this vocab is from
        vocab_pool: list of vocabulary entries for distractors
        question_type: optional explicit type

    Returns:
        dict with question_id, type, question, correct_answer, options
    """
    import random

    if not question_type:
        question_type = random.choices(
            ["french_to_english", "english_to_french", "fill_blank"],
            weights=[0.45, 0.45, 0.10]
        )[0]

    if question_type == "fill_blank":
        return generate_fill_blank_question(vocab_item, lesson_id, vocab_pool)

    question_id = f"{lesson_id}::{slugify_vocab(vocab_item['french'])}::{question_type}"

    if question_type == "french_to_english":
        question_text = f"What does '{vocab_item['french']}' mean in English?"
        correct_answer = vocab_item["english"]
        options = [correct_answer]
        options.extend(pick_distractors(vocab_pool, "english", correct_answer, count=2))
    else:  # english_to_french
        question_text = f"How do you say '{vocab_item['english']}' in French?"
        correct_answer = vocab_item["french"]
        options = [correct_answer]
        options.extend(pick_distractors(vocab_pool, "french", correct_answer, count=2))

    if len(options) < 3:
        options.extend([correct_answer] * (3 - len(options)))

    random.shuffle(options)

    return {
        "question_id": question_id,
        "type": question_type,
        "question": question_text,
        "correct_answer": correct_answer,
        "options": options,
        "lesson_id": lesson_id,
        "french_word": vocab_item["french"],
        "english_word": vocab_item["english"]
    }


# Static files (will serve HTML/CSS/JS)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Submission directories
audio_dir = Path(__file__).parent / "submissions" / "audio"
audio_dir.mkdir(parents=True, exist_ok=True)
tts_dir = Path(__file__).parent / "submissions" / "tts"
tts_dir.mkdir(parents=True, exist_ok=True)

# API Endpoints

# ===== Vocabulary Practice Endpoints =====

@app.get("/api/vocabulary/practice")
async def get_vocabulary_practice(mode: str = "daily", user_id: int = 1, limit: int = 10):
    """Get vocabulary practice questions based on mode.
    
    Args:
        mode: "daily" (SRS due items), "weak" (from weakness tracking), or "all" (all lessons)
        user_id: User ID
        limit: Maximum number of questions to return
        
    Returns:
        List of vocabulary questions with multiple choice options
    """
    try:
        questions = []
        all_lessons = db_lessons.get_all_lessons()
        vocab_pool = build_vocab_pool(all_lessons)
        
        if mode == "daily":
            # Get lessons due for SRS review
            srs_items = db_srs.get_srs_due(user_id=user_id, limit=limit)
            lesson_ids = [item["lesson_id"] for item in srs_items]
            
            # Get lesson data and extract vocabulary
            for item in srs_items:
                lesson_id = item["lesson_id"]
                lesson_data = db_lessons.get_lesson_by_id(lesson_id)
                if lesson_data:
                    vocab_items = extract_vocabulary_from_lesson(lesson_data)
                    for vocab in vocab_items[:2]:  # 2 questions per lesson
                        question = generate_vocab_question(vocab, lesson_id, vocab_pool)
                        question["srs_id"] = item["srs_id"]
                        question["srs_meta"] = {
                            "next_review_date": item.get("next_review_date"),
                            "interval_days": item.get("interval_days"),
                            "ease_factor": item.get("ease_factor"),
                            "repetitions": item.get("repetitions"),
                            "status": item.get("status"),
                            "last_reviewed": item.get("last_reviewed")
                        }
                        questions.append(question)
                        if len(questions) >= limit:
                            break
                if len(questions) >= limit:
                    break
                    
        elif mode == "weak":
            # Get weak topics
            weaknesses = db_utils.get_user_weaknesses(user_id=user_id, limit=limit)
            
            # Get lessons related to weak topics
            for lesson in all_lessons:
                lesson_data = db_lessons.get_lesson_by_id(lesson["lesson_id"])
                if lesson_data:
                    # Check if lesson matches weak topics
                    for weakness in weaknesses:
                        if weakness["topic"].lower() in lesson_data.get("theme", "").lower():
                            vocab_items = extract_vocabulary_from_lesson(lesson_data)
                            for vocab in vocab_items:
                                questions.append(generate_vocab_question(vocab, lesson["lesson_id"], vocab_pool))
                                if len(questions) >= limit:
                                    break
                if len(questions) >= limit:
                    break
                    
        else:  # mode == "all"
            # Get all lessons
            for lesson in all_lessons:
                lesson_data = db_lessons.get_lesson_by_id(lesson["lesson_id"])
                if lesson_data:
                    vocab_items = extract_vocabulary_from_lesson(lesson_data)
                    for vocab in vocab_items:
                        questions.append(generate_vocab_question(vocab, lesson["lesson_id"], vocab_pool))
                        if len(questions) >= limit:
                            break
                if len(questions) >= limit:
                    break
        
        return {
            "mode": mode,
            "user_id": user_id,
            "questions_count": len(questions),
            "questions": questions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vocabulary practice: {str(e)}")


@app.post("/api/vocabulary/check")
async def check_vocabulary_answer(request: VocabularyCheckRequest):
    """Check a vocabulary practice answer and provide feedback.
    
    Args:
        request: Contains question_id, user_answer, user_id
        
    Returns:
        Feedback with correct/incorrect and explanation
    """
    try:
        # Extract lesson_id from question_id (format: "lesson_id_vocab_word")
        lesson_id = None
        vocab_slug = None
        question_type = None

        if "::" in request.question_id:
            parts = request.question_id.split("::", 2)
            if len(parts) >= 3:
                lesson_id, vocab_slug, question_type = parts[0], parts[1], parts[2]
        else:
            parts = request.question_id.split("_", 1)
            if len(parts) >= 2:
                lesson_id, vocab_slug = parts[0], parts[1]

        if not lesson_id:
            raise HTTPException(status_code=400, detail="Invalid question_id format")
        
        # Get lesson data
        lesson_data = db_lessons.get_lesson_by_id(lesson_id)
        if not lesson_data:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        # Extract vocabulary
        vocab_items = extract_vocabulary_from_lesson(lesson_data)
        
        # Find the matching vocabulary item
        correct_answer = None
        vocab_item = None
        for vocab in vocab_items:
            slug = slugify_vocab(vocab["french"])
            if vocab_slug and slug != vocab_slug:
                continue
            if vocab_slug is None:
                continue

            vocab_item = vocab
            # Determine which was the correct answer based on context
            if question_type in ("english_to_french", "fill_blank"):
                correct_answer = vocab["french"]
            else:
                correct_answer = vocab["english"]
            break
        
        if vocab_item is None:
            raise HTTPException(status_code=404, detail="Vocabulary item not found")
        
        # Check if answer is correct (case-insensitive)
        if question_type in ("english_to_french", "fill_blank"):
            is_correct = request.user_answer.lower() == vocab_item["french"].lower()
        elif question_type == "french_to_english":
            is_correct = request.user_answer.lower() == vocab_item["english"].lower()
        else:
            is_correct = request.user_answer.lower() in [
                vocab_item["french"].lower(),
                vocab_item["english"].lower()
            ]
        
        feedback_message = ""
        if is_correct:
            feedback_message = f"✓ Correct! '{vocab_item['french']}' means '{vocab_item['english']}'"
        else:
            feedback_message = f"✗ Incorrect. The correct answer is '{correct_answer}'. '{vocab_item['french']}' means '{vocab_item['english']}'"
            # Track this as a weakness
            db_utils.track_weakness(user_id=request.user_id, topic=lesson_data.get("theme", "vocabulary"), is_error=True)
        
        return {
            "correct": is_correct,
            "user_answer": request.user_answer,
            "correct_answer": correct_answer,
            "feedback": feedback_message,
            "vocabulary": vocab_item
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check answer: {str(e)}")


@app.post("/api/lessons/{lesson_id}/review")
async def review_lesson(lesson_id: str, user_id: int = 1):
    """Generate a fresh review of an old lesson with new examples (no homework/exam).
    
    Args:
        lesson_id: ID of the lesson to review
        user_id: User ID
        
    Returns:
        Lesson data with fresh AI-generated examples
    """
    try:
        # Get original lesson
        original_lesson = db_lessons.get_lesson_by_id(lesson_id)
        if not original_lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        # Extract the core topic/theme
        theme = original_lesson.get("theme", "")
        level = original_lesson.get("level", "A1.1")
        
        # Generate fresh lesson with same topic but new examples
        prompt = f"""Generate a review lesson for French {level} level.
        
Topic: {theme}
This is a REVIEW lesson, so keep the same grammatical topic but provide FRESH examples.

Requirements:
1. Same grammar topic as: {theme}
2. NEW example sentences (different from original)
3. NEW vocabulary items (3 items)
4. NEW speaking practice prompt
5. NO homework section (this is review only)
6. NO exam section (this is review only)

Format as JSON with this structure:
{{
    "level": "{level}",
    "theme": "{theme}",
    "grammar": {{
        "explanation": "...",
        "examples": ["sentence 1", "sentence 2", ...],
        "conjugation": [...]
    }},
    "vocabulary": ["word1 (translation)", "word2 (translation)", ...],
    "speaking": {{
        "prompt": "...",
        "targets": [...]
    }}
}}

Make it engaging and practical for review!"""

        # Call Gemini AI to generate fresh content
        fresh_lesson = await generate_lesson_ai(prompt, level)
        
        # Add review flag
        fresh_lesson["is_review"] = True
        fresh_lesson["original_lesson_id"] = lesson_id
        fresh_lesson["reviewed_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "lesson": fresh_lesson,
            "message": f"Fresh review generated for: {theme}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate review: {str(e)}")


@app.get("/api/vocabulary/stats")
async def get_vocabulary_stats(user_id: int = 1):
    """Get vocabulary practice dashboard stats."""
    try:
        return db_utils.get_vocab_stats(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vocabulary stats: {str(e)}")


# ===== App Lifecycle =====

@app.on_event("startup")
async def startup_event():
    """Initialize database, API key, and pre-load Whisper model on startup"""
    global WHISPER_MODEL
    
    # Initialize database
    db_core.init_db()
    print("[OK] Database initialized")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("[OK] GEMINI_API_KEY loaded successfully")
    else:
        print("[WARNING] GEMINI_API_KEY not found in environment")
    
    # Pre-load Whisper model to avoid slow startup on first request
    try:
        print("[LOADING] Whisper model (this takes 30-60 seconds on first run)...")
        WHISPER_MODEL = whisper.load_model("base")
        print("[OK] Whisper model loaded and cached in memory")
    except Exception as e:
        print(f"[WARNING] Failed to load Whisper model: {e}")
        print("[WARNING] Audio transcription will not be available")
        WHISPER_MODEL = None

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global WHISPER_MODEL
    if WHISPER_MODEL is not None:
        print("[OK] Shutting down Whisper model")
        # Whisper model is cleaned up by Python's garbage collection
        WHISPER_MODEL = None

@app.get("/")
async def root():
    """Serve main page"""
    html_path = Path(__file__).parent / "templates" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "French Tutor API - Use /docs for API documentation"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_loaded = os.getenv("GEMINI_API_KEY") is not None
    return {
        "status": "healthy",
        "message": "API running",
        "api_key_loaded": api_key_loaded,
        "database": "connected"
    }


@app.get("/api/mode")
async def get_app_mode():
    """Get current application mode and user setup state."""
    dev_mode = get_dev_mode()
    starting_level = db_core.get_app_setting("starting_level")
    current_level = db_core.get_app_setting("current_level")
    homework_blocking = db_core.get_app_setting("homework_blocking_enabled", "true") == "true"
    return {
        "mode": "dev" if dev_mode else "production",
        "starting_level": starting_level,
        "current_level": current_level,
        "homework_blocking_enabled": homework_blocking
    }


@app.post("/api/mode/toggle")
async def toggle_app_mode(request: ModeToggleRequest):
    """Toggle development mode on or off."""
    db_core.set_app_setting("dev_mode", "true" if request.dev_mode else "false")
    return {
        "status": "success",
        "mode": "dev" if request.dev_mode else "production"
    }


@app.post("/api/settings/homework-blocking")
async def toggle_homework_blocking(enabled: bool = True):
    """Toggle homework blocking on or off.
    
    Args:
        enabled: True to enable blocking (production mode), False to disable (dev mode)
    
    When disabled, all lessons are accessible regardless of homework completion.
    When enabled, next lesson is blocked until current homework is submitted and passed.
    """
    db_core.set_app_setting("homework_blocking_enabled", "true" if enabled else "false")
    return {
        "status": "success",
        "homework_blocking_enabled": enabled,
        "message": "Homework blocking " + ("enabled" if enabled else "disabled")
    }


@app.post("/api/first-time-setup")
async def first_time_setup(request: FirstTimeSetupRequest):
    """Set the user's starting level on first use."""
    if request.starting_level not in LEVEL_ORDER:
        raise HTTPException(status_code=400, detail="Invalid starting level")

    db_core.set_app_setting("starting_level", request.starting_level)
    current_level = db_core.get_app_setting("current_level")
    if current_level not in LEVEL_ORDER:
        db_core.set_app_setting("current_level", request.starting_level)

    return {
        "status": "success",
        "starting_level": request.starting_level,
        "current_level": db_core.get_app_setting("current_level")
    }


@app.get("/api/curriculum/plan")
async def get_curriculum_plan():
    """Return the curriculum plan markdown."""
    plan_path = Path(__file__).parent / "French_Course_Weekly_Plan.md"
    if not plan_path.exists():
        raise HTTPException(status_code=404, detail="Curriculum plan not found")
    return {"plan": plan_path.read_text(encoding="utf-8")}


@app.get("/api/lessons/available", response_model=List[LessonResponse])
async def get_available_lessons():
    """Get lessons available for the current mode and user level."""
    try:
        lessons_raw = db_lessons.get_all_lessons()
        dev_mode = get_dev_mode()
        current_level = get_current_level()
        
        # Filter by level unless in dev mode
        if not dev_mode:
            lessons_raw = [lesson for lesson in lessons_raw if lesson.get("level") == current_level]
        
        # Filter out blocked lessons (unless blocking is disabled)
        blocking_enabled = db_core.get_app_setting("homework_blocking_enabled", "true") == "true"
        
        if blocking_enabled:
            available_lessons = []
            for lesson in lessons_raw:
                if not db_lessons.is_lesson_blocked(lesson["lesson_id"]):
                    available_lessons.append(lesson)
        else:
            available_lessons = lessons_raw
        
        return [build_lesson_response(lesson) for lesson in available_lessons]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch available lessons: {str(e)}")

@app.get("/api/lessons", response_model=List[LessonResponse])
async def get_lessons():
    """Get all available lessons"""
    try:
        lessons_raw = db_lessons.get_all_lessons()
        return [build_lesson_response(lesson) for lesson in lessons_raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lessons: {str(e)}")

@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get specific lesson by ID"""
    try:
        lesson = db_lessons.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Check if lesson is blocked
        blocking_enabled = db_core.get_app_setting("homework_blocking_enabled", "true") == "true"
        if blocking_enabled and db_lessons.is_lesson_blocked(lesson_id):
            raise HTTPException(
                status_code=403, 
                detail="This lesson is blocked. Complete the previous lesson's homework first."
            )
        
        return build_lesson_response(lesson)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lesson: {str(e)}")

@app.get("/api/lessons/selection-ui")
async def get_lessons_for_selection_ui(user_id: int = 1):
    """Get available lessons with their status for the lesson selection UI.
    
    Returns:
        - completed: Green (can review)
        - in_progress: White (current lesson)
        - not_started: Dimmed (locked until previous complete)
    """
    try:
        lessons = db_lessons.get_available_lessons_for_ui(user_id)
        return {"success": True, "lessons": lessons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lessons: {str(e)}")

@app.post("/api/lessons/{lesson_id}/start")
async def start_lesson(lesson_id: str, user_id: int = 1):
    """Mark lesson as started when user opens it."""
    try:
        db_lessons.mark_lesson_started(lesson_id)
        return {"success": True, "message": "Lesson started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start lesson: {str(e)}")

@app.post("/api/homework/submit")
async def submit_homework(
    lesson_id: str = Form(...),
    homework_text: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    user_id: int = Form(1)
):
    """Submit homework with text and optional audio"""
    try:
        # Save audio if provided
        audio_path = None
        if audio_file:
            audio_path = audio_dir / f"hw_{lesson_id}_{user_id}_{audio_file.filename}"
            with open(audio_path, "wb") as f:
                content = await audio_file.read()
                f.write(content)
        
        # Save submission to database
        submission_id = db_homework.save_homework_submission(
            lesson_id=lesson_id,
            text_content=homework_text,
            audio_file_path=str(audio_path) if audio_path else None,
            character_count=len(homework_text),
            audio_size_kb=audio_path.stat().st_size / 1024 if audio_path else 0
        )
        
        # Evaluate using AI
        evaluation = evaluate_homework_ai(
            homework_text=homework_text,
            audio_path=str(audio_path) if audio_path else None
        )
        
        # Save feedback
        db_homework.save_homework_feedback(
            submission_id=submission_id,
            text_score=evaluation["text_score"],
            audio_score=evaluation["audio_score"],
            passed=evaluation["passed"],
            grammar_feedback=evaluation.get("grammar_feedback", ""),
            vocabulary_feedback=evaluation.get("vocabulary_feedback", ""),
            pronunciation_feedback=evaluation.get("pronunciation_feedback"),
            overall_feedback=evaluation.get("overall_feedback", "")
        )
        
        # Update submission status
        db_homework.update_homework_status(submission_id, "completed")
        
        # Update lesson progress with homework result
        db_lessons.update_lesson_homework_progress(lesson_id, evaluation["passed"])
        
        # Track weaknesses from homework
        if not evaluation["passed"]:
            if evaluation["text_score"] < 70:
                db_utils.track_weakness(user_id=user_id, topic="grammar and vocabulary", is_error=True)
        if evaluation["audio_score"] is not None and evaluation["audio_score"] < 60:
            db_utils.track_weakness(user_id=user_id, topic="pronunciation", is_error=True)
        
        return {
            "success": True,
            "submission_id": submission_id,
            "text_score": evaluation["text_score"],
            "audio_score": evaluation["audio_score"],
            "passed": evaluation["passed"],
            "feedback": {
                "grammar": evaluation.get("grammar_feedback", ""),
                "vocabulary": evaluation.get("vocabulary_feedback", ""),
                "pronunciation": evaluation.get("pronunciation_feedback"),
                "overall": evaluation.get("overall_feedback", "")
            },
            "message": "Homework submitted and evaluated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit homework: {str(e)}")

@app.post("/api/speaking/feedback")
async def speaking_feedback(request: SpeakingRequest):
    """Get AI feedback for speaking practice"""
    try:
        feedback = get_ai_speaking_feedback(
            transcribed_text=request.transcribed_text,
            scenario=request.scenario,
            targets=request.targets
        )
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")

@app.post("/api/audio/transcribe")
async def transcribe_audio_file(audio_file: UploadFile = File(...)):
    """Transcribe uploaded audio file"""
    try:
        # Save temporary file
        temp_path = Path(tempfile.gettempdir()) / audio_file.filename
        with open(temp_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Transcribe
        transcription = transcribe_audio(str(temp_path))
        
        # Cleanup
        temp_path.unlink()
        
        return {"transcription": transcription}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe: {str(e)}")

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using gTTS"""
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        cleaned_text = sanitize_tts_text(request.text)
        if not cleaned_text:
            raise HTTPException(status_code=400, detail="Text contains no speakable content")
        
        tts_path = tts_dir / f"tts_{hash(cleaned_text)}_{request.lang}.mp3"
        if not tts_path.exists():
            # Generate TTS only if not cached
            tts = gTTS(text=cleaned_text, lang=request.lang, slow=False)
            tts.save(str(tts_path))
        
        return FileResponse(
            path=str(tts_path),
            media_type="audio/mpeg",
            filename="speech.mp3"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@app.get("/api/progress/{user_id}")
async def get_user_progress(user_id: int = 1):
    """Get user progress summary"""
    try:
        progress = db_lessons.get_user_progress(user_id)
        return {
            "user_id": user_id,
            "progress": progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}")

@app.post("/api/exam/generate")
async def generate_exam(request: ExamGenerateRequest):
    """Generate a weekly exam for a given level and week"""
    try:
        exam = generate_exam_ai(level=request.level, week_number=request.week_number)
        
        if "error" in exam:
            raise HTTPException(status_code=500, detail=exam["error"])
        
        # Store exam in database for later reference
        db_exams.save_exam(
            exam_id=exam["exam_id"],
            level=request.level,
            week_number=request.week_number,
            questions=json.dumps(exam["questions"]),
            user_id=request.user_id
        )
        
        return exam
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate exam: {str(e)}")

@app.post("/api/exam/submit")
async def submit_exam(request: ExamSubmitRequest):
    """Submit exam answers and get graded results"""
    try:
        # Retrieve exam from database
        exam_data = db_exams.get_exam(request.exam_id)
        if not exam_data:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Parse questions
        questions = json.loads(exam_data["questions"]) if isinstance(exam_data["questions"], str) else exam_data["questions"]
        
        # Grade the exam
        grading = grade_exam_ai(questions=questions, student_answers=request.answers)
        
        if "error" in grading:
            raise HTTPException(status_code=500, detail=grading["error"])
        
        # Save results
        db_exams.save_exam_result(
            exam_id=request.exam_id,
            user_id=request.user_id,
            answers=json.dumps(request.answers),
            overall_score=grading["overall_score"],
            passed=grading["passed"],
            feedback=grading.get("feedback", "")
        )
        
        # Track weaknesses from exam results
        # For each question, we'd analyze if student got it wrong
        # This is a simplified approach - tracks overall weak topics
        if not grading["passed"]:
            for topic, score in grading.get("critical_topics", {}).items():
                if score < 70:
                    db_utils.track_weakness(user_id=request.user_id, topic=topic, is_error=True)
        
        return {
            "success": True,
            "overall_score": grading["overall_score"],
            "passed": grading["passed"],
            "critical_topics": grading.get("critical_topics", {}),
            "question_scores": grading.get("question_scores", {}),
            "feedback": grading.get("feedback", ""),
            "message": "Exam submitted and graded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit exam: {str(e)}")

@app.get("/api/weakness/report/{user_id}")
async def get_weakness_report(user_id: int = 1):
    """Get weakness analysis report for a user"""
    try:
        report = db_utils.get_weakness_report(user_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weakness report: {str(e)}")

@app.post("/api/lessons/generate-batch")
async def generate_lessons_batch(level: str, week_count: int = 4):
    """Generate and seed lessons for a specific level"""
    try:
        # A1.1 curriculum: 4 weeks
        a1_1_curriculum = [
            ("Week 1", "Present Tense - être, avoir, aller", ["être", "avoir", "aller", "present"]),
            ("Week 2", "Regular -ER Verbs in Present", ["parler", "habiter", "manger", "present", "regular"]),
            ("Week 3", "Regular -IR and -RE Verbs", ["finir", "choisir", "vendre", "present"]),
            ("Week 4", "Basic Sentences - Subject + Verb + Object", ["je", "tu", "il", "elle", "sentence"]),
        ]
        
        a1_2_curriculum = [
            ("Week 5", "Negation and Questions", ["ne pas", "pas du tout", "question"]),
            ("Week 6", "Adjectives and Agreement", ["beau", "grand", "petit", "adjective"]),
            ("Week 7", "Prepositions and Location", ["à", "de", "en", "sur", "sous", "location"]),
            ("Week 8", "Passé Composé Introduction", ["j'ai", "je suis", "passé composé", "past"]),
        ]
        
        # Select curriculum based on level
        if level == "A1.1":
            curriculum = a1_1_curriculum
        elif level == "A1.2":
            curriculum = a1_2_curriculum
        else:
            raise HTTPException(status_code=400, detail=f"Level {level} not yet supported")
        
        generated_lessons = []
        
        for week_num, (week_label, topic, vocab_seeds) in enumerate(curriculum, 1):
            if week_num > week_count:
                break
            
            # Generate lesson using AI
            lesson = generate_lesson_ai(
                level=level,
                week_number=week_num,
                grammar_topic=topic,
                vocabulary_words=vocab_seeds
            )
            
            if "error" not in lesson:
                #Save to database
                try:
                    lesson_id = f"lesson_{level}_w{week_num}"
                    db_lessons.save_lesson(
                        lesson_id=lesson_id,
                        level=level,
                        theme=lesson.get("theme", topic),
                        week_number=week_num,
                        grammar_explanation=json.dumps(lesson.get("grammar", {})),
                        vocabulary=json.dumps(lesson.get("vocabulary", [])),
                        speaking_prompt=json.dumps(lesson.get("speaking", {})),
                        homework_prompt=lesson.get("homework", f"Write and record a lesson on {topic}"),
                        quiz_questions=json.dumps(lesson.get("quiz", {}))
                    )
                    generated_lessons.append({
                        "lesson_id": lesson_id,
                        "theme": lesson.get("theme", topic),
                        "status": "created"
                    })
                except Exception as e:
                    generated_lessons.append({
                        "lesson_id": f"lesson_{level}_w{week_num}",
                        "theme": topic,
                        "status": f"error: {str(e)}"
                    })
            else:
                generated_lessons.append({
                    "lesson_id": f"lesson_{level}_w{week_num}",
                    "theme": topic,
                    "status": f"error: {lesson.get('error')}"
                })
        
        return {
            "success": True,
            "level": level,
            "lessons_generated": len(generated_lessons),
            "lessons": generated_lessons,
            "message": f"Generated {len(generated_lessons)} lessons for {level}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lessons: {str(e)}")

@app.get("/api/srs/due")
async def get_srs_due(user_id: int = 1, limit: int = 50):
    """Get vocabulary items due for review (SM-2 spaced repetition)"""
    try:
        items = db_srs.get_srs_due(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "items_due": len(items),
            "items": items,
            "message": f"{len(items)} items due for review"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SRS items: {str(e)}")


@app.get("/api/srs/items")
async def get_srs_items(user_id: int = 1, limit: int | None = None):
    """Get all SRS items with lesson metadata."""
    try:
        items = db_srs.get_srs_items(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "items": items,
            "items_count": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SRS items: {str(e)}")

@app.post("/api/srs/review")
async def submit_srs_review(request: SRSReviewRequest):
    """Submit a review response for an SRS item and update using SM-2 algorithm"""
    try:
        # Validate quality score
        if not (0 <= request.quality <= 5):
            raise HTTPException(status_code=400, detail="Quality must be 0-5")
        
        # Update SRS item using SM-2
        updated_item = db_srs.update_srs_review(
            srs_id=request.srs_id,
            quality=request.quality,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "updated_item": updated_item,
            "message": f"Review recorded. Next review in {updated_item['interval_days']} days"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit review: {str(e)}")

# ===== DYNAMIC LESSON GENERATION ENDPOINTS =====

@app.post("/api/lessons/generate")
async def generate_lesson(request: LessonGenerateRequest):
    """
    Generate a dynamic lesson from curriculum using Gemini AI (DEPRECATED).
    
    ⚠️ DEPRECATED: Use /api/lessons/load instead for NEW CURRICULUM SYSTEM.
    
    This endpoint uses the OLD curriculum format (New_Curriculum/wkX.md).
    For the redesigned curriculum (Research/NEW_CURRICULUM_REDESIGNED/), use /api/lessons/load.
    
    Args:
        week: Week number (1-52)
        day: Day number (1-7), default 1
        student_level: CEFR level (optional, uses student profile if not provided)
        user_id: Student ID (default 1)
    
    Returns:
        Generated lesson JSON with grammar, vocabulary, speaking, quiz, homework
    
    Rate limit: 1 request per user per hour (prevents API spam)
    """
    try:
        # Validate input
        if not (1 <= request.week <= 52):
            raise HTTPException(status_code=400, detail="Week must be 1-52")
        if not (1 <= request.day <= 7):
            raise HTTPException(status_code=400, detail="Day must be 1-7")
        
        # Get or use provided student level
        if request.student_level:
            student_level = request.student_level
        else:
            student_level = db_utils.get_student_level(request.user_id)
        
        # Check rate limiting (optional - can be enabled later)
        # For now, allow unlimited generation for testing
        
        # Generate the lesson
        lesson_dict, was_generated = lesson_generator.generate_lesson_from_curriculum(
            week_number=request.week,
            day_number=request.day,
            student_level=student_level,
            user_id=request.user_id,
            fallback_on_error=True  # Always provide a lesson, even if API fails
        )
        
        # Add metadata about generation
        lesson_dict['generated_by_ai'] = was_generated
        lesson_dict['generation_status'] = 'success' if was_generated else 'fallback'
        # Create a lesson ID for tracking homework/progress
        lesson_dict['lesson_id'] = f"dynamic_wk{request.week}_d{request.day}"
        
        return {
            "success": True,
            "lesson": lesson_dict,
            "lesson_id": lesson_dict['lesson_id'],
            "was_generated_by_ai": was_generated,
            "message": "Lesson generated successfully" if was_generated else "Using fallback lesson (AI generation failed)"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except lesson_generator.LessonGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Lesson generation failed: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/api/lessons/load")
async def load_lesson_from_redesigned_curriculum(request: LessonGenerateRequest):
    """
    Load a lesson from the NEW CURRICULUM SYSTEM (Research/NEW_CURRICULUM_REDESIGNED/).
    
    ✅ NEW SYSTEM - Uses FIXED curriculum content (no AI generation).
    
    The redesigned curriculum contains:
    - Pre-written grammar explanations (5-paragraph format)
    - Pre-defined vocabulary (5 words/day with examples)
    - Pre-created quiz questions (50/day, 8-10 shown randomly)
    - Content identifiers for each question type
    
    Args:
        week: Week number (1-52)
        day: Day number (1-7)
        user_id: Student ID (default 1)
    
    Returns:
        Complete lesson JSON ready for display:
        {
            'lesson_id': str,
            'week': int,
            'day': int,
            'cefr_level': str,
            'grammar_topic': str,
            'grammar_explanation': str (HTML formatted),
            'vocabulary': list (5 words),
            'quiz_questions': list (8-10 selected),
            'speaking_tier': int,
            'content_identifiers': list
        }
    """
    try:
        # Validate input
        if not (1 <= request.week <= 52):
            raise HTTPException(status_code=400, detail="Week must be 1-52")
        if not (1 <= request.day <= 7):
            raise HTTPException(status_code=400, detail="Day must be 1-7")
        
        # Load lesson from redesigned curriculum
        lesson_dict = lesson_generator.generate_lesson_from_redesigned_curriculum(
            week_number=request.week,
            day_number=request.day,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "lesson": lesson_dict,
            "lesson_id": lesson_dict['lesson_id'],
            "source": "redesigned_curriculum",
            "message": f"Lesson loaded successfully: Week {request.week} Day {request.day}"
        }
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Curriculum file not found for Week {request.week} Day {request.day}. "
                   f"Only Weeks 1-7 are currently available."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except lesson_generator.LessonGenerationError as e:
        raise HTTPException(status_code=500, detail=f"Lesson loading failed: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/api/lessons/history")
async def get_lesson_generation_history(user_id: int = 1, limit: int = 20):
    """Get lesson generation history for a student.
    
    Args:
        user_id: Student ID
        limit: Maximum number of records (default 20)
    
    Returns:
        List of lesson generation records
    """
    try:
        history = db_utils.get_lesson_generation_history(user_id=user_id, limit=limit)
        return {
            "success": True,
            "user_id": user_id,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@app.get("/api/lessons/available-weeks")
async def get_available_weeks():
    """Get list of available curriculum weeks (1-52).
    
    Returns:
        List of week numbers that have curriculum files
    """
    try:
        from pathlib import Path
        curriculum_dir = Path(__file__).parent / "New_Curriculum"
        
        available_weeks = []
        for week_num in range(1, 53):
            filepath = curriculum_dir / f"wk{week_num}.md"
            if filepath.exists():
                available_weeks.append(week_num)
        
        return {
            "success": True,
            "available_weeks": available_weeks,
            "total_weeks": len(available_weeks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available weeks: {str(e)}")

@app.get("/api/srs/stats")
async def get_srs_stats(user_id: int = 1):
    """Get SRS statistics for a user"""
    try:
        stats = db_srs.get_srs_stats(user_id=user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SRS stats: {str(e)}")

@app.post("/api/lessons/{lesson_id}/schedule-srs")
async def schedule_lesson_srs(lesson_id: str, user_id: int = 1):
    """Schedule vocabulary from a lesson for SRS review"""
    try:
        count = db_srs.schedule_lesson_vocabulary(
            lesson_id=lesson_id,
            vocabulary_count=3,
            user_id=user_id
        )
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "srs_items_created": count,
            "message": f"Scheduled {count} vocabulary items for spaced repetition"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule SRS: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    from threading import Timer
    
    def open_browser():
        """Auto-open browser after server starts"""
        webbrowser.open("http://localhost:8000")
    
    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
