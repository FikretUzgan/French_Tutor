"""
French Tutor - FastAPI Backend
High-performance web application for French language learning
"""

import os
from pathlib import Path
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
import db
from google import genai
from google.genai import types
import whisper
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile

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

# Helper Functions
def load_whisper_model():
    """Load Whisper model with caching"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        WHISPER_MODEL = whisper.load_model("base")
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
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
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
        client = genai.Client(api_key=api_key)
        
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=lesson_prompt
        )
        
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
        client = genai.Client(api_key=api_key)
        
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=exam_prompt
        )
        
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
        client = genai.Client(api_key=api_key)
        
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=grade_prompt
        )
        
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
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

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
@app.on_event("startup")
async def startup_event():
    """Initialize database and check API key on startup"""
    db.init_db()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("[OK] GEMINI_API_KEY loaded successfully")
    else:
        print("[WARNING] GEMINI_API_KEY not found in environment")
    print("[OK] Database initialized")

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

@app.get("/api/lessons", response_model=List[LessonResponse])
async def get_lessons():
    """Get all available lessons"""
    try:
        lessons_raw = db.get_all_lessons()
        
        # Transform to match frontend expectations
        lessons = []
        for lesson in lessons_raw:
            # Build content object from schema columns
            content = {
                "grammar": json.loads(lesson.get("grammar_explanation", "{}")) if lesson.get("grammar_explanation") else {},
                "vocabulary": json.loads(lesson.get("vocabulary", "[]")) if lesson.get("vocabulary") else [],
                "speaking": json.loads(lesson.get("speaking_prompt", "{}")) if lesson.get("speaking_prompt") else {},
                "homework": lesson.get("homework_prompt", ""),
                "quiz": json.loads(lesson.get("quiz_questions", "{}")) if lesson.get("quiz_questions") else {}
            }
            
            lessons.append(LessonResponse(
                lesson_id=lesson["lesson_id"],
                title=lesson.get("theme", "Untitled Lesson"),
                level=lesson.get("level", "Unknown"),
                description=f"Week {lesson.get('week_number', 'N/A')} - {lesson.get('theme', '')}",
                content=content
            ))
        
        return lessons
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lessons: {str(e)}")

@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get specific lesson by ID"""
    try:
        lesson = db.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Build content object from schema columns
        content = {
            "grammar": json.loads(lesson.get("grammar_explanation", "{}")) if lesson.get("grammar_explanation") else {},
            "vocabulary": json.loads(lesson.get("vocabulary", "[]")) if lesson.get("vocabulary") else [],
            "speaking": json.loads(lesson.get("speaking_prompt", "{}")) if lesson.get("speaking_prompt") else {},
            "homework": lesson.get("homework_prompt", ""),
            "quiz": json.loads(lesson.get("quiz_questions", "{}")) if lesson.get("quiz_questions") else {}
        }
        
        return LessonResponse(
            lesson_id=lesson["lesson_id"],
            title=lesson.get("theme", "Untitled Lesson"),
            level=lesson.get("level", "Unknown"),
            description=f"Week {lesson.get('week_number', 'N/A')} - {lesson.get('theme', '')}",
            content=content
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lesson: {str(e)}")

@app.post("/api/homework/submit")
async def submit_homework(
    lesson_id: int = Form(...),
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
        submission_id = db.save_homework_submission(
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
        db.save_homework_feedback(
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
        db.update_homework_status(submission_id, "completed")
        
        # Track weaknesses from homework
        if not evaluation["passed"]:
            if evaluation["text_score"] < 70:
                db.track_weakness(user_id=user_id, topic="grammar and vocabulary", is_error=True)
        if evaluation["audio_score"] is not None and evaluation["audio_score"] < 60:
            db.track_weakness(user_id=user_id, topic="pronunciation", is_error=True)
        
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
        
        # Generate TTS
        tts = gTTS(text=cleaned_text, lang=request.lang, slow=False)
        tts_path = tts_dir / f"tts_{hash(cleaned_text)}_{request.lang}.mp3"
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
        progress = db.get_user_progress(user_id)
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
        db.save_exam(
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
        exam_data = db.get_exam(request.exam_id)
        if not exam_data:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Parse questions
        questions = json.loads(exam_data["questions"]) if isinstance(exam_data["questions"], str) else exam_data["questions"]
        
        # Grade the exam
        grading = grade_exam_ai(questions=questions, student_answers=request.answers)
        
        if "error" in grading:
            raise HTTPException(status_code=500, detail=grading["error"])
        
        # Save results
        db.save_exam_result(
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
                    db.track_weakness(user_id=request.user_id, topic=topic, is_error=True)
        
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
        report = db.get_weakness_report(user_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weakness report: {str(e)}")

@app.post("/api/lessons/generate")
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
                    db.save_lesson(
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
        items = db.get_srs_due(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "items_due": len(items),
            "items": items,
            "message": f"{len(items)} items due for review"
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
        updated_item = db.update_srs_item(
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

@app.get("/api/srs/stats")
async def get_srs_stats(user_id: int = 1):
    """Get SRS statistics for a user"""
    try:
        stats = db.get_srs_stats(user_id=user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SRS stats: {str(e)}")

@app.post("/api/lessons/{lesson_id}/schedule-srs")
async def schedule_lesson_srs(lesson_id: str, user_id: int = 1):
    """Schedule vocabulary from a lesson for SRS review"""
    try:
        count = db.schedule_lesson_vocabulary(
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
