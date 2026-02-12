# Implementation Plan (12 Months - Updated 2026-02-12)

Project: AI French Tutor (Le Professeur Strict)
Duration: 52 weeks (12 months)

## Guiding Decisions (Updated for New Curriculum)
- **NEW APPROACH:** Curriculum = Fixed content files (Week 1-52), AI = Evaluation only (speaking/homework/exam feedback)
- **NEW:** 52-week curriculum structure (Week 1-52, 5 days/week = 20 days/month)
- **NEW:** Vocabulary: 5 words/day × 20 days = 100 words/month × 12 months = 1,200 total words
- **NEW:** Content Identifier taxonomy for exercise types (conjugation, fill_blank, listening, dialogue, etc.)
- **NEW:** Speaking Tier progression (Tier 1 → Tier 2 → Tier 3) across months
- **NEW:** Monthly comprehensive exams (DELF-aligned mock format)
- **ARCHITECTURE:** Fixed curriculum files provide all lesson content (grammar, vocabulary, examples, quiz questions)
- **AI ROLE:** Gemini API used ONLY for interactive evaluation (speaking feedback, homework grading, exam scoring)
- A1 moves faster; A2/B1 balanced; B2 slower with more review
- Homework requires text + audio, blocks next lesson
- Speaking is a critical topic (>=70%) for pass
- SRS uses SM-2 defaults with daily review cap 50
- Recommendations are optional enrichment

## Definition of Done (MVP - Updated 2026-02-12)
- ✅ Learner can navigate 52-week curriculum structure (view any Week 1-52, Day 1-5)
- ✅ Lessons loaded from fixed curriculum files in NEW_CURRICULUM_REDESIGNED folder (not AI-generated)
- ✅ Content identifiers extracted from metadata and used for exercise type selection
- ✅ Speaking tier automatically assigned based on month/level progression
- ✅ Learner can complete lessons with grammar, vocabulary (5 words/day), speaking, and quiz
- ✅ Homework submission (text+audio) functional with blocking rule
- ✅ Monthly exams (Days 20, 40, 60, etc.) loaded from curriculum files in DELF-aligned format (4 sections)
- ✅ Progress tracking records completion, scores, and weakness patterns
- ✅ Weakness analysis identifies struggling content types (e.g., "conjugation" vs. "listening")
- ✅ SRS scheduling works for vocabulary review (learned_vocabulary table)
- ✅ AI evaluates speaking/homework/exams reliably (<5% error rate in feedback quality)
- ✅ FastAPI web UI covers: lesson navigation, quiz interaction, homework submission, exam taking, progress reports
- ✅ Full 52-week curriculum coverage from A1.1 to B2.2 with specialization paths
- ✅ All 40+ content identifier types represented across curriculum
- ✅ 1,200 total vocabulary words tracked with example sentences

## Dependencies (Updated 2026-02-12)
- Python 3.11+
- FastAPI, uvicorn, python-multipart, python-dotenv
- Gemini API key (google.generativeai)
- Whisper.cpp model (fr) for STT
- gTTS (fr) for TTS
- SQLite (database)
- ChromaDB (optional for semantic search in future phases)
- **NEW:** Curriculum files in `Research/NEW_CURRICULUM_REDESIGNED/` folder
  - Week_1_A1.1.md through Week_52_*.md (52 files total)
  - Consistent markdown structure with metadata sections
  - Content identifier taxonomy from `Research/Content_identifiers.md`
- GitHub repo (version control)
- CI/CD pipeline (optional for automated testing)

## Risks and Mitigations (Updated 2026-02-12)
- **API rate limits:** Use AI only for evaluation (speaking/homework/exam), not content generation. Retry logic with exponential backoff for evaluation requests.
- **STT accuracy:** Whisper model tuning for French pronunciation, post-processing phonetic normalization
- **User burnout:** Adaptive pace based on performance, weekly review days (Day 5, 10, 15 lighter load), monthly milestones
- **Content quality in fixed curriculum files:**
  - Manual review process for all 52 curriculum files before deployment
  - Consistent markdown structure validation
  - Grammar accuracy verification by native speakers
  - Quiz question quality testing (distractor effectiveness, answer key validation)
