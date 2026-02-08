# Dynamic Lesson Generation System

**Feature:** On-demand lesson generation from curriculum files  
**Status:** Planning Phase  
**Date Created:** 2026-02-08  
**Target Implementation:** Phase 2

---

## 1. Overview

Instead of pre-storing lessons in a database, the system will:
1. Load curriculum content from weekly markdown files (`wk1.md` - `wk52.md`)
2. Generate fresh lessons dynamically when user clicks "Start Lesson"
3. Provide AI with complete context (big picture, week/day, student profile, curriculum)
4. Return dynamically generated lesson content with grammar, vocabulary, speaking, and quiz

### Key Benefits
- **No week restriction** - Students can start at any week (currently limited to wk5 due to DB)
- **Fresh content each time** - Same week/day generates new examples and questions
- **Curriculum-aligned** - AI strictly follows structured weekly plans
- **Adaptive difficulty** - AI considers student weaknesses and level

---

## 2. Curriculum File Structure

Each `wk{N}.md` contains:
- **Learning Outcomes** (CEFR descriptors)
- **Grammar Target** (form, complexity, prerequisites, scaffolding steps)
- **Vocabulary Set** (21 words with semantic domain)
- **Speaking Scenario** (prompt, domain, AI role expectations)
- **Reading/Listening Component** (type, content description, comprehension tasks)
- **Homework Assignment** (type, task description, rubric)

Example: `New_Curriculum/wk5.md` = Week 5 (A1.2) = Passé Composé focus

---

## 3. System Architecture

### 3.1 Frontend Changes (Web UI)

**Remove:** Lesson selection from pre-stored database  
**Add:** Week/Day selector

```
┌─────────────────────────────────────────┐
│  Lesson Selection                       │
├─────────────────────────────────────────┤
│  Week: [Dropdown: 1-52]                 │
│  Day:  [Buttons: 1 2 3 4 5]             │
│  Start Lesson →                         │
└─────────────────────────────────────────┘
```

**Flow:**
1. User selects Week 5, Day 2
2. Click "Start Lesson"
3. Fetch `/api/lessons/generate` with week=5, day=2
4. Render generated lesson content in lesson view

### 3.2 Backend Architecture

#### New Endpoint: `POST /api/lessons/generate`

```json
{
  "week": 5,
  "day": 2,
  "student_level": "A1.2",
  "student_weaknesses": ["passé composé agreement", "pronunciation"],
  "user_id": 1
}
```

**Response:**
```json
{
  "lesson_id": "wk5_day2_20260208_user1",
  "title": "Passé Composé: Regular Verbs with Avoir",
  "level": "A1.2",
  "theme": "Daily Activities & Recent Past",
  "grammar": {
    "explanation": "...",
    "form": "avoir + participe passé",
    "examples": ["...", "...", "..."],
    "conjugation_table": "...",
    "focus_on_weakness": "agreement with avoir"
  },
  "vocabulary": [
    {"word": "manger", "translation": "to eat", "example": "..."},
    ...
  ],
  "speaking": {
    "prompt": "Raconte-moi ce que tu as fait hier...",
    "targets": ["use 5 passé composé verbs", "natural flow", "clear pronunciation"],
    "expected_elements": ["time expression", "action verb", "object"]
  },
  "quiz": {
    "questions": [
      {"type": "fill", "text": "Hier, je ___ mangé une pizza", "correct": "ai"},
      ...
    ]
  },
  "homework": {
    "type": "audio",
    "prompt": "Describe your last weekend using 8+ passé composé verbs",
    "requirements": ["min 30s", "5+ verbs", "clear pronunciation"]
  },
  "session_metadata": {
    "estimated_duration": 30,
    "recommended_pace": "go slowly on agreement"
  }
}
```

#### Process Flow

