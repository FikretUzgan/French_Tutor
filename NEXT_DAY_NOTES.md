# Next Day Notes

Date: 2026-02-07

## Session Summary (Audio Recording Feature Complete)
**Date:** February 7, 2026  
**Focus:** Audio recording capability + SRS spec updates

Successfully implemented dual-mode audio submission system:
- ✅ Browser-based audio recording (WebRTC)
- ✅ File upload option (MP3, WAV, OGG, FLAC, M4A)
- ✅ Updated French_Tutor_SRS.md to document both methods
- ✅ Enhanced UI with tabbed interface and clear instructions
- ✅ Installed streamlit-webrtc + dependencies (av, aiortc)
- ✅ All features tested and working

**App Status:** Running at http://localhost:8501 ✅  
**Database:** french_tutor.db with 7 tables ✅  
**Tests:** All passing - import, database, workflow ✅

## Current State
- Environment: Python 3.13, Streamlit 1.54.0 (working perfectly)
- App Status: Running at http://localhost:8501 with live reload
- Database: french_tutor.db initialized with schema
- Submissions: Directory structure created (submissions/audio/)
- Test Results: All database operations passing ✅

## Files of Interest
- app.py (Streamlit sample lesson UI)
- data/sample_lesson_a2.json (A2 sample lesson)
- data/lesson_template.json (lesson template)
- French_Tutor_SRS.md (updated rules)
- French_Course_Weekly_Plan.md (weekly plan)
- Implementation_Plan.md (detailed roadmap)

## Pending Decisions
- Gemini API integration method (streaming vs batch for feedback) - **prioritize batch for reliability**
- Audio transcription service (Whisper.cpp vs Google Speech-to-Text) - **prefer Whisper.cpp for privacy**
- Exam UI layout (single question vs multi-question per page) - **recommend single for better focus**
- SRS review scheduling rules (daily cap behavior) - **implement SM-2 with 50-item daily limit**
- Audio codec preference for storage (WAV vs compressed) - **store WAV for quality, compress on demand**

## Completed Tasks (Session 2026-02-07)
1. ✅ Set up Python 3.13 venv with Streamlit 1.54.0 (worked despite earlier concerns)
2. ✅ Installed LangChain and Google Genai dependencies
3. ✅ Implemented tabbed interface (Lesson, Speaking, Quiz, Homework)
4. ✅ Built homework submission form with:
   - Text area (min 50 characters)
   - Audio file upload (MP3, WAV, OGG, FLAC, M4A)
   - Validation for both inputs
   - Success/error feedback
5. ✅ Updated requirements.txt with all dependencies
6. ✅ App running and reloading via Streamlit dev server
7. ✅ Created SQLite database schema (french_tutor.db) with tables:
   - lessons (lesson metadata)
   - lesson_progress (tracking completion and homework status)
   - homework_submissions (text + audio storage)
   - homework_feedback (AI grading results)
   - srs_schedule (spaced repetition scheduling)
   - exams (exam metadata)
   - exam_submissions (exam answers and scores)
8. ✅ Database integration with app.py - submissions now persist to database
9. ✅ Test suite confirms full workflow: submit → save → grade → retrieve

## Latest Updates (Audio Recording)
10. ✅ Added browser-based audio recording using **streamlit-webrtc** (WebRTC)
11. ✅ Dual audio submission modes:
    - **Record:** Real-time recording via browser (Record tab)
    - **Upload:** File upload for pre-recorded audio (Upload File tab)
12. ✅ Updated SRS spec to document audio recording and upload options
13. ✅ Enhanced UI with tabs, emojis, and clearer instructions
14. ✅ Installed dependencies: streamlit-webrtc, av, aiortc
15. ✅ Updated requirements.txt with audio libraries
16. ✅ **Fixed:** Removed unsupported `disabled` parameter from webrtc_streamer()
    - Error was: "webrtc_streamer() got an unexpected keyword argument 'disabled'"
    - Solution: Removed `disabled=False` - not needed in v0.64.5
17. ✅ **Fixed WebRTC connection timeout issue** with multi-method approach:
    - Added multiple STUN servers (5 Google STUN servers for redundancy)
    - Implemented **Python-based audio recording** using `sounddevice` package
    - Provides 30s and 60s recording options as fallback
    - Clear error messages guide users to alternative recording method
    - Installed: sounddevice==0.5.5, soundfile==0.13.1