- **Content identifier imbalance:** 
  - Analytics dashboard tracks type distribution across curriculum files
  - Curriculum review to ensure all 40+ types represented
  - Rebalance weeks if analytics show gaps
- **Speaking tier progression too slow/fast:**
  - Performance-based tier advancement (70%+ accuracy → next tier)
  - Manual override option for advanced learners
  - Tier lock prevents regression below mastered level
- **Monthly exam difficulty calibration:**
  - Target 50-60% pass rate on first attempt
  - Fixed exam content pre-validated for difficulty
  - Alternative exam versions for retakes (stored in curriculum files)

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
- AI can evaluate speaking/homework submissions and return structured feedback

### Phase 2A: Fixed Curriculum Loading & Display System (Weeks 5-6) ✅ COMPLETED
**CRITICAL PATH FEATURE** - Loads and displays pre-authored curriculum content from NEW_CURRICULUM_REDESIGNED

**Status: COMPLETED 2026-02-12**
- ✅ Curriculum loader parses Week_1_A1.1.md through Week_4_A1.1.md files
- ✅ Fixed content extraction: grammar (pre-written), vocabulary (5 words/day), examples (50), quiz (50 questions)
- ✅ All lesson content sourced from curriculum files (NO AI generation for lessons)
- ✅ Complete lesson structure displayed: grammar, vocabulary, speaking prompts, quiz questions
- ✅ Content Identifier metadata extracted from curriculum
- ✅ Speaking Tier metadata tracked per lesson
- ✅ Frontend week/day selector UI implemented
- ✅ Error handling for missing/malformed curriculum files
- ✅ Database: `lessons` table stores references to curriculum file content (not generated content)

**Current Curriculum Coverage:**
- ✅ Month 1 (A1.1) - Weeks 1-4 complete (Days 1-20, 100 vocabulary words)
- 🔜 Month 2 (A1.2) - Weeks 5-8 planned (Days 21-40, +100 words)
- 🔜 Remaining 44 weeks in research phase

**Key Architectural Decisions:**
- **FIXED CURRICULUM:** All lesson content pre-authored in `Research/NEW_CURRICULUM_REDESIGNED/` folder (52 files)
- **AI EVALUATION ONLY:** Gemini API used for speaking feedback, homework grading, exam scoring (NOT lesson generation)
- Each week file contains 5 days (Monday-Friday structure)
- Each day includes: metadata, grammar section (pre-written), vocabulary (5 words), examples (50), speaking prompts (fixed), quiz questions (50, pre-written)
- **Content Identifiers** embedded in day metadata (e.g., "conjugation, fill_blank, listening, dialogue")
- **Speaking Tier** progression tracked (Tier 1 → 2 → 3)
  
**Content Identifier System:**
- Taxonomy from `Research/Content_identifiers.md`
- 7 categories: Grammar, Vocabulary, Reading, Listening, Speaking, Writing, Interaction
- 40+ specific types (conjugation, fill_blank, listening, dialogue_comprehension, role_play, etc.)
- Each day's metadata includes relevant content_identifiers for quiz question selection from fixed bank

**Next Steps (Phase 2A Extension - Week 7):**
- 🔜 Parse quiz questions from curriculum files (not generated, pre-written in markdown)
- 🔜 Quiz question display logic: select 8 questions from 50-question fixed bank per day
- 🔜 Database schema update: add `content_identifiers` and `speaking_tier` columns to lessons table
- 🔜 Speaking evaluation prompts: AI analyzes user audio and provides feedback
- 🔜 Vocabulary practice modes using fixed vocabulary lists (semantic_field, word_association, etc.)

### Phase 2B: Quiz Display & AI Evaluation System (Weeks 7-9)
**NEW FOCUS:** Display quiz questions from fixed curriculum files + implement AI-based evaluation for speaking/homework

