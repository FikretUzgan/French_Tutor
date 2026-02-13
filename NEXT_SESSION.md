# Next Session To-Do List

**Last Updated:** 2026-02-12  
**Current Status:** Week 13 Curriculum Created ✅ | Month 4 Started (A2.2) ✅ | New Curriculum System Live ✅

---

## 🔄 WORKFLOW FOR EACH SESSION

**IMPORTANT:** At the start of EVERY new session:

1. **Read Phase_2_Detailed_12Month_Plan.md FIRST** (general overview - only once per session)
2. Then create the requested week curriculum
3. **DO NOT commit/push** until user explicitly requests it at end of session
4. Update NEXT_SESSION.md when week is complete

**User will say:** "commit ve push işini seans sonunda söyleyeyim" (I'll tell you about commit/push at end of session)

**TTS guardrail (do not override):** Preserve `addTTSButtonsToExamples()` enhancements in [static/app.js](static/app.js) so listen buttons appear for dialogue, arrow, and quoted French patterns. Avoid reverting this when refactoring UI or lesson rendering.

**Git Method:** Use SSH for all git operations.

---

## 📋 PENDING ISSUES (Session 6 - 2026-02-12)

### 🔴 HIGH PRIORITY - UI/CSS

- [ ] **Modal width not updating in browser** (Cache/CSS conflict issue)
  - **Problem:** ui-enhancements.css override style.css (max-width: 600px vs 1600px)
  - **Status:** CSS files updated but browser still shows old width (600px modal)
  - **Solution needed:**
    - Possible: Combine CSS files or add !important to force override
    - Or: Restart server to force CSS reload for all browsers
    - Or: Add CSS version hash to force cache bust (`style.css?v=2`)
  - **Files affected:**
    - `static/style.css` (updated to 1600px)
    - `static/ui-enhancements.css` (updated to 1600px)
    - `static/app.js` (TTS buttons added to examples)
  - **Testing:** Browser hard refresh (Ctrl+Shift+R) didn't work - need server restart or CSS versioning

---

## 📚 CURRICULUM GENERATION PROGRESS

### Completed

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

✅ **Week 3 (A1.1 - Days 11-15)** - Created (NOT YET COMMITTED)

- Day 11: Gender in French (Masculine/Feminine)
- Day 12: Number (Singular/Plural)
- Day 13: Article Agreement (Gender + Number)
- Day 14: Adjective Placement & Agreement
- Day 15: Week 3 Review & Assessment
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_3_A1.1.md`

✅ **Week 4 (A1.1 - Days 16-20)** - Created (NOT YET COMMITTED)

- Day 16: Question Formation (intonation, est-ce que, inversion)
- Day 17: Complex Negation (ne...plus, jamais, rien, personne)
- Day 18: Imperatives & Commands
- Day 19: Time Expressions & Daily Routines
- Day 20: Month 1 Comprehensive Review & Exam
- **MONTH 1 COMPLETE!** ✅ 100 vocabulary words achieved
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_4_A1.1.md`

✅ **Week 5 (A1.2 - Days 21-25)** - Created (NOT YET COMMITTED) **MONTH 2 BEGINS!**

- Day 21: Passé Composé with Avoir (introduction)
- Day 22: Regular Past Participles (extensive practice)
- Day 23: Irregular Past Participles (avoir, être, faire, prendre, voir, boire)
- Day 24: More Irregular Past Participles (dire, écrire, lire, mettre, pouvoir, vouloir, savoir, devoir)
- Day 25: Week 5 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: 125 words total)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_5_A1.2.md`

✅ **Week 6 (A1.2 - Days 26-30)** - Created (NOT YET COMMITTED)

- Day 26: Passé Composé with ÊTRE (introduction, movement verbs)
- Day 27: Complete DR MRS VANDERTRAMP list (17 verbs)
- Day 28: Agreement rules with ÊTRE (4 forms: -é, -ée, -és, -ées)
- Day 29: Reflexive verbs in Passé Composé (all use ÊTRE)
- Day 30: Week 6 Review & Mixed Practice (AVOIR vs. ÊTRE)
- **NEW:** 25 vocabulary words (cumulative: 150 words total) 🎉
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_6_A1.2.md`

