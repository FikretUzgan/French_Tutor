# Planning Documents Update Summary

## Date: 2026-02-08
## Feature: Dynamic Lesson Generation System (Critical Path Update)

---

## Documents Created

### 1. [DYNAMIC_LESSON_GENERATION.md](DYNAMIC_LESSON_GENERATION.md)
**Comprehensive Design Specification**

Contains:
- System overview (problem, benefits, architecture)
- Curriculum file structure explanation
- Frontend & backend architecture
- Complete API endpoint specification (`POST /api/lessons/generate`)
- **6 AI Prompts with detailed documentation:**
  1. **System Prompt** - Big picture, role definition, course scope
  2. **Lesson Generation Prompt** - Main curriculum-to-lesson transformation
  3. **Weakness Personalization Subprompt** - Targeted scaffolding
  4. **Homework Evaluation Prompt** - Automatic grading criteria
  5. **Speaking Feedback Prompt** - Real-time speaking practice feedback
  6. **Quiz Answer Evaluation Prompt** - Question-level answer checking
- Complete data flow diagram
- Implementation checklist (backend, database, frontend, documentation)
- Testing strategy (unit, integration, manual, prompt validation)
- Risk mitigation table
- Future enhancement ideas

**Key Section:** See "4. AI Prompts" - All 6 prompts fully defined with examples and usage context

---

### 2. [TODO_DYNAMIC_LESSONS.md](TODO_DYNAMIC_LESSONS.md)
**Detailed Implementation To-Do List**

Organized by 7 phases with specific, actionable tasks:

**Phase 1: Backend Implementation (Weeks 1-2)**
- Curriculum file parsing module
- AI prompt engineering & templates
- Prompt context builders
- Main lesson generation function
- [ ] 1.4.1 `generate_lesson_from_curriculum()` with all steps

**Phase 2: API Endpoint Implementation (Week 2)**
- [ ] POST /api/lessons/generate endpoint
- [ ] lesson_generation_history database table
- [ ] Student profile helper functions
- [ ] Error handling & fallbacks

**Phase 3: Frontend Implementation (Week 3)**
- [ ] Week/day selector UI
- [ ] generateLesson() function update
- [ ] Dynamic lesson display rendering
- [ ] Session navigation between days

**Phase 4: Integration & Testing (Week 4)**
- [ ] End-to-end testing for all weeks
- [ ] Prompt quality validation
- [ ] Performance benchmarking
- [ ] Error scenario testing
- [ ] Database persistence testing

**Phase 5: AI Prompt Refinement (Ongoing)**
- Continuous quality monitoring
- Prompt documentation with version history
- Student feedback integration loop

**Phase 6: Documentation (Ongoing)**
- Technical architecture documentation
- Operational runbooks
- Prompt engineering guide

**Phase 7: Additional Features (Post-MVP)**
- Lesson review functionality
- Curriculum search
- Adaptive difficulty

---

## Documents Updated

### 1. [Implementation_Plan.md](Implementation_Plan.md)
**Changes Made:**

- **Added Phase 2A: Dynamic Lesson Generation System (Weeks 5-6)**
  - New critical path feature that must complete before Phase 2B
  - Includes curriculum loader, AI prompts, API endpoint, week/day selector UI
  - Lists key AI prompts: SYSTEM_PROMPT, LESSON_GENERATION_PROMPT, WEAKNESS_PERSONALIZATION_SUBPROMPT
  - Detailed acceptance criteria (9 points verifying curriculum alignment, dynamic generation, error handling)
  - Risk mitigation strategies

- **Refactored Phase 2B: Core Features (Weeks 7-12)**
  - Changed to leverage dynamically generated lessons
  - Emphasis on: "lessons are now GENERATED, not pre-stored"
  - Homework evaluation uses dedicated AI prompt with grammar/pronunciation scoring

- **Updated Phase 3-6 Timeline** (shifted 2 weeks to accommodate Phase 2A)
  - Phase 3 now: Weeks 13-20 (was 13-18)
  - Phase 4 now: Weeks 21-26 (was 19-22)
  - Phase 5 now: Weeks 27-30 (was 23-26) - Added prompt validation testing
  - Phase 6 now: Weeks 31-40 (was 27-36)

- **Updated Milestone Checkpoints**
  - Week 6: Dynamic lesson generation working (NEW checkpoint)
  - Week 12: Core features with generated lessons (updated)
  - Week 20: A1/A2 content complete (updated)
  - Week 30: UX and testing complete (updated)
  - Week 40: Beta and launch (updated)

- **Updated Phase Notes**
  - Emphasizes Phase 2A as critical path blocking Phase 2B
  - Notes curriculum file consistency requirement

---

### 2. [French_Tutor_SRS.md](French_Tutor_SRS.md)
**Changes Made:**

