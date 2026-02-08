# French Tutor - Implementation To-Do List
## Dynamic Lesson Generation System (Current Sprint)

**Status:** Planning Phase  
**Priority:** Critical Path  
**Target Completion:** Before playable UI phase  
**Created:** 2026-02-08  

---

## PHASE 1: Backend Implementation (Weeks 1-2)

### 1.1 Curriculum File Parsing
- [ ] **1.1.1** Create `curriculum_loader.py` module
  - [ ] Function `load_curriculum_file(week_number)` → returns dict with parsed metadata
  - [ ] Function `parse_learning_outcomes(markdown_text)` → list of strings
  - [ ] Function `parse_grammar_target(markdown_text)` → {form, complexity, prerequisites, scaffolding}
  - [ ] Function `parse_vocabulary_set(markdown_text)` → list of 21 words/definitions
  - [ ] Function `parse_speaking_scenario(markdown_text)` → {domain, prompt, ai_role}
  - [ ] Function `parse_homework_task(markdown_text)` → {type, task_desc, rubric}
  - [ ] Error handling for missing files and malformed content
  - [ ] Unit tests for each function

### 1.2 Prompt Engineering & System Prompts
- [ ] **1.2.1** Create `ai_prompts.py` module with all prompt templates
  - [ ] SYSTEM_PROMPT: Big picture, role definition, course scope
  - [ ] LESSON_GENERATION_PROMPT: Main prompt for generating lesson JSON
  - [ ] WEAKNESS_PERSONALIZATION_SUBPROMPT: Adaptation for weaknesses
  - [ ] HOMEWORK_EVALUATION_PROMPT: Homework grading template
  - [ ] SPEAKING_FEEDBACK_PROMPT: Push-to-talk feedback
  - [ ] QUIZ_EVALUATION_PROMPT: Quiz answer checking
  - [ ] Document all prompts with:
    - [ ] Purpose and when used
    - [ ] Expected input variables
    - [ ] Expected output format (JSON or text)
    - [ ] Example input/output pairs
    - [ ] Token count estimation (for cost tracking)

### 1.3 Prompt Context Builders
- [ ] **1.3.1** Create prompt building functions
  - [ ] `build_system_prompt(student_level, completed_weeks, weaknesses)` → string
  - [ ] `build_lesson_generation_context(week, day, curriculum_data, student_profile, weaknesses)` → string
  - [ ] `format_curriculum_for_prompt(curriculum_dict)` → formatted string
  - [ ] `format_student_weaknesses_for_prompt(weaknesses_list)` → formatted string
  - [ ] Test all builders with mock data
  - [ ] Verify token counts stay within limits

### 1.4 Lesson Generation Function
- [ ] **1.4.1** Create main lesson generation logic in `main.py`
  - [ ] `generate_lesson_from_curriculum(week_num, day_num, student_level, user_id)` → dict
  - [ ] Load curriculum file
  - [ ] Get student profile from DB (level, completed_weeks, weaknesses)
  - [ ] Build system + content prompts
  - [ ] Call Gemini API with error handling
  - [ ] Validate response JSON schema
  - [ ] Fallback handling (default lesson structure if API fails)
  - [ ] Return lesson dict with: lesson_id, grammar, vocabulary, speaking, quiz, homework, metadata

---

## PHASE 2: API Endpoint Implementation (Week 2)

### 2.1 RESTful Endpoint
- [ ] **2.1.1** Create `POST /api/lessons/generate` endpoint in `main.py`
  - [ ] Accept: week (1-52), day (1-7), student_level (A1.1-B2.2), user_id (optional, default=1)
  - [ ] Validate input bounds
  - [ ] Check rate limiting (max 1 req/user/hour to prevent spam)
  - [ ] Call `generate_lesson_from_curriculum()`
  - [ ] Return lesson JSON or 500 error with fallback
  - [ ] Log all requests with timestamp, user_id, week, day

### 2.2 Database Schema Updates
- [ ] **2.2.1** Create `lesson_generation_history` table in `db.py`
  - Columns: id, user_id, lesson_id, week, day, timestamp, curriculum_file, status, error_msg
  - [ ] Add migration/init logic to `init_db()`
  - [ ] Add `store_generated_lesson(user_id, week, day, lesson_id, curriculum_file)` function
  - [ ] Add `get_lesson_generation_history(user_id, limit=20)` function

### 2.3 Student Profile Functions
- [ ] **2.3.1** Add helper functions in `db.py`
  - [ ] `get_student_weaknesses(user_id, limit=5)` → list of {topic, error_count}
  - [ ] `get_completed_weeks(user_id)` → list of week numbers
  - [ ] `get_student_level(user_id)` → current level string
  - [ ] `get_homework_quality_summary(user_id, recent_n=5)` → quality metrics
  - [ ] Add error handling for missing user data