✅ **Week 7 (A1.2 - Days 31-35)** - Created (NOT YET COMMITTED)

- Day 31: Futur Proche (aller + infinitive) - Introduction
- Day 32: Futur Proche practice (plans, intentions, predictions)
- Day 33: Time expressions for future (demain, la semaine prochaine, bientôt, dans X temps)
- Day 34: Futur Proche vs. Present (near future vs. habitual actions)
- Day 35: Week 7 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: 175 words total) 🎉
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_7_A1.2.md`

✅ **Week 8 (A1.2 - Days 36-40)** - Created (NOT YET COMMITTED) **MONTH 2 COMPLETE!** 🎉

- Day 36: Possessive Adjectives (mon, ma, mes, ton, ta, tes, son, sa, ses, notre, votre, leur)
- Day 37: Demonstrative Adjectives (ce, cet, cette, ces) + -ci/-là
- Day 38: Complex Negation Review (ne...plus, ne...jamais, ne...rien, ne...personne)
- Day 39: Month 2 Grammar Review (All A1.2 grammar - PC, Futur Proche, Possessives, Demonstratives, Negation)
- Day 40: Month 2 Comprehensive Exam & Assessment (A1.2 Complete!)
- **NEW:** 25 vocabulary words (cumulative: **200 words total - MONTH 2 COMPLETE!**) 🎉🎊
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_8_A1.2.md`

✅ **Week 9 (A2.1 - Days 41-45)** - Created (NOT YET COMMITTED) **MONTH 3 BEGINS!** 🎉

- Day 41: Imparfait Formation (Regular -ER, -IR, -RE verbs)
- Day 42: Imparfait Irregular Verbs (être, avoir, faire + common irregulars)
- Day 43: Imparfait Usage (Descriptions, habits, ongoing actions)
- Day 44: Imparfait Practice (Weather, age, time, il y avait)
- Day 45: Week 9 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **225 words total**) 🎉
- **CEFR:** A2.1 level begins
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_9_A2.1.md`

✅ **Week 10 (A2.1 - Days 46-50)** - Created (NOT YET COMMITTED)

- Day 46: PC vs. Imparfait (Introduction - When to use each tense)
- Day 47: PC vs. Imparfait (Completed actions vs. ongoing/background)
- Day 48: PC vs. Imparfait (Interruptions - one action interrupts another)
- Day 49: PC vs. Imparfait (Narrative building - telling complete stories)
- Day 50: Week 10 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **250 words total**) 🎉
- **CEFR:** A2.1 (Month 3 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_10_A2.1.md`

✅ **Week 11 (A2.1 - Days 51-55)** - Created (NOT YET COMMITTED)

- Day 51: Comparatives (plus/moins/aussi + adjectives)
- Day 52: Comparatives (plus/moins/autant + nouns + verbs)
- Day 53: Superlatives (le/la/les plus, le/la/les moins)
- Day 54: Equality & Irregular Comparatives (meilleur/pire/mieux)
- Day 55: Week 11 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **275 words total**) 🎉
- **CEFR:** A2.1 (Month 3 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_11_A2.1.md`

✅ **Week 12 (A2.1 - Days 56-60)** - Created (NOT YET COMMITTED)

- Day 56: Relative Pronouns (qui/que) - basics
- Day 57: Relative Pronoun "où" - place/time
- Day 58: Relative Pronouns review + complex sentences
- Day 59: Month 3 Comprehensive Review (Weeks 9-12)
- Day 60: Month 3 Exam & Assessment (A2.1 complete)
- **NEW:** 25 vocabulary words (cumulative: **300 words total**) 🎉
- **CEFR:** A2.1 (Month 3 ends)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_12_A2.1.md`

✅ **Week 13 (A2.2 - Days 61-65)** - Created, committed, and pushed **MONTH 4 BEGINS!** 🎉

- Day 61: Futur simple formation (regular verbs)
- Day 62: Futur simple irregular verbs
- Day 63: Futur simple usage (predictions, plans)
- Day 64: Futur simple practice (time markers, contrast with futur proche)
- Day 65: Week 13 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **325 words total**) 🎉
- **CEFR:** A2.2 (Month 4 begins)
- **Speaking Tier:** 2→3 transition (guided to freer conversation)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_13_A2.2.md`

✅ **Week 14 (A2.2 - Days 66-70)** - Created, committed, and pushed

- Day 66: Conditionnel présent formation
- Day 67: Conditionnel présent usage (polite requests)
- Day 68: Conditionnel présent (hypotheticals)
- Day 69: Si-clauses (present + futur / imparfait + conditionnel)
- Day 70: Week 14 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **350 words total**) 🎉
- **CEFR:** A2.2 (Month 4 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_14_A2.2.md`