Deliverables:
- **Content Identifier Parser** - Extract content_identifiers from day metadata
- **Quiz Question Parser** - Parse pre-written quiz questions from curriculum markdown files
  - Extract 50 questions per day from curriculum files
  - Parse question format (multiple_choice, fill_blank, conjugation, etc.)
  - Store question metadata (content_identifier type, difficulty, answer key)
- **Quiz Display Logic** - Show 8 questions from 50-question fixed bank
  - Random selection ensuring content_identifier variety
  - Track which questions already shown to user (avoid repeats)
  - Rotate question types based on content_identifiers
- **AI Evaluation Prompts** - Gemini API for interactive feedback
  - **Speaking Evaluation:** Analyze user audio, score pronunciation/grammar/content (0-100)
  - **Homework Grading:** Evaluate text+audio submissions, provide detailed feedback
  - **Exam Scoring (future):** Score written/speaking exam sections, generate rubric-based results
- **Database Schema Updates:**
  - Add `content_identifiers` TEXT column to `lessons` table (JSON array)
  - Add `speaking_tier` INTEGER column to `lessons` table (1, 2, or 3)
  - Add `shown_questions` TEXT to `lesson_progress` (track which questions user saw)
- **Speaking Tier Evaluation Logic**
  - Tier 1 (Months 1-2): AI checks script adherence, basic pronunciation
  - Tier 2 (Months 3-6): AI evaluates scenario completion, grammar accuracy
  - Tier 3 (Months 7-12): AI scores fluency, complexity, naturalness

Acceptance criteria:
- ✅ Content identifiers correctly parsed from curriculum metadata
- ✅ Quiz questions loaded from curriculum files (not AI-generated)
- ✅ 8 questions displayed per quiz with content_identifier variety
- ✅ Speaking tier correctly assigned and AI evaluation adapts scoring criteria
- ✅ AI provides structured feedback for speaking/homework (<10 second response time)
- ✅ Database stores content_identifiers, speaking_tier, and shown_questions for analytics

### Phase 2C: Homework & Assessment System (Weeks 10-12)
Deliverables:
- Homework module (text+audio submission, blocking rule)
- Monthly exam generator (comprehensive DELF-aligned format)
  - 4 sections: Listening (25pts), Reading (25pts), Writing (25pts), Speaking (25pts)
  - Pass threshold: 50/100 points
  - Section-specific rubrics aligned with CEFR standards
- Auto-grading and pass/fail logic (critical topics + overall)
- Weakness tracking with monthly report
- **Monthly Exam Structure** (from curriculum Week 4/8/12/16/20 etc.)
  - Day 20, 40, 60, 80, 100, 120, 140, 160 = monthly comprehensive exams
  - 60-90 minute duration
  - All 4 skills tested
  - Results determine progression to next month

Acceptance criteria:
- End-to-end lesson flow works for test user (using fixed curriculum content with AI evaluation)
- Homework blocks next lesson until submitted (prevents Day 6→Day 7 jump without homework)
- Monthly exam (Day 20, 40, etc.) loaded from curriculum files with all 4 sections
- Weakness report lists top 5 topics with accuracy percentages
- AI homework evaluation provides structured feedback (grammar, pronunciation, content scores)
- Monthly exam pass/fail determines if user advances to next month

### Phase 3: Curriculum Expansion & Advanced Features (Weeks 13-24)
**GOAL:** Author complete 52-week fixed curriculum + implement advanced practice modes

Deliverables:
- **Month 2 (A1.2) Curriculum Authoring** - Weeks 5-8 complete (Days 21-40)
  - Author fixed content: Passé composé with avoir/être, Futur proche, Possessive adjectives
  - +100 vocabulary words (Total: 200 words)
  - Pre-write 50 quiz questions per day
- **Month 3 (A2.1) Curriculum Authoring** - Weeks 9-12 complete (Days 41-60)
  - Author fixed content: Imparfait, Passé composé vs. Imparfait, Comparatives/superlatives, Relative pronouns
  - +100 vocabulary words (Total: 300 words)
  - Pre-write 50 quiz questions per day