### 2.4 Error Handling & Fallbacks
- [ ] **2.4.1** Implement graceful degradation
  - [ ] Handle missing curriculum files → return error with helpful message
  - [ ] Handle API timeouts → return cached lesson or fallback
  - [ ] Handle JSON parsing errors → log and return error
  - [ ] Handle rate limit (429) → queue request or return error
  - [ ] Create fallback lesson template (basic structure, no personalization)

---

## PHASE 3: Frontend Implementation (Week 3)

### 3.1 UI Components
- [ ] **3.1.1** Create week/day selector UI in `app.js`
  - [ ] Remove old lesson list view
  - [ ] Add `<select id="week-selector">` (1-52)
  - [ ] Add day buttons: `<button class="day-btn" data-day="1-7">`
  - [ ] Add "Start Lesson" button
  - [ ] Style with CSS (horizontal layout, clear labels)
  - [ ] Show current week/day selection clearly

### 3.2 Generate Lesson Function
- [ ] **3.2.1** Update `app.js` to call new endpoint
  - [ ] Create `generateLesson(week, day)` function
  - [ ] Call `POST /api/lessons/generate` with week, day, user_id
  - [ ] Show loading spinner ("Generating lesson...")
  - [ ] Handle errors gracefully (show retry button)
  - [ ] Call `displayLesson(lessonContent)` on success

### 3.3 Lesson Display
- [ ] **3.3.1** Update lesson rendering to handle dynamic content
  - [ ] `displayLesson(lessonContent)` render all sections:
    - [ ] Grammar explanation with examples
    - [ ] Vocabulary with pronunciation tips
    - [ ] Speaking scenario (with push-to-talk UI)
    - [ ] Quiz questions (multiple choice, fill-blank, translation)
    - [ ] Homework prompt with requirements
  - [ ] Add "Lesson Details" (week, day, level, estimated time)
  - [ ] Add visual progress indicator

### 3.4 Session Navigation
- [ ] **3.4.1** Implement navigation between days/weeks
  - [ ] "Next Day" button (only if homework passed)
  - [ ] "Jump to Week" warning if skipping ahead
  - [ ] Show "homework blocking" message if attempting skip
  - [ ] Display current progress (e.g., "Week 5, Day 2 of 7")

---

## PHASE 4: Integration & Testing (Week 4)

### 4.1 End-to-End Testing
- [ ] **4.1.1** Test full lesson generation flow
  - [ ] [ ] Test Week 1 → Should generate A1.1 lesson
  - [ ] [ ] Test Week 5 → Should use passé composé curriculum
  - [ ] [ ] Test Week 52 → Should work (B2.2)
  - [ ] [ ] Verify grammar matches curriculum
  - [ ] [ ] Verify all 21 vocabulary words are used
  - [ ] [ ] Verify speaking prompt matches scenario type
  - [ ] [ ] Verify homework rubric aligns with learning outcomes

### 4.2 Prompt Quality Testing
- [ ] **4.2.1** Validate that AI prompts work well
  - [ ] Test SYSTEM_PROMPT with different student levels
  - [ ] Test LESSON_GENERATION_PROMPT produces valid JSON
  - [ ] Test WEAKNESS_PERSONALIZATION_SUBPROMPT addresses weaknesses
  - [ ] Generate 3 lessons for same week → verify different examples (no duplicates)
  - [ ] Test with student weaknesses → verify extra scaffolding in grammar section
  - [ ] Manual review of generated grammar explanations (clarity, accuracy)
  - [ ] Manual review of examples (relevant, correct, progressive difficulty)

### 4.3 Performance Testing
- [ ] **4.3.1** Monitor API response times
  - [ ] Measure lesson generation time (target: <10s end-to-end)
  - [ ] Track Gemini API call duration
  - [ ] Identify bottlenecks (file I/O, prompt building, API latency)
  - [ ] Optimize hot paths (cache curriculum files, pre-compile prompts)