18. ✅ Updated audio submission logic to handle both WebRTC and Python recordings
    - Session state management for recorded audio
    - Automatic fallback from WebRTC to Python recording option
    - Better file handling for bytes vs file objects

## Audio Recording Implementation Details

### Recording Methods (Tripled-redundancy approach)
1. **Browser Recording (WebRTC)**
   - Uses streamlit-webrtc for in-browser audio capture
   - No installation required for users
   - Real-time microphone access via browser permissions
   - Cross-platform (Windows, Mac, Linux)
   - **5 STUN servers for redundancy:**
     - stun.l.google.com:19302
     - stun1.l.google.com:19302
     - stun2.l.google.com:19302
     - stun3.l.google.com:19302
     - stun4.l.google.com:19302

2. **Python-based Recording (sounddevice)**
   - Direct local audio capture when WebRTC unavailable
   - **Two duration options: 30 seconds or 60 seconds**
   - No network required - pure local recording
   - Saves as WAV format directly
   - Fallback when "Connection taking longer..." error occurs
   - Built-in error handling with clear user guidance

3. **File Upload**
   - Accepts: MP3, WAV, OGG, FLAC, M4A
   - Max file size: 25 MB
   - Persisted to disk in submissions/audio/
   - Metadata stored in database

### Technical Stack (Audio)
- **streamlit-webrtc==0.64.5** - Browser WebRTC wrapper
- **sounddevice==0.5.5** - Local audio recording (pure Python)
- **soundfile==0.13.1** - WAV file writing
- **av (PyAV)==16.1.0** - Audio/video frame processing
- **aiortc** - WebRTC protocol implementation
- **numpy==2.4.2** - Audio array handling

### User Experience (Improved)
- Radio button to select recording method
- Clear instructions for each method
- Graceful error handling when WebRTC fails
- Automatic suggestion to switch to Python recording
- Audio preview player for all methods
- File size display
- Success confirmation with metrics

### Database Functions Reference
- `init_db()` - Initialize database (safe to call multiple times)
- `save_homework_submission()` - Store text+audio submission
- `save_homework_feedback()` - Store AI-generated feedback
- `get_homework_submission(id)` - Retrieve submission by ID
- `get_homework_feedback(id)` - Retrieve feedback by ID
- `update_homework_status()` - Change submission status (pending/graded/needs_revision)
- `mark_lesson_complete()` - Mark lesson done with homework passed flag
- `is_lesson_blocked()` - Check if next lesson is blocked (homework required)

## File Structure Added
```
French_Tutor/
├── db.py (new - database module)
├── test_db.py (new - database tests)
├── french_tutor.db (created - SQLite database file)
├── submissions/
│   └── audio/ (created - audio file storage)
└── app.py (updated - database integration)
```

## App Files of Interest
- `app.py` - Main Streamlit app with homework submission
- `data/sample_lesson_a2.json` - Sample lesson data
- `data/lesson_template.json` - Lesson template structure
- `db.py` - Database schema and CRUD operations
- `test_db.py` - Integration tests for database

## Suggested Next Steps
1. **Integrate Gemini API** for automated homework grading with French-specific feedback.
   - Build prompt templates for grammar/vocabulary/pronunciation feedback
   - Handle audio transcription (Whisper.cpp or Google Speech-to-Text)
   - Implement feedback storage and retrieval

2. **Build exam UI** with quiz submission flow.
   - Single question per page display
   - Timer integration (45-minute exam duration)
   - Answer collection and submission
   - Auto-grading with pass/fail logic

3. **Implement progress dashboard** showing:
   - Lessons completed/blocked
   - Homework submission status and scores
   - Weekly exam results
   - Weakness analysis heatmap

4. **Add SRS scheduling logic** with SM-2 algorithm.
   - Review interval calculation
   - Daily cap (50 items max)
   - Next review date scheduling

5. **Expand content library** with at least 4-6 more lessons per level.

6. **Commit changes** to GitHub with detailed commit messages.

## Commands to Resume Development
```bash
# Full setup from scratch
cd c:\Users\fikre\Documents\PlatformIO\Projects\French_Tutor
.venv\Scripts\activate.bat

# Initialize database (idempotent)
python db.py

# Run app
streamlit run app.py

# Run tests
python test_db.py
```