- **Month 4 (A2.2) Curriculum Authoring** - Weeks 13-16 complete (Days 61-80)
  - Author fixed content: Futur simple, Conditionnel présent, Pronouns Y & EN, Reflexive verbs
  - +100 vocabulary words (Total: 400 words)
  - Pre-write 50 quiz questions per day
- **Vocabulary Practice System (4 modes)** - Using fixed vocabulary lists
  - Mode 1: Bidirectional Translation (FR↔EN with STT/TTS)
  - Mode 2: Verb Conjugation Practice (random tense from learned forms)
  - Mode 3: Multiple Choice Context (4 options with images)
  - Mode 4: Visual Recognition (match word to image)
  - SRS scheduling: words reappear at Day +7, +14, +30
- **Learned Vocabulary Database** (`learned_vocabulary` table)
  - Tracks all 1,200 words from curriculum files
  - Fields: word_id, french_word, english_translation, cefr_level, day_introduced, word_type, example_sentence, pronunciation
  - Verb conjugation tracking (which tenses learned per verb)
- **Speaking Prompt Pools** by Tier (Fixed content in curriculum files)
  - Tier 1: 50+ script-based prompts (A1.1-A1.2)
  - Tier 2: 75+ guided scenario prompts (A2.1-A2.2, B1.1)
  - Tier 3: 100+ free conversation prompts (B1.2-B2.2)
  - AI evaluates user responses, does NOT generate new prompts
- **Lesson Review with Content Identifier Variation**
  - Display same lesson again but select different quiz questions from 50-question fixed bank
  - Example: Day 1 (être) review → show questions 9-16 instead of 1-8
  - Track which questions already shown to ensure variety
  - AI evaluation remains same (speaking/homework feedback)

Acceptance criteria:
- ✅ Months 1-4 curriculum files authored (Weeks 1-16, Days 1-80, 400 vocabulary words)
- ✅ All content_identifiers represented across curriculum files (manual content authoring)
- ✅ Vocabulary practice uses learned_vocabulary table with SRS scheduling
- ✅ Verb conjugation mode only asks tenses introduced up to current day
- ✅ Speaking prompts match tier complexity (script vs. guided vs. free) - fixed content in files
- ✅ Lesson review shows different quiz questions from same fixed 50-question bank
- ✅ Content identifier distribution analytics available (which types used most/least in authored content)

### Phase 4: B1/B2 Curriculum Authoring & SRS Enhancement (Weeks 25-32)
**GOAL:** Author B1/B2 curriculum files + enhance vocabulary review system

Deliverables:
- **Month 5 (B1.1) Curriculum Authoring** - Weeks 17-20 (Days 81-100)
  - Author fixed content: Subjonctif présent, Passé simple (reading), Complex relative pronouns, Advanced indirect speech
  - +100 vocabulary words (Total: 500 words)
  - Pre-write 50 quiz questions per day
- **Month 6 (B1.2) Curriculum Authoring** - Weeks 21-24 (Days 101-120)
  - Author fixed content: Passive voice, Participle phrases, Advanced si-clauses, Literary devices
  - +100 vocabulary words (Total: 600 words)
  - Pre-write 50 quiz questions per day
- **Month 7-8 (B2.1-B2.2) Curriculum Authoring** - Weeks 25-32 (Days 121-160)
  - Author fixed content: Conditionnel passé, Subjunctive complex uses, Register shifts, Stylistic variation, Argumentative structures
  - +200 vocabulary words (Total: 800 words)
  - Pre-write 50 quiz questions per day
- **SRS Scheduler Enhancement**
  - SM-2 algorithm defaults with daily cap 50
  - Content-identifier-aware review (prioritize weak types)
  - Review session flow integrated into 30-minute slots
- **Optional Content Recommendations**
  - Authentic materials by level (news articles, videos, podcasts)
  - Recommendations based on weakness_tracking + content_identifier gaps