```
User clicks "Start Lesson" (week 5, day 2)
    ↓
POST /api/lessons/generate
    ↓
✓ Read wk5.md from filesystem
✓ Parse curriculum structure
✓ Build system prompt (big picture)
✓ Build week/curriculum context
✓ Get student profile (level, weaknesses)
✓ Call Gemini API with complete context
    ↓
Gemini returns structured lesson JSON
    ↓
Store lesson metadata in DB (for history/tracking)
    ↓
Return lesson to frontend
    ↓
Frontend renders lesson UI
```

---

## 4. AI Prompts

### 4.1 System Prompt (Big Picture)

**Purpose:** Frame the AI's role and course scope  
**Used in:** Every lesson generation call  

```
You are a French tutor following a rigorous 52-week curriculum (A1 → B2, CEFR-aligned).

Context:
- This is week {week} of {total_weeks} weeks
- Current CEFR Level: {student_level}
- Student has completed weeks: {completed_weeks}
- Known weaknesses: {weaknesses_list}

Course Philosophy:
- Grammar-focused with contextual vocabulary
- Practical scenarios (daily life, travel, work)
- Productivity over perfection
- Explicit error correction with reasoning
- Homework is mandatory and blocks lesson progression

Your role:
- Deliver curriculum content EXACTLY as specified in the weekly plan
- Provide clear, scaffolded explanations with 5+ examples
- Focus on structures that are prerequisites for future weeks
- Adapt difficulty if student shows specific weaknesses
- Use English comparisons for clarity
- Keep tone encouraging but rigorous ("strict professor")

Do NOT:
- Deviate from the weekly curriculum
- Skip grammar prerequisites
- Use overly simplified French
- Give vague feedback without specific corrections
```

### 4.2 Lesson Generation Prompt

**Purpose:** Generate lesson content from curriculum data  
**Input:** Curriculum metadata + student profile  

```
Generate a {student_level} French lesson for Week {week}/Day {day}.

Curriculum Framework:
{curriculum_json}

Learning Outcomes This Week:
{learning_outcomes}

Grammar Target:
{grammar_target}

Vocabulary Set (use ALL 21 words):
{vocabulary_list}

Speaking Scenario Requirements:
{speaking_requirements}

Homework Task:
{homework_task}

Student Context:
- Level: {student_level}
- Completed lessons: {completed_weeks_count}
- Known weaknesses: {weaknesses_json}
- Previous homework quality: {homework_quality_summary}

Instructions:
1. Generate lesson following this EXACT structure:
   {
     "grammar": {
       "explanation": "Clear explanation with English parallels (100-150 words)",
       "form": "The specific grammar pattern",
       "examples": [5+ example sentences with English translations],
       "conjugation_table": "If applicable, provide conjugation grid",
       "scaffolding_steps": [List the 7 scaffolding steps from curriculum],
       "focus": "If student has weakness in this area, explicitly address it"
     },
     "vocabulary": [
       {
         "word": "French word",
         "part_of_speech": "noun/verb/adj",
         "translation": "English translation",
         "example_sentence": "French example with translation",
         "pronunciation_tips": "If relevant"
       }
       ... (all 21 words)
     ],
     "speaking": {
       "prompt": "Scenario prompt in French",
       "targets": ["target 1", "target 2", "target 3"],
       "expected_elements": ["element the student should include"],
       "difficulty_level": "easy/moderate/challenging"
     },
     "quiz": {
       "questions": [
         {
           "type": "fill_blank|mcq|translation|reading",
           "text": "Question in English for clarity",
           "options": ["Option A", "Option B", ...],
           "correct_answer": "The correct answer",
           "explanation": "Why this is correct and why others are wrong"
         }
         ... (3-5 questions)
       ]
     },
     "homework": {
       "prompt": "The homework task",
       "requirements": ["requirement 1", "requirement 2"],
       "rubric": ["criterion 1: min threshold", "criterion 2: min threshold"],
       "estimated_time": "X minutes"
     }
   }

2. Ensure:
   - Grammar explanations have minimum 5 examples
   - ALL 21 vocabulary words are used in examples
   - Speaking scenario integrates vocabulary and grammar
   - Quiz tests grammar AND vocabulary
   - Homework is challenging but achievable for the level
   - If student showed weakness in {weaknesses}, provide extra scaffolding

3. Language:
   - Explanations in English
   - Examples and prompts in French
   - Use formal French (vous) in scenarios
   - Include pronunciation tips only when relevant

Return ONLY valid JSON. No markdown, no extra text.
```