✅ **Week 15 (A2.2 - Days 71-75)** - Created, committed, and pushed

- Day 71: Pronoun Y (Location - à + place)
- Day 72: Pronoun EN (Quantity - de + noun)
- Day 73: Pronoun Y vs EN practice
- Day 74: Advanced Pronoun Placement
- Day 75: Week 15 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **375 words total**) 🎉
- **CEFR:** A2.2 (Month 4 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_15_A2.2.md`

✅ **Week 16 (A2.2 - Days 76-80)** - Created, committed, and pushed **MONTH 4 COMPLETE!** 🎉

- Day 76: Reflexive Verbs (Review & Expansion)
- Day 77: Indirect Speech (Introduction - il dit que...)
- Day 78: Indirect Speech (Questions & Commands)
- Day 79: Month 4 Comprehensive Review
- Day 80: Month 4 Exam & Assessment (A2.2 Complete!)
- **NEW:** 25 vocabulary words (cumulative: **400 words total**) 🎉
- **CEFR:** A2.2 (Month 4 ends)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_16_A2.2.md`

✅ **Week 17 (B1.1 - Days 81-85)** - Created, committed, and pushed **MONTH 5 BEGINS!** 🎉

- Day 81: Passé Simple (Receptive - Reading focus)
- Day 82: Passé Simple (Irregular verbs - Reading focus)
- Day 83: Plus-que-parfait (Formation - had done)
- Day 84: Plus-que-parfait (Usage & Concordance)
- Day 85: Week 17 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **425 words total**) 🎉
- **CEFR:** B1.1 (Month 5 begins)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_17_B1.1.md`

✅ **Week 18 (B1.1 - Days 86-90)** - Created, committed, and pushed

- Day 86: Subjonctif Introduction (Concept & Formation)
- Day 87: Subjonctif Irregulars (Faire, Aller, Être, Avoir)
- Day 88: Subjonctif Usage 1 (Will & Necessity)
- Day 89: Subjonctif Usage 2 (Emotion & Doubt)
- Day 90: Week 18 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **450 words total**) 🎉
- **CEFR:** B1.1 (Month 5 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_18_B1.1.md`

✅ **Week 19 (B1.1 - Days 91-95)** - Created, committed, and pushed

