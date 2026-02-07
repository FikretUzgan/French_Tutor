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
        targets_list = "\\n".join(f"- {t}" for t in targets)
        prompt = f"""You are a French language tutor. Evaluate this student's response in a conversation scenario.

Scenario: {scenario}
Conversation goals:
{targets_list}

Student said: "{transcribed_text}"

Provide concise, encouraging feedback in this format:
✅ What was good (grammar, vocabulary, relevance)
⚠️ What could be improved
💡 Suggestion for next response

Keep it under 100 words, be supportive."""
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        feedback_text = response.text.strip()
        return f"📝 Your response: {transcribed_text}\\n\\n🤖 AI Feedback:\\n{feedback_text}"
    
    except Exception as e:
        return f"❌ Error getting AI feedback: {str(e)}"

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
            user_id=user_id,
            lesson_id=lesson_id,
            submission_text=homework_text,
            audio_path=str(audio_path) if audio_path else None
        )
        
        # Placeholder for AI evaluation (implement later)
        text_score = 75.0  # TODO: Implement AI evaluation
        audio_score = 70.0 if audio_path else None
        passed = (text_score >= 70 and (audio_score >= 60 if audio_score else True))
        
        # Save feedback
        db.save_homework_feedback(
            submission_id=submission_id,
            text_score=text_score,
            audio_score=audio_score,
            passed=passed,
            grammar_feedback="Evaluation pending",
            vocabulary_feedback="Evaluation pending",
            pronunciation_feedback="Audio analysis pending" if audio_path else None,
            overall_feedback="Your homework has been submitted successfully."
        )
        
        return {
            "success": True,
            "submission_id": submission_id,
            "text_score": text_score,
            "audio_score": audio_score,
            "passed": passed,
            "message": "Homework submitted successfully"
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
        
        # Generate TTS
        tts = gTTS(text=request.text, lang=request.lang, slow=False)
        tts_path = tts_dir / f"tts_{hash(request.text)}_{request.lang}.mp3"
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