### 4.3 Student Weakness Personalization Subprompt

**Purpose:** Tailor lesson to specific weaknesses  
**Trigger:** When `student_weaknesses` array is non-empty  

```
PERSONALIZATION NOTE:

This student has documented difficulties with: {weaknesses}

For this lesson:
1. Add an extra example for each weakness (min 2)
2. In the grammar explanation, explicitly compare to English/Spanish if helpful
3. In the homework, include at least one exercise that targets the weakness
4. In quiz questions, ensure that one question specifically tests the weakness
5. In speaking targets, note if there's a pronunciation-related weakness

This is NOT about lowering standards—it's about providing extra scaffolding while maintaining rigor.
```

### 4.4 Homework Evaluation Prompt

**Purpose:** Evaluate homework submissions against rubric  
**Used in:** POST `/api/homework/submit`  

```
You are evaluating a homework submission against this rubric:

Lesson: Week {week}, Day {day} ({level})
Homework Task: {homework_prompt}
Success Criteria: {homework_rubric}

Student Submission:
- Text: "{homework_text}"
- Audio transcription (STT): "{audio_transcription}"

Evaluate and return JSON with:
{
  "text_score": {0-100},
  "text_feedback": "Specific feedback on grammar, vocab, content",
  "audio_score": {0-100},
  "audio_feedback": "Feedback on pronunciation, rhythm, clarity",
  "passed": {true/false},
  "corrections": [{
    "type": "grammar|vocabulary|pronunciation",
    "error_text": "What the student said/wrote",
    "correction": "The corrected version",
    "explanation": "Why this is correct"
  }],
  "strengths": ["What the student did well"],
  "next_focus": "One specific thing to focus on next lesson"
}

Grading Scale:
- 100-90: Excellent (no significant errors)
- 89-75: Good (minor errors, meaning clear)
- 74-70: Passing (some errors but meets requirements)
- <70: Needs revision (major errors affect meaning)

Be specific, cite exact words, and give actionable feedback.
```

### 4.5 Speaking Feedback Prompt

**Purpose:** Provide real-time speaking practice feedback  
**Used in:** Interactive speaking practice (push-to-talk)  

```
A student completed a speaking practice scenario in French.

Scenario: {speaking_prompt}
Targets: {speaking_targets}

What they said (transcribed): "{student_response}"

Provide brief, encouraging feedback (3-4 sentences max):
1. Did they address the scenario? (yes/no + evidence)
2. Grammar and vocabulary quality
3. One specific suggestion for improvement

Respond ONLY in French (no English).
Keep it under 100 words.
Be encouraging but constructive.

Format as plain text, not JSON.
```

### 4.6 Quiz Answer Evaluation Prompt

**Purpose:** Evaluate quiz responses with explanation  
**Used in:** During lesson quiz questions  

```
Quiz Question: {question_text}
Question Type: {question_type}
Correct Answer: {correct_answer}

Student Answer: "{student_answer}"

Return JSON:
{
  "is_correct": {true/false},
  "feedback": "1-2 sentences explaining why (or why not)",
  "explanation": "Why the correct answer is right",
  "hint_next_time": "If wrong, a hint for how to approach this type of question"
}
```

---

## 5. Data Flow Diagram

