"""
API Helper Functions for French Tutor
Utility functions for lessons, exams, speaking, homework, and vocabulary
"""

import os
import json
import re
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Audio and AI imports (lazy loaded)
WHISPER_MODEL = None
genai_client = None


def load_whisper_model():
    """Get cached Whisper model (pre-loaded on startup)"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        try:
            import whisper
            print("[WARNING] Whisper model not pre-loaded. Loading now (this will be slow)...")
            WHISPER_MODEL = whisper.load_model("tiny")
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper: {e}")
            return None
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


# CEFR Level ordering
LEVEL_ORDER = ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2.1", "B2.2"]


def get_level_index(level: str) -> int:
    """Get index of CEFR level for ordering"""
    return LEVEL_ORDER.index(level) if level in LEVEL_ORDER else 0


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Whisper"""
    model = load_whisper_model()
    if not model:
        return "[Transcription failed]"
    try:
        result = model.transcribe(str(audio_path), language="fr")
        return result["text"].strip()
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return f"[Error: {str(e)}]"


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


def slugify_vocab(text: str) -> str:
    """Create a URL-safe identifier for vocabulary items."""
    return re.sub(r"\s+", "_", text.strip().lower())


# ===== Vocabulary Extraction =====

def extract_vocabulary_from_lesson(lesson_data: dict) -> list[dict]:
    """Extract vocabulary items from lesson data.
    
    Returns list of dicts with 'french', 'english' keys.
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
            vocab_list.append({"french": french_part, "english": english_part})
    
    return vocab_list


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
        item[field] for item in vocab_pool 
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


def generate_vocab_question(vocab_item: dict, lesson_id: str, vocab_pool: list[dict], 
                            question_type: Optional[str] = None) -> dict:
    """Generate a vocabulary practice question with multiple choice options."""
    import random
    
    if not question_type:
        question_type = random.choices(
            ["french_to_english", "english_to_french"],
            weights=[0.5, 0.5]
        )[0]
    
    question_id = f"{lesson_id}::{slugify_vocab(vocab_item['french'])}::{question_type}"
    
    if question_type == "french_to_english":
        question_text = f"What does '{vocab_item['french']}' mean?"
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


# ===== AI Functions (Gemini) =====

def get_gemini_client():
    """Get or initialize Gemini API client"""
    global genai_client
    if genai_client is None:
        try:
            import google.genai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai_client = genai.Client(api_key=api_key)
        except ImportError:
            print("[ERROR] google-genai not installed")
            return None
    return genai_client


def call_gemini_json(prompt: str, model: str = "gemini-2.5-flash") -> Optional[Dict[str, Any]]:
    """Call Gemini API and parse JSON response safely"""
    try:
        client = get_gemini_client()
        if not client:
            return None

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        text = response.text.strip()
        return json.loads(text)
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON from Gemini")
        return None
    except Exception as e:
        print(f"[ERROR] Gemini API error: {e}")
        return None


def get_ai_speaking_feedback(transcribed_text: str, scenario: str, targets: List[str]) -> str:
    """Generate AI feedback for speaking practice"""
    model = get_gemini_model("gemini-2.5-flash")
    if not model:
        return "⚠️ API not configured"
    
    try:
        targets_list = "\n".join(f"- {t}" for t in targets)
        prompt = f"""You are a French language tutor. Evaluate this student's response.

Scenario: {scenario}
Goals: {targets_list}
Student said: "{transcribed_text}"

Provide concise feedback in French only:
✅ Points positifs
⚠️ Améliorations
💡 Alternative response

Keep it under 80 words."""
        
        response = model.generate_content(prompt)
        return f"📝 Votre réponse: {transcribed_text}\n\n🤖 Retour:\n{response.text}"
    except Exception as e:
        return f"❌ Feedback error: {str(e)}"


def evaluate_homework_ai(homework_text: str, audio_path: Optional[str] = None) -> Dict[str, Any]:
    """Evaluate homework submission using AI"""
    client = get_gemini_client()
    if not client:
        return {
            "text_score": 50.0,
            "passed": False,
            "grammar_feedback": "API not configured",
            "vocabulary_feedback": "API not configured",
            "overall_feedback": "Evaluation pending"
        }
    
    try:
        prompt = f"""Grade this French homework:

"{homework_text}"

Check grammar, vocabulary, and accuracy. Score 0-100.
Respond with JSON only:
{{
    "text_score": <0-100>,
    "grammar_feedback": "<brief feedback>",
    "vocabulary_feedback": "<brief feedback>",
    "overall_feedback": "<overall assessment>"
}}"""
        
        result = call_gemini_json(prompt)
        if result is None:
            return {"text_score": 50.0, "passed": False, "grammar_feedback": "Grading failed"}
        
        text_score = result.get("text_score", 50.0)
        passed = text_score >= 70
        
        return {
            "text_score": text_score,
            "audio_score": None,
            "passed": passed,
            "grammar_feedback": result.get("grammar_feedback", ""),
            "vocabulary_feedback": result.get("vocabulary_feedback", ""),
            "pronunciation_feedback": None,
            "overall_feedback": result.get("overall_feedback", "")
        }
    except Exception as e:
        return {
            "text_score": 50.0,
            "passed": False,
            "overall_feedback": f"Error: {str(e)}"
        }


def grade_exam_ai(questions: List[Dict[str, Any]], student_answers: Dict[str, str]) -> Dict[str, Any]:
    """Grade exam answers using AI"""
    client = get_gemini_client()
    if not client:
        return {"overall_score": 0.0, "passed": False, "error": "API not configured"}
    
    try:
        grading_data = []
        for q in questions:
            grading_data.append({
                "id": q.get("question_id", ""),
                "type": q.get("question_type", ""),
                "question": q.get("question_text", ""),
                "correct": q.get("correct_answer", ""),
                "student": student_answers.get(q.get("question_id", ""), "")
            })
        
        prompt = f"""Grade these French exam answers fairly:

{json.dumps(grading_data, indent=2)}

Score each 0-1. Respond with JSON only:
{{
    "question_scores": {{}},
    "overall_percentage": <0-100>,
    "feedback": "<brief overall feedback>"
}}"""
        
        result = call_gemini_json(prompt)
        if result is None:
            return {"overall_score": 50.0, "passed": False, "feedback": "Grading failed"}
        
        overall_score = result.get("overall_percentage", 50.0)
        passed = overall_score >= 70
        
        return {
            "overall_score": overall_score,
            "passed": passed,
            "question_scores": result.get("question_scores", {}),
            "critical_topics": {},
            "feedback": result.get("feedback", "")
        }
    except Exception as e:
        return {
            "overall_score": 0.0,
            "passed": False,
            "error": str(e)
        }


# ===== Setup Utilities =====

def setup_directories():
    """Create necessary directories for submissions"""
    audio_dir = Path(__file__).parent / "submissions" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    tts_dir = Path(__file__).parent / "submissions" / "tts"
    tts_dir.mkdir(parents=True, exist_ok=True)
    
    speaking_dir = Path(__file__).parent / "submissions" / "speaking_temp"
    speaking_dir.mkdir(parents=True, exist_ok=True)
    
    return audio_dir, tts_dir, speaking_dir
