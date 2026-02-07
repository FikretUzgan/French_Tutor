# Implementation Plan (9 Months)

Project: AI French Tutor (Le Professeur Strict)
Duration: 36 weeks

## Guiding Decisions
- A1 moves faster; A2/B1 balanced; B2 slower with more review
- Weekly exam replaces one weekend session (45 minutes)
- Homework requires text + audio, blocks next lesson
- Speaking is a critical topic (>=70%) for pass
- SRS uses SM-2 defaults with daily review cap 50
- Recommendations are optional enrichment
- Vocabulary target: 27 words/week (3 words x 9 sessions)

## Definition of Done (MVP)
- Learner can complete lessons, submit homework (text+audio), and take weekly exams
- Progress tracking and weakness analysis are recorded in SQLite
- SRS scheduling works with review reminders
- AI agents generate lessons, exams, and feedback reliably
- FastAPI web UI (HTML/CSS/JS) covers lessons, exams, reports
- Basic content coverage from A1 to B2 with weekly themes

## Dependencies
- Python 3.11+, FastAPI, uvicorn, python-multipart, python-dotenv
- Gemini API key
- Whisper.cpp model (fr)
- gTTS (fr)
- SQLite + ChromaDB
- GitHub repo and CI (optional)

## Risks and Mitigations
- API rate limits: caching, retry, and offline fallback prompts
- STT accuracy: model tuning and post-processing
- User burnout: adaptive pace and review weeks
- Content repetition: prompt variance + template pools

## Phase Plan (Weeks 1-36)

### Phase 1: Foundation (Weeks 1-4)
Deliverables:
- Local environment setup and project skeleton
- Basic FastAPI SPA shell (Lesson/Exam/Report tabs)
- STT/TTS minimal pipeline test
- SQLite schema and initial data seeding
- Gemini API integration with prompt templates

Acceptance criteria:
- App runs locally and can record, transcribe, and play back audio
- Can save and load a lesson record from SQLite
- AI returns a valid lesson JSON schema on request

### Phase 2: Core Features (Weeks 5-12)
Deliverables:
- Lesson Planner agent (grammar, vocab, speaking, quiz)
- Homework module (text+audio submission, blocking rule)
- Exam generator (MCQ, fill, translation, reading, speaking)
- Auto-grading and pass/fail logic (critical topics + overall)
- Weakness tracking with weekly report

Acceptance criteria:
- End-to-end lesson flow works for a test user
- Homework blocks next lesson until submitted
- Weekly exam can be generated and graded
- Weakness report lists top 3 topics

### Phase 3: Curriculum and Content (Weeks 13-18)
Deliverables:
- A1.1/A1.2 full content library
- A2.1/A2.2 full content library
- B1/B2 skeleton and topic inventory
- Speaking scenario pools and reading passages
- **Vocabulary Practice System (3 modes)**
  - Daily Review mode (SRS-based, max 50 items)
  - Weak Areas mode (from weakness_tracking)
  - Comprehensive Review mode (all vocabulary)
- **Lesson Review with Fresh Examples**
  - AI regenerates lessons with same topic but NEW examples
  - Review lessons have no homework/exam requirements
  - Enables repeated practice without static content

Acceptance criteria:
- Weekly themes from A1/A2 can be generated without repeats
- Minimum vocabulary pool per level in database
- Speaking prompts available for each week
- **Vocabulary practice provides MCQ questions with real-time feedback**
- **Lesson review generates fresh content for any completed lesson**
- **Incorrect vocabulary answers tracked in weakness_tracking**

### Phase 4: Advanced Features (Weeks 19-22)
Deliverables:
- SRS scheduler (SM-2 defaults, daily cap 50)
- Review session flow integrated into weekly cadence
- Optional content recommendations by level

Acceptance criteria:
- SRS queue respects daily cap and next_review_date
- Review session can run inside the 30-minute slot
- Recommendations display without blocking progress

### Phase 5: Polish and Testing (Weeks 23-26)
Deliverables:
- UX improvements (progress bars, streaks, level badges)
- Unit tests for core utilities and grading
- Integration test for lesson -> homework -> exam -> report
- Documentation: user guide + developer notes

Acceptance criteria:
- All tests pass locally
- App handles network errors with fallback messages
- Documentation covers setup and usage

### Phase 6: Beta and Launch (Weeks 27-36)
Deliverables:
- Beta program (10-20 users) with feedback loop
- B1/B2 content expansion and refinement
- Error logging and basic metrics dashboard
- Release prep and public launch

Acceptance criteria:
- Beta feedback logged and triaged weekly
- Error rate and latency metrics visible
- Public release builds with onboarding flow

## Testing Strategy
- Unit tests: SRS scheduling, scoring, and data access
- Integration tests: lesson generation to completion flow
- Manual tests: STT/TTS quality checks and speaking scoring

## Milestone Checkpoints
- Week 4: Basic system runs end-to-end (single lesson)
- Week 12: Core feature set complete (lesson, homework, exam)
- Week 18: A1/A2 content complete, B1/B2 skeleton ready
- Week 22: SRS and review cadence integrated
- Week 26: UX and testing complete
- Week 36: Beta closed and launch stabilized

## Later Improvements
- Polished UI (visual design, animations, richer layouts)