Acceptance criteria:
- ✅ Months 5-8 curriculum files authored (Weeks 17-32, Days 81-160, 800 vocabulary words)
- ✅ All curriculum files follow consistent markdown structure
- ✅ SRS queue respects daily cap and next_review_date
- ✅ Review sessions prioritize content types with low accuracy
- ✅ Recommendations display without blocking progress
- ✅ B2-level lessons include authentic material references

## Phase Notes (Updated 2026-02-12)
- **COMPLETED:** Phase 2A (Fixed Curriculum Loading) - critical path finished
  - Curriculum file parsing from NEW_CURRICULUM_REDESIGNED folder operational
  - Fixed content display: grammar (pre-written), vocabulary, examples, quiz questions
  - Week/day selector UI functional in frontend
  - Month 1 (Weeks 1-4, Days 1-20) curriculum files complete with 100 vocab words
- **IN PROGRESS:** Phase 2B (Quiz Display & AI Evaluation) - Weeks 7-9
  - Content identifier extraction from metadata
  - Quiz question parser: load 50 pre-written questions per day from curriculum files
  - AI evaluation prompts for speaking/homework feedback
  - Database schema updates for content_identifiers and speaking_tier
- **UPCOMING:** Phase 2C (Homework & Monthly Exams) - Weeks 10-12
  - AI homework evaluation system with audio transcription + grading
  - Monthly comprehensive exams (loaded from curriculum files, DELF-aligned, 4 sections)
  - Weakness tracking by content type
- **PLANNED:** Phase 3 (Curriculum Expansion) - Weeks 13-24
  - Author Months 2-4 curriculum files (A1.2, A2.1, A2.2) - 300 additional vocab words
  - Vocabulary practice system (4 modes with SRS) using fixed vocabulary lists
  - Learned_vocabulary database implementation
  - Speaking prompt pools by tier (fixed content in curriculum files)
- **FUTURE:** Phases 4-6 - Weeks 25-52
  - Author B1/B2 curriculum files + specialization paths
  - Content identifier analytics dashboard
  - Beta testing with 50-100 users
  - Public launch with full 52-week fixed curriculum
- **KEY ARCHITECTURAL DECISIONS:**
  - **FIXED CURRICULUM + AI EVALUATION ONLY:** All lesson content pre-authored, AI used only for feedback
  - Monthly structure (20 days/month) instead of weekly (easier pacing)
  - Content identifiers drive question selection from fixed 50-question banks
  - Speaking tier progression automatic but performance-gated
  - All 52 curriculum files must follow consistent markdown structure
  - Test coverage required before each phase completion (90%+ target)

### Phase 5: Specialization Paths & Final Curriculum Authoring (Weeks 33-40)
**GOAL:** Author all 52 curriculum files + user-selected specialization tracks

Deliverables:
- **Specialization Path Authoring** (Months 9-12, Weeks 33-52, Days 161-240)
  - Path A: Business French (commerce, negotiation, professional communication)
  - Path B: Literary French (classic literature, poetry analysis)
  - Path C: Cultural French (cinema, history, philosophy, social studies)
  - Path D: Conversational Mastery (dialectology, regional speech)
  - Each path: Author 20 weeks of fixed curriculum content with +400 vocabulary words (Total: 1,200 words)
- **Content Identifier Coverage Analytics**
  - Dashboard showing which exercise types used across all curriculum files
  - Identify content type gaps (e.g., "role_play" underutilized in authored content)
  - Rebalance curriculum files to ensure all 40+ content types represented
- **UX Improvements**
  - Progress bars showing % of month complete (20 days/month)
  - Speaking tier badges (unlocked at Tier 2, Tier 3 milestones)
  - Vocabulary mastery % per month (target: 95% retention)
  - Monthly exam results dashboard
- **Testing & Quality**
  - Unit tests for curriculum parsing, content identifier extraction
  - Integration tests for full lesson flow (load curriculum → display → quiz → AI evaluation → homework)
  - Curriculum file validation (all 52 files have consistent structure)
  - Content identifier distribution tests (ensure variety across authored files)
- **Documentation**
  - User guide: How to navigate 52-week structure
  - Developer notes: Adding new content identifiers
  - **Curriculum authoring guide:** Template for new week files, style guide, quality checklist