- Day 91: Pronoms Relatifs Composés (Lequel, Duquel, Auquel)
- Day 92: Pronoms Démonstratifs (Celui, Celle, Ceux, Celles)
- Day 93: Pronoms Démonstratifs Composés (Celui-ci/Celui-là)
- Day 94: La Mise en Relief (C'est...qui, C'est...que)
- Day 95: Week 19 Review & Assessment
- **NEW:** 25 vocabulary words (cumulative: **475 words total**) 🎉
- **CEFR:** B1.1 (Month 5 continues)
- Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_19_B1.1.md`

### Next Task

🎯 **CREATE WEEK 20 CURRICULUM (B1.1 - Advanced Indirect Speech & Month 5 Exam)**

**User command:** "Week 20" or "Next week"

1. **FIRST:** Read `Research/Phase_2_Detailed_12Month_Plan.md`
2. Create Week 20 (B1.1 - Days 96-100) curriculum file
3. Grammar topics:
   - Day 96: Discours Rapporté au Passé (Concordance des temps - Présent -> Imparfait)
   - Day 97: Discours Rapporté au Passé (PC -> PQP, Futur -> Cond)
   - Day 98: Discours Rapporté (Time markers changes: Demain -> Le lendemain)
   - Day 99: Month 5 Comprehensive Review
   - Day 100: Month 5 Exam & Assessment (B1.1 Complete!)
4. Update NEXT_SESSION.md

---

## 🗓️ 52-WEEK CURRICULUM PLAN

**Structure:**

- 52 weeks total (1 year)
- Each week = 5 days of lessons
- Each week file = detailed format (like Phase_1_Example_Week_15.md)
- Vocabulary: 5 words/day
- Speaking Tier progression: 1 → 2 → 3

**Month 1 (Weeks 1-4) - A1.1:** ✅ COMPLETE

- ✅ Week 1: être, avoir, -ER verbs, articles
- ✅ Week 2: -IR/-RE verbs, negation, questions, numbers
- ✅ Week 3: Adjectives, agreement, possessives, colors
- ✅ Week 4: Review + Month 1 exam
- **Vocabulary:** 100 words

**Month 2 (Weeks 5-8) - A1.2:** ✅ COMPLETE

- ✅ Week 5: Passé composé (avoir)
- ✅ Week 6: Passé composé (être)
- ✅ Week 7: Futur proche
- ✅ Week 8: Possessives, Demonstratives, Complex Negation + Month 2 exam
- **Vocabulary:** 100 words (Total: 200)

**Month 3 (Weeks 9-12) - A2.1:** ✅ COMPLETE

- ✅ Week 9: Imparfait (introduction, irregular verbs, usage)
- ✅ Week 10: Passé Composé vs. Imparfait
- ✅ Week 11: Comparatives & Superlatives
- ✅ Week 12: Relative Pronouns + Month 3 Exam
- **Vocabulary:** 100 words (Total: 300) ✅

**Month 4 (Weeks 13-16) - A2.2:** ✅ COMPLETE

- ✅ Week 13: Futur simple (formation, irregular verbs, usage, vs. futur proche)
- ✅ Week 14: Conditionnel présent (formation, polite requests, hypotheticals, si-clauses)
- ✅ Week 15: Pronouns Y & EN (location & quantity replacement)
- ✅ Week 16: Reflexive verbs, indirect speech + Month 4 Exam
- **Vocabulary:** 100 words (Total: 400) **MONTH 4 COMPLETE!** 🎉

**Month 5 (Weeks 17-20) - B1.1:** 🔄 IN PROGRESS

- ✅ Week 17: Passé Simple (Receptive) & Plus-que-parfait
- ✅ Week 18: Subjonctif (Introduction & Usage)
- ✅ Week 19: Relative Pronouns (Advanced) & Demonstratives
- [ ] Week 20: Indirect Speech (Advanced) + Month 5 Exam
- **Vocabulary:** 100 words (Total: 500)

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

### For Future Weeks

- Continue Babbel/Busuu structured approach
- Emphasize dialogue-first scenarios
- Include more cultural context specific to each grammar topic
- Use visual tables and color-coding where helpful
- Avoid gamification language (no "earn XP" or "level up")

---

## ⚠️ CRITICAL: Package Dependencies

- ✅ **Closed:** Google Generative AI migration complete. Now using `google-genai` only (old SDK removed).

---

## 🎯 Program Implementation Tasks (Updated 2026-02-12)

### **Phase 2B: NEW CURRICULUM SYSTEM Integration** (Current Sprint) 🔴

#### CRITICAL - Curriculum System Refactor

1. **NEW_CURRICULUM_REDESIGNED Integration** (quiz_parser.py + curriculum_loader.py)
   - [ ] Update curriculum_loader.py to parse NEW_CURRICULUM_REDESIGNED/Week_X_A1.X.md format
   - [ ] Parse DAY sections with metadata (CEFR, Grammar Topic, Content Identifiers, Speaking Tier)
   - [ ] Extract 5-paragraph grammar explanations (pre-written, no AI generation needed)
   - [ ] Parse 5 vocabulary words/day with example sentences
   - [ ] Parse 50 example sentences per day (10 shown randomly in quiz)
   - [ ] Extract content_identifiers from each example: [listening, dialogue, conjugation, fill_blank] etc.
   - [ ] Function: `parse_day_curriculum(week, day) → DayLessonData`
   - Function: `parse_quiz_examples(week, day) → List[ExampleQuestion]` (50 total, select 8-10 randomly)

#### HIGH PRIORITY - Core Functionality

1. **Quiz Question Parser** (quiz_parser.py)
   - [ ] Parse 50 pre-written quiz questions per day from curriculum markdown files
   - [ ] Extract question metadata: type, answer key, content_identifier
   - [ ] Validate all questions have required fields
   - [ ] Function: `parse_quiz_questions(week, day) → List[QuizQuestion]`

2. **Quiz Display Logic** (Frontend + Backend)
   - [ ] Select 8 questions from 50-question fixed bank per day
   - [ ] Ensure content_identifier variety (mix of exercise types)
   - [ ] Track shown_questions in lesson_progress table
   - [ ] Randomize order of selected questions
   - [ ] Display questions with immediate feedback

3. **Database Schema Updates**
   - [ ] ALTER TABLE lessons ADD COLUMN content_identifiers TEXT (JSON array)
   - [ ] ALTER TABLE lessons ADD COLUMN speaking_tier INTEGER DEFAULT 1
   - [ ] ALTER TABLE lesson_progress ADD COLUMN shown_questions TEXT (JSON array)
   - [ ] Create migration script for existing data

4. **AI Evaluation Prompts** (Speaking/Homework/Exam)
   - [ ] Speaking Tier 1: Script adherence + basic pronunciation scoring
   - [ ] Speaking Tier 2: Grammar accuracy + scenario completion scoring
   - [ ] Speaking Tier 3: Fluency + complexity + naturalness scoring
   - [ ] Test evaluation prompts with sample transcriptions
   - [ ] Validate response format (JSON with scores + feedback)

#### MEDIUM PRIORITY - Quality & Performance

1. **Fix Gemini JSON Parsing Issues** (~60% fallback rate)
   - [ ] Log raw Gemini responses to identify malformed fields
   - [ ] Simplify vocabulary section (top 10 words instead of all 21)
   - [ ] Implement JSON repair logic for common formatting errors
   - [ ] Add structured prompting hints for valid JSON escaping
   - Goal: Reduce fallback rate to <10%

2. **Prompt Optimization**
   - [ ] Reduce token usage (simplify curriculum formatting in prompts)
   - [ ] Add JSON schema validation before passing to users
   - [ ] Test prompt variations with different token budgets
   - [ ] Profile which sections are most token-hungry

#### LOW PRIORITY - Documentation

1. **Testing & Validation**
   - [ ] Document grammar explanation quality expectations
   - [ ] Test generated lessons across all 52 weeks for consistency
   - [ ] Create test suite for fallback lesson generation
   - [ ] Curriculum file validation (all 52 files consistent structure)

---

### **Phase 2C: Homework & Monthly Exam System** (Next Sprint - Weeks 10-12) 🟡

1. **Homework Blocking System**
   - [ ] Implement homework submission requirement (text + audio)
   - [ ] Block next lesson until homework submitted
   - [ ] AI grading with text/audio evaluation
   - [ ] Pass criteria: text_score ≥70% AND audio_score ≥60%
   - [ ] Re-submission workflow for failed homework

2. **Monthly Comprehensive Exams** (Days 20, 40, 60, 80, etc.)
   - [ ] Parse monthly exam content from curriculum files
   - [ ] 4 sections: Listening (25pts), Reading (25pts), Writing (25pts), Speaking (25pts)
   - [ ] AI evaluation for writing + speaking sections
   - [ ] Pass threshold: 50/100 points
   - [ ] Generate weakness report from exam results

3. **Weakness Tracking Refinement**
   - [ ] Track errors by content_identifier type
   - [ ] Generate monthly report (top 5 weak topics with accuracy %)
   - [ ] Prioritize weak content types in review sessions
   - [ ] Content-identifier-aware SRS scheduling

---

### **Backlog: Future Enhancements** (Post Phase 2) 🟢

#### Interactive Lesson Features

- [ ] "More Explanation" and "More Examples" buttons in grammar section
  - Generate ADDITIONAL explanation on demand (supplements fixed content)
  - Create `POST /api/lessons/{lesson_id}/expand-grammar` endpoint
  
- [ ] Grammar Reference Tab
  - Fixed, curated content per topic (tenses, pronouns, negation)
  - Searchable by CEFR level and content type
  - Reliable fallback when AI output insufficient

#### Quiz & Speaking Improvements

- [ ] Quiz question bank pooling (avoid immediate repeats)
  - Store quiz questions separately in DB
  - Track question usage per user
  - Reuse best questions across attempts

- [ ] Speaking scenario history (avoid AI repetition)
  - Cache last 5 speaking scenarios per user/week
  - Pass to AI prompt: "Do NOT use these opening lines: {history}"
  - Ensure fresh conversation starters

#### Technical Debt

- [x] **COMPLETED & VERIFIED (Session 6 - 2026-02-12)**: Migrated from deprecated `google.generativeai` to `google-genai`
  - ✅ All files updated (lesson_generator.py, main.py, api_helpers.py)
  - ✅ Old SDK removed from requirements.txt
  - ✅ Tested and confirmed working
  - See: <https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md>
  
- [ ] Database version control strategy
  - Decide: .gitignore, schema-only commits, or migrations (alembic)
  - Add DB backup script

- [ ] Performance optimization
  - Cache curriculum files in memory
  - Batch processing for AI evaluation requests
  - Database indexing for content_identifier queries

## ⚠️ Known Issues & Status (Updated 2026-02-12)

### ✅ RESOLVEDSee: <https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md> (Session 4 - 2026-02-09)

1. **Quiz scoring shows 0/5 even when answers are correct**
   - Fixed via multi-part normalization, answer extraction, fuzzy matching

2. **Speaking practice not embedded in lesson modal**
   - Fixed: Now hides modal instead of destroying, preserves lesson scenario

3. **Audio-based quiz questions missing (no Listen button)**
   - Fixed: Added `audio_text` field with TTS support for listening questions

4. **Grammar explanations showing "Tableau..." instead of detailed content**
   - Fixed: Added API key config to lesson_generator.py
   - Fixed: Structured 5-paragraph explanations (both AI and fallback)

5. **Fill-in-the-blank questions impossible to answer**
   - Fixed: Validates base verb included in parentheses format

### 🔄 ACTIVE ISSUES

1. **Gemini returning invalid/malformed JSON (~60% fallback rate)**
   - Root cause: Prompt exceeds effective context window
   - Workaround: Improved fallback provides quality explanations
   - Solution: See Phase 2B Item #5 (Simplify vocab section + JSON repair)

2. **Quiz question parsing not yet implemented**
   - Status: Planned for Phase 2B
   - Current: No quiz questions loaded from curriculum files
   - Target: Parse 50 questions/day from markdown files

3. **Content identifier distribution not tracked**
   - Status: Database schema update pending (Phase 2B)
   - Impact: Cannot analyze exercise type variety or effectiveness

4. **Speaking tier evaluation prompts need refinement**
   - Status: Planned for Phase 2B
   - Current: AI evaluation exists but not tier-specific
   - Target: 3 distinct scoring rubrics (Tier 1/2/3)

---

## 📊 Current Development Phase: Phase 2A → 2B Transition

### ✅ Phase 2A: Fixed Curriculum Loading (COMPLETE)

- curriculum_loader.py operational
- Week/day selector UI functional
- Month 1 (Weeks 1-4) curriculum files complete
- Grammar/vocabulary/examples display working

### 🔄 Phase 2B: Quiz Display & AI Evaluation (IN PROGRESS - Weeks 7-9)

- See "Program Implementation Tasks" section above for detailed sprint plan
- Current focus: Quiz parser, content identifiers, AI evaluation prompts

### 🕒 Phase 2C: Homework & Monthly Exams (UPCOMING - Weeks 10-12)

- Homework blocking system
- DELF-aligned monthly comprehensive exams
- Weakness tracking by content type

---

## 🔗 Reference Documents

- **Implementation_Plan.md** - Global 36-week project roadmap
- **French_Tutor_SRS.md** - Software requirements specification

---

## 📝 Session Notes

### Session 5 (2026-02-12) - Part 1

**Date:** 2026-02-12  
**Focus:** Review Implementation Plan and SRS, consolidate program to-do list  
**Completed:**

- Read full Implementation_Plan.md (550 lines) - Phase 2A complete, Phase 2B in progress
- Read French_Tutor_SRS.md (Software Requirements Specification) - Fixed curriculum + AI evaluation approach
- Updated NEXT_SESSION.md with consolidated, prioritized program tasks
- Organized tasks by Phase 2B (current sprint), Phase 2C (next sprint), and Backlog (future)
- Clarified current development phase: Phase 2A → 2B transition

**Key Findings:**

- Phase 2B critical path: Quiz parser, content identifiers, AI evaluation prompts, DB schema updates
- Phase 2C upcoming: Homework blocking, monthly exams (DELF-aligned), weakness tracking
- Active issue: Gemini JSON parsing ~60% fallback rate (needs simplification + JSON repair)
- Architecture clarity: Fixed curriculum files (no AI content generation) + AI evaluation only

### Session 5 (2026-02-12) - Part 2: NEW CURRICULUM SYSTEM Implementation ✅

**Date:** 2026-02-12  
**Focus:** Implement new curriculum system using Research/NEW_CURRICULUM_REDESIGNED/ format

**Completed:**

- ✅ **curriculum_loader.py** - Added functions for redesigned curriculum:
  - `load_redesigned_curriculum_day(week, day)` - Parse NEW_CURRICULUM_REDESIGNED format
  - `_parse_day_metadata()` - Extract CEFR level, grammar topic, content identifiers, speaking tier
  - `_parse_day_grammar_explanation()` - Extract 5-paragraph grammar (FIXED content)
  - `_parse_day_vocabulary()` - Extract 5 words with examples
  - `_parse_day_examples()` - Extract 50 quiz questions with content identifiers
  
- ✅ **quiz_parser.py** - NEW FILE created:
  - `get_quiz_questions(week, day, count=8)` - Randomly select 8-10 from 50 available
  - `_select_diverse_questions()` - Ensure variety of content identifier types
  - `_determine_primary_type()` - Classify question by main content identifier
  - `format_question_for_display()` - Add UI-specific fields (audio, answer_type)
  - `get_content_identifier_stats()` - Analytics for question type distribution

- ✅ **lesson_generator.py** - New function added:
  - `generate_lesson_from_redesigned_curriculum()` - Load FIXED curriculum (no AI generation)
  - `_format_grammar_as_html()` - Convert markdown to HTML (tables, lists, bold)
  - Uses pre-written grammar explanations (5-paragraph format)
  - Grammar already exists in curriculum → No token usage!

- ✅ **main.py** - New API endpoint:
  - `/api/lessons/load` - NEW SYSTEM endpoint (uses redesigned curriculum)
  - `/api/lessons/generate` - Marked as DEPRECATED (old system)
  - Error handling for missing curriculum files (Week 8+ not yet created)

- ✅ **static/app.js** - Frontend updated:
  - Changed endpoint from `/api/lessons/generate` → `/api/lessons/load`
  - `displayGeneratedLesson()` - Supports both OLD and NEW formats
  - Detects new format by checking `grammar_explanation` field
  - Shows content identifiers in quiz questions
  - Displays vocabulary with example sentences

- ✅ **TEST_NEW_CURRICULUM.md** - Created comprehensive test guide

**System Architecture (NEW):**

```
User clicks "Load Lesson"
    ↓