### 4.4 Error Scenario Testing
- [ ] **4.4.1** Test error handling
  - [ ] Missing curriculum file (wk99.md doesn't exist)
  - [ ] API timeout (simulate 30s delay)
  - [ ] Malformed JSON response from API
  - [ ] Invalid student_level parameter
  - [ ] Day out of range (day 8, day 0)
  - [ ] User not found in database

### 4.5 Database Testing
- [ ] **4.5.1** Verify data persistence
  - [ ] Generate lesson → stores in lesson_generation_history
  - [ ] Retrieve lesson history → matches what was generated
  - [ ] Get student weaknesses → returns correct data
  - [ ] No orphaned records after failed generation

---

## PHASE 5: AI Prompt Refinement (Ongoing)

### 5.1 Prompt Optimization
- [ ] **5.1.1** Continuous improvement of prompts
  - [ ] Monitor generated lesson quality (manual spot-checks)
  - [ ] Adjust system prompt if students report confusion
  - [ ] Improve weakness personalization based on feedback
  - [ ] Reduce token count in prompts (cost optimization)
  - [ ] Add more specific examples in complex prompts (subjunctive, conditional, etc.)

### 5.2 Prompt Documentation
- [ ] **5.2.1** Create prompt engineering guide
  - [ ] Document each prompt's purpose and history
  - [ ] Record changes and why they were made
  - [ ] Include examples of good vs bad outputs
  - [ ] Maintain prompt version control (dated entries)
  - [ ] Create prompt testing checklist

### 5.3 Student Feedback Loop
- [ ] **5.3.1** Track which aspects of lessons are confusing
  - [ ] Add "Was this explanation clear?" survey in UI
  - [ ] Log which quiz items have high failure rates
  - [ ] Correlate lesson quality with homework submission rates
  - [ ] Use feedback to iterate on prompts

---

## PHASE 6: Documentation (Ongoing)

### 6.1 Technical Documentation
- [ ] **6.1.1** Document system architecture
  - [ ] Diagram: lesson generation flow (already in DYNAMIC_LESSON_GENERATION.md)
  - [ ] Explain curriculum file format
  - [ ] Document all prompt templates with examples
  - [ ] API endpoint documentation (OpenAPI/Swagger)
  - [ ] Database schema documentation

### 6.2 Operational Documentation
- [ ] **6.2.1** Create runbooks
  - [ ] How to add a new week's curriculum (manual process)
  - [ ] How to debug API failures
  - [ ] How to monitor token usage
  - [ ] How to handle API quota limits
  - [ ] Emergency fallback procedures

---

## PHASE 7: Additional Features (Post-MVP)

### 7.1 Lesson Review Feature
- [ ] **7.1.1** Allow re-generating same week/day with different examples
  - [ ] New endpoint: `POST /api/lessons/{lesson_id}/review`
  - [ ] Mark lesson as "review" in UI
  - [ ] AI generates new content but maintains same learning objectives
  - [ ] No homework/exam requirement on review

### 7.2 Curriculum Search
- [ ] **7.2.1** Add search by topic
  - [ ] "Find all lessons about passé composé"
  - [ ] "Find all lessons with verb conjugation"
  - [ ] Database index on grammar_target

### 7.3 Adaptive Difficulty
- [ ] **7.3.1** Adjust lesson difficulty in real-time
  - [ ] Track student's quiz performance during lesson
  - [ ] If >80% correct → slightly harder vocabulary
  - [ ] If <50% correct → request simpler explanation from AI
  - [ ] Update next lesson difficulty based on homework quality

---

## Dependencies & Prerequisites

### Code Dependencies
- [ ] FastAPI (already installed)
- [ ] pydantic (already installed)
- [ ] google.generativeai (already installed)
- [ ] pathlib (built-in)
- [ ] json (built-in)

### Curriculum Files
- [ ] All 52 week files must exist: `New_Curriculum/wk1.md` through `wk52.md`
- [ ] Each file must contain the required sections (verify with curriculum_loader parsing test)
- [ ] All files must be valid markdown with consistent structure

### API Quota
- [ ] Ensure Gemini API quota is sufficient for testing (may need to increase)
- [ ] Monitor token usage during development
- [ ] Set up alerts if approaching quotas

---

## Acceptance Criteria (MVP)

✓ Users can select any week (1-52) and day (1-7)  
✓ Clicking "Start Lesson" generates fresh content from curriculum  
✓ Generated lessons include: grammar, vocabulary, speaking, quiz, homework  
✓ Grammar explanations match curriculum learning outcomes  
✓ Speaking scenarios are dynamically generated from weekly prompts  
✓ Homework aligns with weekly rubric from curriculum  
✓ Student weaknesses are addressed with extra scaffolding  
✓ Error handling: missing files, API timeouts, invalid input all handled gracefully  
✓ Lesson generation takes <10 seconds  
✓ Generated lessons persist in database for tracking  
✓ No pre-stored lessons in database needed (fully dynamic)  

---

## Success Metrics

- **User Response**: "I can finally start at week 5 without restrictions"
- **Content Quality**: Spot-check 5 generated lessons → all match curriculum requirements
- **Performance**: Average /api/lessons/generate response: 8-10 seconds
- **Reliability**: 99% successful lesson generations (retry on 1% failures)
- **AI Quality**: 0 hallucinations or curriculum violations in 100 generated lessons