Acceptance criteria:
- ✅ All 52 curriculum files authored with consistent markdown structure
- ✅ 4 specialization paths fully developed (Months 9-12, all pre-written content)
- ✅ Content identifier analytics dashboard functional
- ✅ All exercise types (40+) used at least 5 times across curriculum files
- ✅ Unit + integration tests pass with 90%+ coverage
- ✅ Documentation complete and published
- ✅ Curriculum authoring guide enables third-party content creation

### Phase 6: Beta Testing & Launch (Weeks 41-52)
Deliverables:
- **Beta Program** (50-100 users, 12-week cohort)
  - Structured feedback on all 12 months of curriculum
  - Content identifier preference surveys (which exercise types most helpful?)
  - Speaking tier effectiveness evaluation (AI evaluation quality)
  - Monthly exam difficulty calibration (pass rate tracking)
- **Error Logging & Analytics**
  - Track curriculum file loading success rate
  - Monitor content identifier distribution per user (which types completed)
  - Speaking tier progression analytics (how fast users advance)
  - AI evaluation quality metrics (feedback helpfulness ratings)
  - Monthly exam pass rates by level (calibrate difficulty)
  - Vocabulary retention metrics (SRS effectiveness)
- **Production Optimizations**
  - Caching for frequently accessed curriculum files
  - Batch processing for AI evaluation requests
  - Database indexing for content_identifier queries
  - API rate limit management for Gemini evaluation calls
- **Public Launch Preparation**
  - Onboarding flow (level assessment, goal setting)
  - Marketing materials highlighting 52-week structured curriculum
  - Tutorial videos for content types and speaking tiers
  - Community features (optional peer review, discussion forums)

Acceptance criteria:
- ✅ Beta feedback logged, triaged, and addressed weekly
- ✅ Error rate <1% for curriculum file loading
- ✅ AI evaluation latency <10 seconds for 95% of requests
- ✅ Content identifier variety confirmed across user sessions (no type completed >30% or <1%)
- ✅ Speaking tier progression validated (users advance naturally based on performance)
- ✅ Monthly exam calibrated (50-60% pass rate on first attempt)
- ✅ Public release build with full 52-week fixed curriculum
- ✅ Onboarding flow tested with 20+ new users

## Testing Strategy (Updated 2026-02-12)
- **Unit tests:** 
  - SRS scheduling logic
  - Content identifier parsing from curriculum metadata
  - Quiz question parsing from markdown files (validate 50 questions/day)
  - Speaking tier assignment logic
  - Scoring and grading algorithms
  - Database CRUD operations
- **Integration tests:**
  - Full lesson loading flow (curriculum file → parse content → display in UI)
  - Quiz question selection logic (8 from 50, variety by content_identifier)
  - AI evaluation pipeline (user audio/text → Gemini API → structured feedback)
  - Homework submission → AI grading → blocking logic
  - Monthly exam loading → AI grading → progression decision
  - Vocabulary practice modes with SRS scheduling
- **Manual tests:**
  - STT/TTS quality checks (French pronunciation accuracy)
  - AI speaking evaluation fairness across tiers (does Tier 1 scoring differ from Tier 3?)
  - Curriculum file validation (all 52 files have consistent structure)
  - Quiz question quality (answer keys correct, distractors plausible)
  - Monthly exam difficulty calibration
- **Curriculum validation tests:**
  - Ensure all curriculum files have 5 days (Monday-Friday)
  - Validate each day has: grammar (400+ words), vocabulary (5 words), examples (50), quiz (50 questions)
  - Verify content_identifiers match Content_identifiers.md taxonomy
  - Check vocabulary progression (no repeated words across days)
  - Validate quiz answer keys (all questions have correct answers)
- **AI evaluation quality tests:**
  - Speaking feedback accuracy (does AI correctly identify pronunciation errors?)
  - Homework grading consistency (same submission → similar scores across attempts)
  - Exam scoring rubric validation (CEFR-aligned criteria)
