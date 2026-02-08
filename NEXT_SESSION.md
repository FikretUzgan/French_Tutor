# Next Session To-Do List
**Last Updated:** 2026-02-08  
**Current Status:** Dynamic Lesson Generation Complete ✅

---

## 🎯 Priority Tasks for Next Session

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

## ✅ Recently Completed (2026-02-08)

### Dynamic Lesson Generation System
- ✅ Complete backend implementation (curriculum_loader, ai_prompts, lesson_generator)
- ✅ Enhanced AI prompts with 5-paragraph grammar structure
- ✅ Attempt-based variation system with temperature escalation
- ✅ POST /api/lessons/generate endpoint
- ✅ Week/day selector frontend UI (1-52 weeks, 1-7 days)
- ✅ Interactive lesson modal with grammar, vocab, speaking, quiz sections
- ✅ Curriculum parsing fixes (vocabulary + homework task extraction)
- ✅ Comprehensive test suite (test_dynamic_lesson_gen.py)
- ✅ All 52 curriculum weeks validated

### Curriculum Content Creation
- ✅ All 52 weeks created (A1.1 → B2.2)
- ✅ Weekly exam rubrics and remedial templates
- ✅ Variation pools for dynamic content (contexts, adjectives, scenarios)

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

## 📝 Session Notes Template

When starting next session, add notes here:

**Date:** _____  
**Focus:** _____  
**Completed:** _____  
**Blocked by:** _____  
**Next steps:** _____