- **Added Section 2.1.2: Dynamic Lesson Generation System (FR-004 through FR-009)**
  - **FR-004: Curriculum-Driven Lesson Generation**
    - Complete input/process/output specification
    - Key benefits (no storage limit, no week restriction, always fresh, personalized)
  
  - **FR-005: Curriculum File Structure**
    - Required sections for all 52 weekly files
    - Consistency requirements for parsing
  
  - **FR-006: System Prompt**
    - Content, usage, token cost estimation (~300 tokens)
    - Purpose in framing AI responses
  
  - **FR-007: Lesson Generation Prompt (Main)**
    - Detailed content of what it instructs AI to do
    - Input variables (curriculum JSON, learning outcomes, vocabulary, speaking scenario, etc.)
    - Output specification (lesson JSON structure)
    - Token cost estimation (~2000-3000 tokens)
    - Failure modes and handling strategies
  
  - **FR-008: Weakness Personalization Subprompt**
    - When/how it's used
    - How it provides adaptive scaffolding
    - Not a standalone prompt (combined with FR-007)
  
  - **FR-009: Homework Evaluation Prompt**
    - Automatic grading against rubric
    - Scoring logic and grading scale
    - Output structure (scores, feedback, corrections)

---

## AI Prompts Summary

### Complete List of Prompts (in DYNAMIC_LESSON_GENERATION.md Section 4)

| # | Prompt Name | Purpose | Usage | Token Cost |
|---|------------|---------|-------|------------|
| 1 | **SYSTEM_PROMPT** | Frame AI role, course scope, tone | Every lesson generation | ~300 |
| 2 | **LESSON_GENERATION_PROMPT** | Transform curriculum → lesson JSON | Every lesson generation | ~2000-3000 |
| 3 | **WEAKNESS_PERSONALIZATION** | Add targeted scaffolding | When weaknesses exist | Subprompt (combined with #2) |
| 4 | **HOMEWORK_EVALUATION** | Grade homework submissions | After homework submit | ~1500 |
| 5 | **SPEAKING_FEEDBACK** | Real-time practice feedback | Push-to-talk sessions | ~500 |
| 6 | **QUIZ_EVALUATION** | Check individual quiz answers | During lesson quiz | ~300 per question |

**Cost Estimation per Lesson Generation:**
- System Prompt: 300 tokens
- Lesson Generation Prompt: 2500 tokens (average)
- **Total per lesson: ~2800 tokens**
- At Google's free tier & pricing: Manageable for development/testing

---

## Key Design Decisions

✅ **Curriculum files as source of truth** - No pre-stored lessons in DB  
✅ **Dynamic generation on demand** - Fresh examples every time  
✅ **Week/Day selector UI** - Replace static lesson list  
✅ **Six specialized AI prompts** - Each with specific purpose (no single mega-prompt)  
✅ **Weakness-aware personalization** - Extra scaffolding without lowering standards  
✅ **Error handling with fallbacks** - Missing files, API timeouts handled gracefully  
✅ **Prompt validation testing** - Ensure curriculum compliance before release  

---

## Acceptance Criteria for Planning Phase ✓

- [x] To-do list created with specific, actionable tasks (TODO_DYNAMIC_LESSONS.md)
- [x] Implementation plan updated with Phase 2A (critical path)
- [x] SRS updated with FR-004 through FR-009 (Dynamic Lesson Generation)
- [x] All 6 AI prompts documented (DYNAMIC_LESSON_GENERATION.md, Section 4)
- [x] Prompts mention in both SRS (FRs) and Design Document
- [x] Test strategy documented in implementation plan
- [x] Risk mitigation identified

---

## Next Steps

When ready to implement, follow in this order:

1. **Review** all three planning documents
2. **Validate** that 52 curriculum files (wk1-wk52.md) have consistent structure
3. **Start Phase 2A** (Week 5-6 per updated plan):
   - Week 5: Backend implementation (curriculum_loader.py, ai_prompts.py)
   - Week 6: API endpoint + frontend + test
4. **Execute** to-do list items sequentially
5. **Use SRS FR-004 through FR-009** as acceptance criteria during development

---

## Document Cross-References

- **For Architecture Details:** See [DYNAMIC_LESSON_GENERATION.md](DYNAMIC_LESSON_GENERATION.md) Section 3 (System Architecture)
- **For AI Prompts:** See [DYNAMIC_LESSON_GENERATION.md](DYNAMIC_LESSON_GENERATION.md) Section 4 (AI Prompts)
- **For To-Do Tasks:** See [TODO_DYNAMIC_LESSONS.md](TODO_DYNAMIC_LESSONS.md) (all 7 phases)
- **For Functional Requirements:** See [French_Tutor_SRS.md](French_Tutor_SRS.md) FR-004 through FR-009
- **For Timeline & Milestones:** See [Implementation_Plan.md](Implementation_Plan.md) Phase 2A, Updated Milestones

