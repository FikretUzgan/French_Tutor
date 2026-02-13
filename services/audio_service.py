"""
Audio Service
Handles Text-to-Speech (TTS) and Speech-to-Text (STT/Whisper) operations.
Refactored from main.py.
"""

import os
import logging
import numpy as np
import whisper
from typing import List, Optional
from difflib import SequenceMatcher

# Configure logging
logger = logging.getLogger(__name__)

# Global Whisper model (cached)
WHISPER_MODEL = None

# Common French STT correction dictionary
FRENCH_STT_CORRECTIONS = {
    # Common greetings/polite phrases
    "si vous plair": "s'il vous plaît",
    "si vous plait": "s'il vous plaît",
    "si vous plez": "s'il vous plaît",
    "si vous play": "s'il vous plaît",
    "sil vous plait": "s'il vous plaît",
    "l addition si vous": "l'addition s'il vous",
    "la dition si vous": "l'addition s'il vous",
    "l addition": "l'addition",
    "la dition": "l'addition",
    # Common contractions
    "je mappelle": "je m'appelle",
    "je mapelle": "je m'appelle",
    "je mapel": "je m'appelle",
    "c est": "c'est",
    "d accord": "d'accord",
    "qu est ce que": "qu'est-ce que",
    "est ce que": "est-ce que",
    # Common words
    "merci beaucoup": "merci beaucoup",
    "au revoir": "au revoir",
    "bien sur": "bien sûr",
    "ca va": "ça va",
    "a bientot": "à bientôt",
    "a demain": "à demain",
}


def load_whisper_model():
    """Get cached Whisper model (pre-loaded on startup)"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        logger.info("Loading Whisper model...")
        WHISPER_MODEL = whisper.load_model("base")  # Use base model for better French accuracy
    return WHISPER_MODEL


def transcribe_audio(audio_path: str, target_phrases: List[str] = None) -> str:
    """Transcribe audio file using Whisper with optional context hints"""
    model = load_whisper_model()
    
    # Build initial prompt with target phrases to guide Whisper
    initial_prompt = "Transcription en français. "
    if target_phrases:
        # Add target phrases as hints (max 3-4 to avoid over-prompting)
        hints = ", ".join(target_phrases[:4])
        initial_prompt += f"Phrases courantes: {hints}."
    
    # Transcribe with language and prompt hints
    result = model.transcribe(
        str(audio_path),
        language="fr",
        initial_prompt=initial_prompt,
        temperature=0.0  # More deterministic results
    )
    
    raw_text = result["text"].strip()
    
    # Apply post-processing corrections
    corrected_text = correct_french_transcription(raw_text, target_phrases)
    
    return corrected_text


def correct_french_transcription(text: str, target_phrases: List[str] = None) -> str:
    """Post-process French transcription to fix common STT errors"""
    corrected = text.lower().strip()
    
    # Apply correction dictionary
    for mistake, correction in FRENCH_STT_CORRECTIONS.items():
        corrected = corrected.replace(mistake, correction)
    
    # If we have target phrases, use fuzzy matching to correct towards them
    if target_phrases:
        for target in target_phrases:
            target_lower = target.lower().strip()
            # If transcription is very similar to a target phrase (>70% match), use the target
            similarity = SequenceMatcher(None, corrected, target_lower).ratio()
            if similarity > 0.7:
                return target  # Return the correctly formatted target phrase
    
    return corrected


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