```
┌─────────────────────────────────────────┐
│  Frontend: "Start Lesson Week 5 Day 2"  │
└────────────────────┬────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ POST /api/lessons/     │
        │ generate               │
        │ {week, day, level,     │
        │  user_id}              │
        └────────────┬───────────┘
                     │
        ┌────────────↓─────────────────────┐
        │  Backend: Lesson Generation      │
        ├──────────────────────────────────┤
        │  1. Read wk5.md from filesystem  │
        │  2. Parse curriculum metadata    │
        │  3. Get student profile from DB  │
        │  4. Build system prompt          │
        │  5. Build content prompt         │
        │  6. Call Gemini API              │
        │  7. Parse JSON response          │
        │  8. Store lesson_id + metadata   │
        │  9. Return lesson_content        │
        └────────────┬─────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────┐
        │  Gemini API                     │
        │  (System + Lesson Prompt)       │
        │  Returns: Lesson JSON           │
        └────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────┐
        │  Database: Log Lesson Generated │
        │  - lesson_id (generated)        │
        │  - week, day                    │
        │  - user_id                      │
        │  - timestamp                    │
        │  - curriculum used              │
        └────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────┐
        │  Return to Frontend             │
        │  {lesson_content, session info} │
        └────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────┐
│  Frontend: Render Lesson UI              │
│  - Grammar section                       │
│  - Vocabulary practice                   │
│  - Speaking scenario (push-to-talk)      │
│  - Quiz questions                        │
│  - Homework prompt                       │
└──────────────────────────────────────────┘
```

---

## 6. Implementation Checklist

### Backend (main.py)
- [ ] Create `POST /api/lessons/generate` endpoint
- [ ] Create `load_curriculum_file(week: int)` function
- [ ] Create `build_lesson_generation_prompt()` function
- [ ] Create `build_system_prompt()` function
- [ ] Implement error handling for missing curriculum files
- [ ] Add logging for lesson generation requests

### Database (db.py)
- [ ] Create `lesson_generation_history` table
  - lesson_id, week, day, user_id, timestamp, curriculum_file, generated_content
- [ ] Add `store_generated_lesson()` function
- [ ] Add `get_student_weaknesses(user_id)` function
- [ ] Add `get_completed_weeks(user_id)` function

### Frontend (app.js)
- [ ] Add week/day selector UI
- [ ] Replace lesson list with week/day controls
- [ ] Update `generateLesson()` function to call `/api/lessons/generate`
- [ ] Update lesson display to handle dynamic content
- [ ] Add loading state ("Generating lesson...")

### Documentation
- [ ] Document each AI prompt with examples
- [ ] Add prompt engineering notes
- [ ] Document curriculum file parsing logic

---

## 7. Testing Strategy

### Unit Tests
- [ ] Test curriculum file parsing (valid JSON structure)
- [ ] Test prompt building functions
- [ ] Test response JSON validation

### Integration Tests
- [ ] Full flow: select week/day → generate → display lesson
- [ ] Test with missing curriculum file (graceful error)
- [ ] Test with API timeout (fallback message)
- [ ] Test with invalid week number (bounds checking)

### Manual Tests
- [ ] Generate lesson for each level (A1.1, A1.2, A2.1, etc.)
- [ ] Verify curriculum content matches expected structure
- [ ] Check that weaknesses are actually addressed in lesson content
- [ ] Verify homework rubric matches curriculum requirements

---

## 8. Future Enhancements

- **Lesson Review:** Re-generate same week/day with different examples
- **Difficulty Adjustment:** Adapt lesson difficulty based on real-time performance
- **Multi-day tracking:** Show progress across week (day 1/7 complete)
- **Curriculum Search:** Find lessons by grammar topic, vocabulary, scenario type
- **Fallback Lessons:** Pre-generated backups if API unavailable

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| API rate limits | Cache lesson for 1 hour per user; implement retry logic |
| File parsing errors | Validate curriculum file structure; provide fallback prompt |
| Timeout issues | Set 30s timeout; show "Please wait..." message |
| Weak prompt output | Test prompts thoroughly; iterate before production |
| Student stuck on week | Allow skipping to next week with warning |

