**Updated To-Do List (52 Weeks Content + 12 Month Access Period)**

1. [completed] **Phase 1: A1-A2 Foundation (Weeks 1-20, approximately 5 months)**
   - [completed] Block 1 (Weeks 1-4): A1.1 Foundation  
     → Weeks 1-4 created and updated in English (grok_Week_01_A1.1.md → grok_Week_04_A1.1.md)
  - [completed] Block 2 (Weeks 5-8): A1.2 Building Blocks
  - [completed] Block 3 (Weeks 9-12): A2.1 Consolidation
  - [completed] Block 4 (Weeks 13-16): A2.2 Transition to Tier 2
  - [completed] Block 4.5 / Review & Reinforcement (Weeks 17-20): A2 general review, vocabulary + grammar drills in different contexts, simple dialogue variations

2. [completed] **Phase 2: B1 Intermediate (Weeks 21-36, approximately 4 months)**
  - [completed] Block 5 (Weeks 21-24): B1.1 Semi-Guided Practice
  - [completed] Block 6 (Weeks 25-28): B1.2 Complex Scenarios
  - [completed] Block 6.5 / Deep Practice & Variation (Weeks 29-32): Subjunctive, passive, indirect speech and related topics in different contexts with increased production (writing/speaking)
  - [completed] Block 7 / B1 Consolidation (Weeks 33-36): B1 general synthesis, different text types, conversation scenarios, weak-area focused drills

3. [completed] **Phase 3: B2 Advanced (Weeks 37-52, approximately 4 months)**
  - [completed] Block 8 (Weeks 37-40): B2.1 Transition to Tier 3
    - [completed] Old Week 25 → New Weeks 37-38 (Advanced Subjunctive + Stylistic Choices + variation week)
    - [completed] Old Week 26 → New Weeks 39-40 (Participle Clauses + application week)
    - [completed] Old Week 27 → New Week 41 (Argumentation Structure)
    - [completed] Old Week 28 → New Week 42 (Register and Style Variation)
  - [completed] Block 9 (Weeks 43-46): B2.2 Literature, Connectors, Mediation
    - [completed] Old Week 29 → New Week 43 (Literature Analysis)
    - [completed] Old Week 30 → New Week 44 (Advanced Connectors & Discourse)
    - [completed] Old Week 31 → New Week 45 (Current Events & Mediation)
    - [completed] Old Week 32 → New Week 46 (Presentation Skills)
  - [completed] Block 10 / B2.2 Final (Weeks 47-52): Debate, Exam Prep, Capstone
    - [completed] Old Week 33 → New Week 47 (Structured Debate)
    - [completed] Old Week 34 → New Week 48 (Exam Simulation & Strategy)
    - [completed] Old Week 35 → New Week 49 (Advanced Reading & Literature Focus)
    - [completed] Old Week 36 → New Weeks 50-51 (CAPSTONE PROJECT + Final Assessment)
    - [completed] Week 52: Final Review & DELF B2 Simulation (personalized based on weak areas)

4. [completed] **General Tasks**
  - [completed] Validate all 52 weeks for CEFR compliance and consistency
  - [completed] Strengthen weekly exam rubrics and remedial variation prompt templates
  - [completed] Clarify the rule for AI's dynamic content generation: "same topic with different perspective / context / example" (example: subjunctive for emotions → doubt → necessity → regret weeks)
  - [completed] Clean up / archive old BLOCK_X.md and Week_XX.md files (replace with new versions with grok_ prefix)

5. [completed] **AI Prompt & Dynamic Lesson Enhancement (2026-02-08)**
  - [completed] Rewrite SYSTEM_PROMPT with 5-paragraph grammar mandate & dynamic variation rules
  - [completed] Rewrite LESSON_GENERATION_PROMPT with structured grammar format (400+ words, 20+ sentences)
  - [completed] Add attempt_number tracking to lesson generation (via DB count)
  - [completed] Add variation_seed for deterministic randomization of contexts/adjectives/scenarios
  - [completed] Create variation instruction templates (attempt 1 → 2 → 3 → 4+)
  - [completed] Add 6 context pools, 6 adjective pools, 12 scenario pools for variety
  - [completed] Implement temperature escalation per attempt (0.8 → 0.95 → 1.1 → 1.25)
  - [completed] Fix Gemini model to gemini-2.5-flash in lesson_generator.py
  - [completed] Increase max_tokens from 2000 to 4096 for richer grammar content
  - [completed] Add get_lesson_generation_count() to db.py
  - [completed] Update prompt_builders.py to pass attempt_number and variation_seed
  - [completed] Include curriculum scaffolding steps in prompt context
  - [completed] Include ALL vocabulary words with "MUST INCLUDE" emphasis
  - [completed] Update Implementation_Plan.md and French_Tutor_SRS.md

6. [not-started] **Remaining Interactive Lesson Improvements**
  - [ ] Store generated lesson JSON in DB for cross-attempt comparison
  - [ ] "More Explanation" and "More Examples" interactive buttons in grammar section
  - [ ] Grammar reference tab with curated fixed content per topic
  - [ ] Quiz question bank pooling from previous generations
  - [ ] Speaking scenario history to avoid AI repeating the same opening
  - [ ] Decide how to handle local french_tutor.db changes (commit, discard, or add to .gitignore)