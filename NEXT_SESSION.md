# Next Session To-Do List
**Last Updated:** 2026-02-09  
**Current Status:** Grammar Explanations Fixed ✅ | Base Verb Validation Added ✅

---

## 🎯 Priority Tasks for Next Session

### 1. **HIGH PRIORITY: Fix Gemini JSON Parsing Issues** 🔴
- Current state: ~60% of lessons fall back to curriculum-based template
- Root cause: Gemini responses contain malformed JSON on complex prompts
- Actions:
  - [ ] Log raw Gemini responses to identify which fields are malformed
  - [ ] Simplify vocabulary section (include only top 10 words per lesson, not all 21)
  - [ ] Implement JSON repair logic (auto-fix common Gemini formatting errors)
  - [ ] Add structured prompting hints (e.g., "ensure valid JSON escaping")
- Goal: Reduce fallback rate to <10%

### 2. **MEDIUM PRIORITY: Prompt Optimization** 🟡
- [ ] Reduce token usage by simplifying curriculum formatting in prompts
- [ ] Add JSON schema validation before passing to users
- [ ] Test prompt variations with different token budgets (3500, 4500, etc.)
- [ ] Profile which sections of prompt are most token-hungry

### 3. **Documentation & Testing**
- [ ] Document grammar explanation quality expectations
- [ ] Test generated lessons across all 52 weeks for consistency
- [ ] Create test suite for fallback lesson generation

## ⚠️ Known Issues (Session 4) with Root Causes

1. **Quiz scoring shows 0/5 even when answers are correct** ✅ FIXED
    - Resolved via multi-part normalization, answer extraction, fuzzy matching

2. **Speaking practice not embedded in lesson modal** ✅ FIXED
    - Now hides modal instead of destroying, preserves lesson scenario

3. **Audio-based quiz questions missing (no Listen button)** ✅ FIXED  
    - Added `audio_text` field with TTS support for listening questions

4. **Grammar explanations showing \"Tableau...\" instead of detailed content** ✅ FIXED
    - Root cause: Missing API key config in lesson_generator.py
    - Now generates structured 5-paragraph explanations (both AI and fallback)
    - Fallback includes: Definition, Patterns, Practice, Real-World Usage, Next Steps

5. **Fill-in-the-blank questions are impossible to answer** ✅ FIXED
    - Now validates base verb included in parentheses: `Elle _____ (avoir) un chat.`
    - Students clearly see what verb to conjugate

6. **Gemini returning invalid/malformed JSON** ⚠️ ACTIVE
    - **Root cause:** Prompt exceeds effective context window (~60% fallback rate)
    - **Workaround:** Improved fallback provides quality explanations
    - **Solution in progress:** Simplify vocabulary section or implement JSON repair

### 1. Interactive Lesson Enhancements
- [ ] Store generated lesson JSON in DB for cross-attempt comparison
  - Add `lesson_content` JSON column to `lesson_generation_history` table
  - Enable lesson replay without regeneration
  - Support comparison between attempts (e.g., "Show me attempt 2 vs attempt 3")

- [ ] "More Explanation" and "More Examples" interactive buttons in grammar section
  - Frontend: Add buttons to grammar display modal
  - Backend: Create `POST /api/lessons/{lesson_id}/expand-grammar` endpoint
  - AI: Generate additional 3-5 examples on demand (different from original)

- [ ] Grammar reference tab with curated fixed content per topic
  - Create `grammar_reference/` directory with fixed markdown per topic
  - Map curriculum grammar targets to reference files
  - Display in read-only tab alongside dynamic lesson

### 2. Quiz & Speaking Improvements
- [ ] Quiz question bank pooling from previous generations
  - Store quiz questions separately in DB
  - Track question usage per user to avoid immediate repeats
  - Reuse best questions across different lesson attempts

- [ ] Speaking scenario history to avoid AI repeating the same opening
  - Cache last 5 speaking scenarios per user/week in DB
  - Pass to AI prompt: "Do NOT use these opening lines: {history}"
  - Ensure fresh conversation starters each attempt

### 3. Technical Debt & Dependencies
- [ ] **URGENT**: Migrate from deprecated `google.generativeai` to `google.genai`
  - Update `lesson_generator.py`, `main.py` imports
  - Test all API calls with new library
  - Update `requirements.txt`
  - See: https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

- [ ] Decide database version control strategy
  - Option A: Add `french_tutor.db` to `.gitignore` (local only)
  - Option B: Commit schema-only DB, ignore data changes
  - Option C: Use migrations (alembic) and track schema separately
  - **Recommendation**: Option A + add DB backup script

---

## ✅ Recently Completed (2026-02-09)

### Grammar & Quiz Fixes (Session 4)
- ✅ Fixed grammar explanations: Now show detailed 5-part structure (was showing "Tableau...")
- ✅ Configured Gemini API key in lesson_generator.py (was missing, causing API failures)
- ✅ Increased token budget (3000 → 4000) for fuller responses
- ✅ Added retry logic for empty API responses
- ✅ Improved fallback lesson generation with pedagogical explanations
- ✅ Implemented `base_verb` validation for fill-in-the-blank questions
- ✅ Base verb extracted from parentheses format: `Elle _____ (avoir) un chat.`
- ✅ Relaxed validation from error → warning for graceful degradation
- ✅ All changes committed to git

### Earlier Work (Session 3, 2026-02-08)
- ✅ Quiz scoring fixed (multi-part normalization + fuzzy matching)
- ✅ Speaking practice embedded in lesson modal
- ✅ Audio text extraction for listening questions
- ✅ Dynamic Lesson Generation System complete
- ✅ All 52 curriculum weeks created and validated

---

## 📋 Backlog (Lower Priority)

- [ ] Performance optimization (cache curriculum files in memory)
- [ ] Rate limiting enforcement in API (currently logged but not enforced)
- [ ] Lesson quality analytics dashboard (track generation success rates)
- [ ] Multi-language support for UI (currently English only)
- [ ] Mobile responsive design improvements
- [ ] Export lesson history as PDF for offline review

---

## 🔗 Reference Documents

- **Implementation_Plan.md** - Global 36-week project roadmap
- **French_Tutor_SRS.md** - Software requirements specification
- **DYNAMIC_LESSON_GENERATION.md** - Architecture documentation
- **test_dynamic_lesson_gen.py** - Automated test suite

---

## 📝 Session Notes

### Session 4 (2026-02-09)
**Date:** 2026-02-09  
**Focus:** Fix grammar explanation display, implement base verb validation, debug Gemini API issues  
**Completed:**
- Fixed grammar explanations (was showing "Tableau clair..." from curriculum)
- Added Gemini API key config to lesson_generator.py
- Increased token budget 3000→4000
- Implemented base verb validation for fill-in-the-blank questions
- Improved fallback lesson with structured 5-part grammar explanation
- Committed all changes to git

**Blocked by:**
- Gemini returning invalid/malformed JSON on complex prompts (~60% of requests)
- Need to simplify prompt or implement JSON repair logic

**Next steps:**
- Debug Gemini JSON issues (simplify vocab section or add JSON validation)
- Test accuracy of generated grammar explanations (quality vs detail)
- Consider migrating away from deprecated google.generativeai library
