import json
from pathlib import Path
from datetime import datetime

import streamlit as st
import numpy as np

from db import (
    init_db,
    save_homework_submission,
    get_homework_feedback,
    update_homework_status,
    mark_lesson_complete,
)


def load_sample_lesson() -> dict:
    data_path = Path(__file__).parent / "data" / "sample_lesson_a2.json"
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_section(title: str, content: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(content)


def render_list(title: str, items: list[str]) -> None:
    st.markdown(f"### {title}")
    for item in items:
        st.markdown(f"- {item}")


def validate_homework_text(text: str, min_length: int = 50) -> tuple[bool, str]:
    """Validate homework text submission."""
    if not text or not text.strip():
        return False, "Homework text cannot be empty."
    if len(text) < min_length:
        return False, f"Homework text must be at least {min_length} characters."
    return True, "Text validation passed."


def validate_homework_audio(audio_file) -> tuple[bool, str]:
    """Validate homework audio submission."""
    if audio_file is None:
        return False, "Audio file is required."
    if audio_file.size == 0:
        return False, "Audio file cannot be empty."
    # Check file size (max 25MB for most audio formats)
    if audio_file.size > 25 * 1024 * 1024:
        return False, "Audio file is too large (max 25MB)."
    return True, "Audio validation passed."


def record_audio_with_sounddevice(
    duration: int,
    sample_rate: int = 16000,
    output_dir: Path | None = None,
) -> tuple[Path | None, int]:
    """Record audio using sounddevice and save to disk.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Audio sample rate in Hz
        output_dir: Directory where the WAV file should be saved
    
    Returns:
        Tuple of (audio_file_path, actual_duration_recorded)
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        
        st.info(f"🎙️ Recording for {duration} seconds... Speak now!")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to finish
        
        # Normalize audio to a target peak to improve consistency
        recording = normalize_audio_peak(recording, target_dbfs=-3.0)

        # Save to WAV on disk
        output_dir = output_dir or (Path("submissions") / "audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        file_path = output_dir / filename
        sf.write(file_path, recording, sample_rate)
        
        st.success(f"✅ Recording complete! ({duration}s)")
        return file_path, duration
        
    except Exception as e:
        st.error(f"Recording failed: {str(e)}")
        return None, 0


def normalize_audio_peak(audio: np.ndarray, target_dbfs: float = -3.0) -> np.ndarray:
    """Normalize audio peak to a target dBFS value."""
    peak = float(np.max(np.abs(audio)))
    if peak <= 0.0:
        return audio
    target_linear = 10 ** (target_dbfs / 20.0)
    gain = target_linear / peak
    return np.clip(audio * gain, -1.0, 1.0)


def render_homework_submission(lesson: dict) -> None:
    """Render homework submission section with local Python audio recording and upload options."""
    st.markdown("## Homework Submission")
    st.markdown(f"**Assignment:** {lesson['homework']}")
    
    # Audio recording section (outside form)
    st.markdown("### 🎙️ Audio Submission")
    st.caption("Record your audio directly or upload a pre-recorded file")
    
    # Create tabs for recording vs upload
    record_tab, upload_tab = st.tabs(["🎙️ Record Audio", "📤 Upload File"])
    
    with record_tab:
        st.write("**Record your reading directly on your computer:**")
        st.info("""
        ℹ️ **Recording Instructions:**
        1. Choose a duration in minutes (preset or custom)
        2. Click **Record now**
        3. Start speaking immediately
        4. Recording will stop automatically
        5. Preview the audio below
        6. Then fill out the form and submit
        """)
        
        preset_minutes = st.radio(
            "Preset durations (minutes)",
            [1, 2, 4, 6, 8, 10],
            horizontal=True,
        )
        custom_minutes = st.number_input(
            "Custom duration (minutes)",
            min_value=1,
            max_value=30,
            value=1,
            step=1,
        )
        use_custom = st.checkbox("Use custom duration", value=False)
        duration_minutes = int(custom_minutes) if use_custom else int(preset_minutes)
        
        if st.button("🎙️ Record now", use_container_width=True):
            st.session_state.recording = True
        
        if st.session_state.get("recording"):
            audio_path, duration = record_audio_with_sounddevice(
                duration=duration_minutes * 60
            )
            if audio_path:
                st.audio(str(audio_path), format="audio/wav")
                st.caption(
                    f"✅ Saved: {Path(audio_path).name} ({duration_minutes} min)"
                )
                st.session_state.current_audio_path = str(audio_path)
                st.session_state.current_audio_duration = duration
            st.session_state.recording = False
    
    with upload_tab:
        st.write("**Upload a pre-recorded audio file:**")
        st.caption("Supported formats: MP3, WAV, OGG, FLAC, M4A (Max 25 MB)")
        
        uploaded_audio = st.file_uploader(
            "Choose audio file:",
            type=["mp3", "wav", "ogg", "flac", "m4a"],
            key="homework_audio_upload"
        )
        
        if uploaded_audio is not None:
            st.session_state.uploaded_audio = uploaded_audio
            st.audio(uploaded_audio, format=f"audio/{uploaded_audio.type}")
            st.caption(f"✅ File selected: {uploaded_audio.name} ({uploaded_audio.size / 1024:.1f} KB)")
    
    # Text submission form (separate from recording)
    with st.form("homework_form", clear_on_submit=False):
        st.markdown("### 📝 Text Submission")
        homework_text = st.text_area(
            "Write your homework response:",
            placeholder="Enter your French text here...",
            height=200,
            key="homework_text"
        )
        
        submitted = st.form_submit_button("📤 Submit Homework", use_container_width=True)
        
        if submitted:
            # Validate inputs
            text_valid, text_msg = validate_homework_text(homework_text)
            
            # Check for audio from either recording or upload
            recorded_audio_path = st.session_state.get("current_audio_path")
            uploaded_audio = st.session_state.get("uploaded_audio")
            has_audio = recorded_audio_path is not None or uploaded_audio is not None
            
            if not text_valid:
                st.error(f"❌ Text Error: {text_msg}")
            elif not has_audio:
                st.error("❌ Audio Error: Please record or upload an audio file.")
            else:
                # Determine which audio to use (prefer recorded over uploaded)
                if recorded_audio_path is not None:
                    audio_to_submit = None
                    audio_file_path = Path(recorded_audio_path)
                    audio_size_kb = audio_file_path.stat().st_size / 1024
                    ext = audio_file_path.suffix.lstrip(".") or "wav"
                    audio_file_name = audio_file_path.name
                else:
                    audio_to_submit = uploaded_audio
                    audio_size_kb = uploaded_audio.size / 1024
                    if hasattr(uploaded_audio, "type"):
                        ext = uploaded_audio.type.split("/")[-1] if "/" in uploaded_audio.type else uploaded_audio.type
                    else:
                        ext = "wav"
                    audio_file_name = uploaded_audio.name
                
                # Save submission to database
                lesson_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Save audio file
                audio_dir = Path("submissions") / "audio"
                audio_dir.mkdir(parents=True, exist_ok=True)
                
                final_audio_path = audio_dir / f"{lesson_id}.{ext}"
                
                # Write audio to file
                try:
                    if audio_to_submit is None:
                        Path(recorded_audio_path).replace(final_audio_path)
                    else:
                        with open(final_audio_path, "wb") as f:
                            if isinstance(audio_to_submit, bytes):
                                f.write(audio_to_submit)
                            elif hasattr(audio_to_submit, "read"):
                                audio_to_submit.seek(0)
                                f.write(audio_to_submit.read())
                            elif hasattr(audio_to_submit, "getbuffer"):
                                f.write(audio_to_submit.getbuffer())
                            else:
                                f.write(audio_to_submit)
                    
                    # Save to database
                    submission_id = save_homework_submission(
                        lesson_id=lesson_id,
                        text_content=homework_text,
                        audio_file_path=str(final_audio_path),
                        character_count=len(homework_text),
                        audio_size_kb=audio_size_kb
                    )
                    
                    st.success("✅ Homework submitted successfully!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Text Length", f"{len(homework_text)} chars")
                    with col2:
                        st.metric("Audio Size", f"{audio_size_kb:.1f} KB")
                    st.info("📋 Your submission has been recorded. Awaiting AI feedback...")
                    
                    # Clear session state after successful submission
                    st.session_state.current_audio_path = None
                    st.session_state.uploaded_audio = None
                    
                except Exception as e:
                    st.error(f"❌ Error saving submission: {str(e)}")
                    st.caption("Please try again or contact support.")


def main() -> None:
    st.set_page_config(page_title="French Tutor Sample", layout="wide")
    st.title("French Tutor - Sample Lesson (A2)")
    st.caption("Static sample lesson for review; no API calls.")
    
    # Initialize database
    init_db()

    lesson = load_sample_lesson()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Lesson", "Speaking", "Quiz", "Homework"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            render_section("Level and Focus", f"**Level:** {lesson['level']}  \n**Theme:** {lesson['theme']}")
            render_section("Grammar Focus", lesson["grammar"]["explanation"])
            render_list("Grammar Examples", lesson["grammar"]["examples"])
        
        with col2:
            render_list("Conjugation Snapshot", lesson["grammar"]["conjugation"])
            render_list("Vocabulary (3 words)", lesson["vocabulary"])
    
    with tab2:
        render_section("Speaking Scenario", lesson["speaking"]["prompt"])
        render_list("Speaking Targets", lesson["speaking"]["targets"])
    
    with tab3:
        render_list("Mini Quiz", lesson["quiz"]["questions"])
    
    with tab4:
        render_homework_submission(lesson)


if __name__ == "__main__":
    main()