- **Content identifier analytics tests:**
  - Exercise type distribution across 52 curriculum files (balanced representation?)
  - Content type effectiveness (which types correlate with high scores?)
  - User preference patterns (do users perform better with certain types?)

## Milestone Checkpoints (Updated 2026-02-12)
- ✅ **Week 4:** Basic system runs end-to-end (single lesson)
- ✅ **Week 6:** Dynamic lesson generation working (curriculum → lesson JSON)
- ✅ **Week 6:** Month 1 curriculum complete (Weeks 1-4, Days 1-20, 100 vocab words)
- 🔄 **Week 7-9:** Content identifier integration (exercise type mapping + quiz generator refactor)
- 🔄 **Week 10-12:** Homework + monthly exam system (DELF-aligned, 4 sections)
- 🕒 **Week 16:** Month 2 curriculum complete (Weeks 5-8, Days 21-40, 200 total words)
- 🕒 **Week 20:** Months 3-4 curriculum complete (A1.1-A2.2 finished, 400 total words)
- 🕒 **Week 24:** Vocabulary practice system (4 modes with SRS)
- 🕒 **Week 28:** Learned_vocabulary database fully operational
- 🕒 **Week 32:** B1/B2 curriculum complete (Months 5-8, 800 total words)
- 🕒 **Week 40:** All 52 weeks curriculum + 4 specialization paths complete (1,200 total words)
- 🕒 **Week 44:** Content identifier analytics dashboard operational
- 🕒 **Week 48:** UX polish and testing complete
- 🕒 **Week 52:** Beta launch and feedback integration complete

**Legend:** ✅ Complete | 🔄 In Progress | 🕒 Planned

## Current Phase: Quiz Display & AI Evaluation Implementation (Week 7 - 2026-02-12)

### Recently Completed (Phase 2A):
- ✅ Fixed curriculum file parsing system operational
  - curriculum_loader.py parses Week_1-4 markdown files
  - Extracts pre-written grammar, vocabulary (5 words/day), examples (50), quiz questions (50)
  - No AI generation for lesson content - all content sourced from curriculum files
- ✅ Month 1 (A1.1) Curriculum Files Complete - Weeks 1-4
  - Week 1: Être, Avoir, -ER verbs, Articles (Days 1-5)
  - Week 2: -IR/-RE verbs, Negation, Questions (Days 6-10)
  - Week 3: Gender, Number, Article Agreement, Adjectives (Days 11-15)
  - Week 4: Questions, Complex Negation, Imperatives, Time, Month 1 Exam (Days 16-20)
  - **100 vocabulary words** with example sentences (all pre-written in curriculum files)
  - **Content identifiers** embedded in all day metadata
  - **Speaking Tier 1** → Tier 2 transition
- ✅ Frontend displays fixed curriculum content (grammar, vocabulary, examples)

### Active Work (Phase 2B - Weeks 7-9):
**GOAL:** Parse quiz questions from curriculum files + implement AI evaluation for speaking/homework

**Tasks:**
1. 🔄 **Quiz Question Parser**
   - Parse 50 pre-written quiz questions per day from curriculum markdown files
   - Extract question metadata: type (multiple_choice, fill_blank, conjugation), answer key, content_identifier
   - Store in database for tracking which questions shown to user

2. 🔄 **Quiz Display Logic**
   - Select 8 questions from 50-question fixed bank per day
   - Ensure content_identifier variety (e.g., mix conjugation + fill_blank + listening)
   - Track shown_questions in lesson_progress table to avoid repeats
   - Randomize order for each attempt

3. 🔄 **AI Evaluation Prompts**
   - **Speaking Evaluation:** Gemini API analyzes user audio recording
     - Tier 1: Script adherence (0-100), pronunciation (0-100)
     - Tier 2: Grammar accuracy (0-100), scenario completion (0-100)
     - Tier 3: Fluency (0-100), complexity (0-100), naturalness (0-100)
   - **Homework Grading (future):** Text+audio submission → AI feedback
     - Grammar errors identified with corrections
     - Pronunciation issues flagged with examples
     - Content score (relevance, completeness)

