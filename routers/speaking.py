"""
Speaking Routes: Audio transcription, speech analysis, and TTS
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from core.schemas import SpeakingRequest, TTSRequest
from services import ai_service, audio_service
from gtts import gTTS
import tempfile
import os
import json
import logging
import random

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/speaking/random-scenario")
async def generate_random_scenario():
    """Generate a detailed random French speaking scenario using AI."""
    try:
        import google.genai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "API key not configured", "scenario": None}
        
        locations = [
            "Ticket office",
            "Restaurant", 
            "Café",
            "Shopping center",
            "Kitchen (cooking class)",
            "Education (classroom)",
            "Travel agency",
            "Hotel",
            "Train station",
            "Airport",
            "Pharmacy",
            "Bank"
        ]
        location = random.choice(locations)
        
        prompt = f"""Create a French conversation role-play scenario at a {location}.

Language Level: A1-A2 (Beginner)

The student will have a CONVERSATION with an AI character. You are NOT creating teacher feedback - you are setting up a real dialogue.

Structure your response exactly like this:

**Scenario Title** (2-3 words)
[Name of the roleplay]

**Your Role** 
[Student role description]

**AI Character's Role**
[Character description]

**Opening Dialogue**
AI: [Opening sentence in French - keep it simple]

**Your Goals**
- [Goal 1]
- [Goal 2]
- [Goal 3]"""
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        scenario_text = response.text.strip() if response else ""
        
        return {
            "location": location,
            "scenario": scenario_text,
            "success": bool(scenario_text)
        }
    
    except Exception as e:
        logger.error(f"Failed to generate scenario: {e}")
        return {"error": f"Failed to generate scenario: {str(e)}", "scenario": None}


@router.post("/api/speaking/feedback")
async def get_speaking_feedback(request: SpeakingRequest):
    """
    Get AI feedback on user's speaking.
    Generates AI response as a conversation partner.
    """
    try:
        # Use AI Service to generate roleplay response
        response_text = ai_service.get_speaking_roleplay_response(
            scenario=request.scenario,
            transcribed_text=request.transcribed_text
        )

        return {"feedback": response_text}

    except Exception as e:
        logger.error(f"Speaking feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/audio/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    targets: str = Form(None)
):
    """Transcribe uploaded audio file using Audio Service (Whisper)."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Parse target phrases if provided
        target_list = json.loads(targets) if targets else None

        # Use Audio Service to transcribe
        transcription = audio_service.transcribe_audio(tmp_path, target_list)

        # Cleanup temp file
        os.unlink(tmp_path)

        return {"text": transcription}

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/audio/tts")
async def text_to_speech(request: TTSRequest):
    """Generate Text-to-Speech audio in MP3 format."""
    try:
        # Use gTTS to generate audio
        tts = gTTS(text=request.text, lang=request.lang)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            tmp_path = tmp.name

        return FileResponse(tmp_path, media_type="audio/mpeg", filename="tts.mp3")

    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
