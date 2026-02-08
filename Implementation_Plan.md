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

### Phase 2A: Dynamic Lesson Generation System (Weeks 5-6)
**NEW CRITICAL PATH FEATURE** - Enables curriculum-driven lesson generation instead of static DB

Deliverables:
- `curriculum_loader.py` module (parse wk1.md - wk52.md files)
- `ai_prompts.py` module (all prompt templates with documentation)
- System prompt (big picture, role, course scope)
- Lesson generation prompt (structured curriculum → lesson JSON)
- Weakness personalization subprompt
- `POST /api/lessons/generate` endpoint (week, day, student_level → lesson JSON)
- Database schema: `lesson_generation_history` table
- Frontend: week/day selector UI (replace lesson list)
- Error handling & fallback lessons for API failures

Acceptance criteria:
- Users can select any week (1-52) and day (1-7)
- Clicking "Start Lesson" generates fresh content from curriculum in <10 seconds
- Generated lessons include complete structure: grammar, vocabulary, speaking, quiz, homework
- Grammar explanations match curriculum learning outcomes and scaffolding steps
- All 21 vocabulary words are used in examples and lessons
- Speaking scenarios are dynamically generated from weekly prompts
- Homework rubrics align with weekly curriculum requirements
- Student weaknesses are identified and addressed with extra scaffolding
- Missing curriculum files handled gracefully with error message
- API timeouts fall back to basic lesson structure
- Generated lessons persist in DB for tracking and analytics
- No dependency on pre-stored lessons in database (fully dynamic)

Key AI Prompts Used:
- SYSTEM_PROMPT: Frames AI as French tutor, sets tone, explains course scope
- LESSON_GENERATION_PROMPT: Transforms curriculum metadata → lesson JSON
- WEAKNESS_PERSONALIZATION_SUBPROMPT: Adds targeted scaffolding for identified weaknesses

Risk Mitigation:
- Curriculum files validated on startup
- Prompt quality tested manually (5 lessons per level → verify curriculum alignment)
- Token usage monitored to stay within API quota
- Fallback lesson template for API failures
- Rate limiting per user (max 1 generation/hour)

### Phase 2B: Core Features (Weeks 7-12)
Deliverables:
- Lesson Planner agent (grammar, vocab, speaking, quiz) **[REFACTORED: uses generated lessons]**
- Homework module (text+audio submission, blocking rule)
- Exam generator (MCQ, fill, translation, reading, speaking)
- Auto-grading and pass/fail logic (critical topics + overall)
- Weakness tracking with weekly report

Acceptance criteria:
- End-to-end lesson flow works for a test user (using generated lessons)
- Homework blocks next lesson until submitted (prevents week 5→week 6 jump without homework)
- Weekly exam can be generated and graded
- Weakness report lists top 3 topics
- Homework evaluation uses dedicated prompt that scores grammar, pronunciation, content

### Phase 3: Curriculum and Content (Weeks 13-20)
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
- **Interactive Lesson Delivery (from weekly plans)**
  - Start lesson uses the week plan to drive a step-by-step session
  - AI guides grammar, vocabulary, speaking, and quiz in sequence
  - Progress is tracked per section (complete/skip/retry)

Acceptance criteria:
- Weekly themes from A1/A2 can be generated without repeats
- Minimum vocabulary pool per level in database
- Speaking prompts available for each week
- **Vocabulary practice provides MCQ questions with real-time feedback**
- **Lesson review generates fresh content for any completed lesson**
- **Incorrect vocabulary answers tracked in weakness_tracking**
- **Interactive lesson follows the weekly plan structure**
- **Each section supports user responses and AI feedback**

### Phase 4: Advanced Features (Weeks 21-26)
Deliverables:
- SRS scheduler (SM-2 defaults, daily cap 50)
- Review session flow integrated into weekly cadence
- Optional content recommendations by level

Acceptance criteria:
- SRS queue respects daily cap and next_review_date
- Review session can run inside the 30-minute slot
- Recommendations display without blocking progress

## Phase Notes (Updated 2026-02-08)
- **NEW:** Phase 2A (Dynamic Lesson Generation) is now critical path—must complete before Phase 2B
- Phase 2A includes curriculum file parsing, AI prompts, and week/day selector UI
- Phase 2B refactored to use dynamically generated lessons (no static DB lessons)
- Phase 3 and 4 shifted by 2 weeks to accommodate Phase 2A
- Test coverage and polish remain in Phase 5 scope
- Full 52-week curriculum files (wk1-wk52.md) must exist with consistent structure