Frontend calls /api/lessons/load (week=1, day=1)
    ↓
Backend: lesson_generator.generate_lesson_from_redesigned_curriculum()
    ↓
curriculum_loader.load_redesigned_curriculum_day() → Parse Week_1_A1.1.md
    ├─ Grammar (5-paragraph) ✅ FIXED content
    ├─ Vocabulary (5 words) ✅ With example sentences
    └─ Examples (50 questions) ✅ Content identifiers
    ↓
quiz_parser.get_quiz_questions() → Select 8 random from 50
    ↓
Return lesson JSON to frontend
    ↓
Display: Grammar + Vocab + Quiz (with content identifier badges)
```

**Key Benefits:**

1. **No AI for content** → Grammar explanations are FIXED (pre-written)
2. **Content identifiers** → Every question tagged: [listening], [conjugation], etc.
3. **Diversity guaranteed** → 50 questions/day, show 8-10 randomly selected
4. **No token usage** → No API calls for lesson content
5. **Reliable quality** → Hand-written grammar explanations (5-paragraph format)

**Testing Status:**

- Ready to test: Weeks 1-7 (35 lessons available)
- Each day: Grammar + 5 vocab + 50 quiz questions
- Content identifiers working
- See TEST_NEW_CURRICULUM.md for detailed test instructions

**Next steps:**

- Test the program (uvicorn main:app --reload)
- Verify content identifiers display in UI
- Continue Week 8-52 curriculum creation
- Add content identifier badges to quiz UI
- Implement database schema for content_weaknesses tracking

### Session 6 (2026-02-12) - Part 1: Week 13 Curriculum Generation

**Date:** 2026-02-12  
**Focus:** Generate Week 13 curriculum (A2.2 - Futur Simple)

### Session 6 (2026-02-12) - Part 2: SDK Migration (google-generativeai → google-genai) ✅ COMPLETE

**Date:** 2026-02-12  
**Focus:** Migrate from deprecated `google-generativeai` to official `google-genai` SDK

**Completed:**

- ✅ **requirements.txt** - Migrated to google-genai only (old SDK removed after testing)
- ✅ **lesson_generator.py** - Full migration:
  - Changed `import google.generativeai as genai` → `from google import genai` + `from google.genai import types`
  - Replaced `genai.configure()` with `genai.Client()` pattern
  - Updated `genai.GenerativeModel()` → `client.models.generate_content()`
  - Created `_get_genai_client()` function for client management
- ✅ **main.py** - Full migration:
  - Updated import statement
  - Migrated 7 API call sites to new client-based API
  - All functions now use `client.models.generate_content(model='gemini-2.5-flash', contents=...)`
- ✅ **api_helpers.py** - Full migration:
  - Renamed `get_gemini_model()` → `get_gemini_client()`
  - Updated global `genai` → `genai_client`
  - Changed `call_gemini_json()` to use client pattern
- ✅ **NEXT_SESSION.md** - Updated documentation
- ✅ **Testing** - User confirmed all AI features working correctly
- ✅ **Cleanup** - Old SDK removed from requirements.txt

**Migration Result:**

- Migration successful, all features tested and working
- Old SDK completely removed after verification
- Application now using official googleapis SDK exclusively

**Key API Changes Implemented:**

```python
# OLD SDK (deprecated) - REMOVED
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(prompt)

# NEW SDK (official) - NOW IN USE
from google import genai
from google.genai import types
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=4000)
)
```
