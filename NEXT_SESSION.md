# Next Session To-Do List
**Last Updated:** 2026-02-12  
**Current Status:** Week 1 Curriculum Created ✅ | Pushed to Git ✅

---

## 📚 CURRICULUM GENERATION PROGRESS

### Completed:
✅ **Week 1 (A1.1 - Days 1-5)** - Created, committed, and pushed
  - Day 1: Être (basic)
  - Day 2: Être (plural)
  - Day 3: Avoir
  - Day 4: Regular -ER verbs
  - Day 5: Articles & gender
  - Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_1_A1.1.md`

✅ **Week 2 (A1.1 - Days 6-10)** - Created, committed, and pushed
  - Day 6: Regular -IR verbs (finir, choisir)
  - Day 7: Regular -RE verbs (vendre, attendre)
  - Day 8: Negation (ne...pas)
  - Day 9: Basic questions (est-ce que, inversion)
  - Day 10: Numbers 1-20
  - Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_2_A1.1.md`

### Next Task:
🎯 **CREATE WEEK 3 CURRICULUM**

**User command:** "Bir sonraki haftaya başla" OR "Next week please"

When user says this, automatically:
1. Create Week 3 (A1.1 - Days 11-15) curriculum file
2. Follow the same detailed format as Weeks 1-2
3. Grammar topics for Week 3:
   - Day 11: Adjectives (basic descriptive adjectives)
   - Day 12: Adjective agreement (masculine/feminine, singular/plural)
   - Day 13: Adjective placement (before/after noun)
   - Day 14: Possessive adjectives (mon, ma, mes, ton, ta, etc.)
   - Day 15: Colors and physical descriptions
4. Vocabulary: 5 words/day × 5 days = 25 words (focus: adjectives, colors, descriptions)
5. Commit with message: "Add Week 3 (A1.1) detailed curriculum - Days 11-15"
6. Push to remote
7. Update NEXT_SESSION.md for Week 4

---

## 🗓️ 52-WEEK CURRICULUM PLAN

**Structure:**
- 52 weeks total (1 year)
- Each week = 5 days of lessons
- Each week file = detailed format (like Phase_1_Example_Week_15.md)
- Vocabulary: 5 words/day
- Speaking Tier progression: 1 → 2 → 3

**Month 1 (Weeks 1-4) - A1.1:**
- ✅ Week 1: être, avoir, -ER verbs, articles
- ✅ Week 2: -IR/-RE verbs, negation, questions, numbers
- ⏳ Week 3: Adjectives, agreement, possessives, colors
- ⏳ Week 4: Review + Month 1 exam

**Month 2 (Weeks 5-8) - A1.2:**
- Passé composé (avoir/être)
- Futur proche
- Time expressions

---

## 🎨 TEACHING STYLE PREFERENCES (User Specified)

### ✅ FAVOR: Babbel Style
- **Scene/dialogue-first approach:** Start with realistic conversations, then extract grammar
- **Detailed explicit grammar:** Use 5-paragraph teacher format with tables, examples
- **Cultural context notes:** Include "Cultural Note" sections explaining French customs/usage
- **Pronunciation guidance:** Provide phonetic breakdowns for all new vocabulary
- **Structured lessons:** 25-30 min format with clear sections (like current Week 1)
- **Spaced repetition:** Vocabulary reappears automatically across lessons
- **Practical scenarios:** Real-world contexts (restaurant, travel, work, etc.)

### ✅ ALSO LIKE: Busuu Elements
- **Visual aids:** Use tables, color-coded conjugations, infographics
- **Context-based explanations:** "You'll use this when ordering at a café"
- **Structured vocabulary:** Images/audio presentation before grammar
- **Bullet-point focused:** Concise, scannable grammar rules
- **Social/speaking practice:** Community-style peer review concepts

### ❌ AVOID: Duolingo Style
- **No micro-lessons:** Keep 30-min structured format (not 2-5 min quick games)
- **No heavy gamification:** Avoid streaks, XP points, leagues, competition elements
- **No implicit learning:** Always provide explicit grammar rules upfront
- **No minimal explanations:** Don't let grammar "emerge" without clear teaching
- **No image-matching games:** Focus on practical conversation over matching exercises

### Applied to Week 1 ✅
- ✅ Explicit 5-paragraph grammar explanations (Babbel style)
- ✅ Cultural notes included each day
- ✅ Real-world dialogue examples (Scene-based)
- ✅ Pronunciation provided for all vocabulary
- ✅ 30-min structured lessons with clear sections
- ✅ Practical scenarios (meeting people, introductions, etc.)

### For Future Weeks:
- Continue Babbel/Busuu structured approach
- Emphasize dialogue-first scenarios
- Include more cultural context specific to each grammar topic
- Use visual tables and color-coding where helpful
- Avoid gamification language (no "earn XP" or "level up")

---

## ⚠️ CRITICAL: Package Dependencies - DO NOT CHANGE

### Google Generative AI Package
**USE:** `google-generativeai` (working)  
**NEVER USE:** `google.genai` (breaks the application)

---

## 🎯 Secondary Tasks (After Week 2)

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