### Phase 5: Polish and Testing (Weeks 27-30)
Deliverables:
- UX improvements (progress bars, streaks, level badges)
- Unit tests for core utilities and grading
- Integration test for lesson -> homework -> exam -> report
- Prompt quality validation (5 generated lessons per level reviewed manually)
- Documentation: user guide + developer notes

Acceptance criteria:
- All tests pass locally
- App handles network errors with fallback messages
- Documentation covers setup and usage
- No curriculum violations in 100+ generated lessons

### Phase 6: Beta and Launch (Weeks 31-40)
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
- Unit tests: SRS scheduling, scoring, data access, curriculum parsing
- Integration tests: lesson generation to completion flow (includes curriculum file loading)
- Manual tests: STT/TTS quality checks, speaking scoring, prompt output validation
- Prompt validation tests: Ensure generated lessons match curriculum requirements

## Milestone Checkpoints
- Week 4: Basic system runs end-to-end (single lesson)
- **Week 6: Dynamic lesson generation working (curriculum → lesson JSON)**
- Week 12: Core feature set complete (lesson, homework, exam with generated content)
- Week 20: A1/A2 content complete, B1/B2 skeleton ready
- Week 26: SRS and review cadence integrated
- Week 30: UX and testing complete
- Week 40: Beta closed and launch stabilized

## Current Phase: Dynamic Lesson Quality & Interactive Content (2026-02-08)
Addressing critical issues with lesson generation:
- **COMPLETED:** Enhanced AI prompts with mandatory 5-paragraph grammar structure
  - Paragraph 1: Definition & importance (3-4 sentences)
  - Paragraph 2: English comparison & common difficulties (3-4 sentences)
  - Paragraph 3: Full conjugation/form breakdown per pronoun (6-8 sentences)
  - Paragraph 4: Real-world usage scenarios (3-4 sentences, 2+ scenarios)
  - Paragraph 5: Common pitfalls with corrections (3-4 sentences, 2+ errors)
  - Minimum 400 words, 20 sentences per grammar explanation
- **COMPLETED:** Dynamic content variation system (attempt tracking)
  - Each lesson generation gets a unique attempt_number and variation_seed
  - Attempt count tracked in DB via `get_lesson_generation_count()`
  - Different variation instructions per attempt (contexts, adjectives, scenarios)
  - Temperature escalation: 0.8 → 0.95 → 1.1 → 1.25 (more creative each attempt)
  - 6 context pools × 6 adjective pools × 12 scenario pools = high variation
- **COMPLETED:** Fixed Gemini model to `gemini-2.5-flash` consistently
- **COMPLETED:** Increased max_tokens from 2000 to 4096 for richer content
- **COMPLETED:** Enhanced vocabulary display (ALL curriculum words, usage notes)
- **COMPLETED:** Improved quiz question type rotation per attempt
- Standardized 3-button navigation (Back, Next, Exit Lesson) throughout all lessons
- Vocabulary French-side listening with gender variant support
- Listen icons on example sentences
- Speaking practice modal integration
- Quiz answer validation and feedback system
- Progress tracking fixes
- Post-lesson completion flows

## Future Phase: Homework System (Feedback #10)
Features for future implementation:
- Homework at end of lesson with AI evaluation
- Homework re-submission workflow based on success thresholds
- Chat-based feedback before re-submission
- Initial lesson exemption from homework check
- Homework completion blocking progression

## Later Improvements
- Polished UI (visual design, animations, richer layouts)
- **Interactive grammar expansion buttons**
  - "More Explanation" and "More Examples" in lesson grammar section
  - Calls AI to extend only the grammar section (no full lesson regeneration)
  - Appends new examples and avoids repeats
- **Grammar reference tab with fixed content**
  - Curated explanations by topic (tenses, pronouns, negation, questions)
  - Reliable fallback when AI output is insufficient
- **Store generated lesson JSON in DB** for comparison across attempts
  - Enables "show me what changed" feature
  - Prevents AI from accidentally reusing examples from previous generations
- **Quiz question bank** from previous generations
  - Pool questions across attempts for exam-style varied assessments