4. 🔄 **Database Schema Updates**
   ```sql
   ALTER TABLE lessons ADD COLUMN content_identifiers TEXT; -- JSON array
   ALTER TABLE lessons ADD COLUMN speaking_tier INTEGER DEFAULT 1; -- 1, 2, or 3
   ALTER TABLE lesson_progress ADD COLUMN shown_questions TEXT; -- JSON array of question IDs
   ```

5. 🕒 **Exercise Type Mapper Module** (new file: `quiz_parser.py`)
   - Function: `parse_quiz_questions(week, day) → List[QuizQuestion]`
   - Returns: question text, options, answer key, content_identifier, question_id
   - Validates 50 questions exist per day in curriculum file

### Next Steps (Phase 2C - Weeks 10-12):
- AI homework evaluation system (text+audio → structured feedback)
- Monthly comprehensive exam loading from curriculum files (DELF-aligned)
- Weakness tracking refinement by content type
- Month 2 (A1.2) curriculum file authoring begins (Weeks 5-8, pre-write grammar/vocab/quiz)

### Known Issues / Tech Debt:
- Quiz question parsing not yet implemented (need to extract 50 questions/day from markdown)
- Content identifier distribution not yet tracked (analytics gap)
- AI evaluation prompts need refinement for speaking tier scoring
- Homework grading rubric needs CEFR alignment validation
- Monthly exam files need pre-authoring (4 sections: Listening/Reading/Writing/Speaking)

## Future Enhancements (Post-Launch)
**UI/UX Polish:**
- Visual design system with color-coded content types
- Animations for lesson transitions and quiz interactions
- Richer layouts with infographics for grammar tables
- Mobile-responsive design for on-the-go learning

**Interactive Grammar Expansion (Optional Future Feature):**
- "More Explanation" button in lesson grammar section
  - Calls AI to generate ADDITIONAL explanation (not replace existing fixed content)
  - Appends supplementary examples without modifying curriculum file content
  - Use case: User confused by fixed grammar → AI provides alternative perspective
- "More Examples" button for additional practice sentences
  - AI generates new examples using same grammar topic + different content_identifier focus
  - Tracks which examples already shown to avoid duplicates
  - Use case: User wants more practice beyond 50 fixed examples

**Grammar Reference Library:**
- Curated explanations by topic (tenses, pronouns, negation, questions)
- Fixed content not subject to AI variation
- Reliable fallback when AI output insufficient
- Searchable by CEFR level and content type

**Content Identifier Analytics:**
- **Curriculum file analytics dashboard**
  - Track content_identifier distribution across all 52 curriculum files
  - Identify gaps (e.g., "role_play" underrepresented)
  - Suggest curriculum file revisions for better balance
- **Quiz question bank analytics:**
  - Track which questions from 50-question banks shown most/least
  - Identify overused questions (shown >10 times to same user)
  - Flag difficult questions (low accuracy rate across users)
  - Suggest question rewrites or retirements

**Advanced Vocabulary Practice:**
- Image-based learning (match French word to photo)
- Synonym/antonym games using semantic_field identifier
- Word family exploration (root word + derivatives)
- Pronunciation drills with phonetic breakdown

**Speaking Practice Enhancements:**
- Real-time feedback on pronunciation (phoneme-level analysis)
- Conversation partner AI with memory (remembers previous dialogues)
- Role-play scenarios with branching dialogue trees
- Video-based situational practice (react to French movie clips)

**Homework System Enhancements (Feedback #10):**
- Homework at end of every lesson with AI evaluation
- Re-submission workflow based on success thresholds (<70% triggers retry)
- Chat-based feedback before re-submission (AI tutor explains errors)
- Initial lesson exemption from homework check (first attempt always passes)
- Homework completion blocks progression (can't advance to next day without passing)

**Social Learning Features:**
- Peer review option (community feedback on writing/speaking)
- Discussion forums by week/topic
- Study groups with shared progress tracking
- Leaderboards by content type mastery (optional opt-in)
