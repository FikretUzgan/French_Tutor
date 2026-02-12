# PHASE 2: Detailed 12-Month Curriculum Plan (Monthly Based)

## OVERVIEW

**Structure:** 12 months × 20 days/month = 240 days (+ 125 review/assessment days = 365 total)  
**Vocabulary:** 5 words/day × 20 days = 100 words/month × 12 months = **1,200 total A1-B2 words**  
**Format:** Month-based (not week-based) for comprehensive monthly coverage  
**Progression:** A1.1 → A1.2 → A2.1 → A2.2 → B1.1 → B1.2 → B2.1 → B2.2 (8 CEFR levels)  

---

## VOCABULARY SYSTEM CHANGES (From User Feedback)

### New Requirements:
1. ✅ **Context Example:** Every vocabulary word shown in example sentence
   - Format: `Le café` → "Je vais **au café** à 9h." (I go to the café at 9 AM)
2. ✅ **5 words/day** (not 10) → 100 words/month
3. ✅ **Learned words database:** `learned_vocabulary` table tracks all mastered words
4. ✅ **Vocabulary Practice (App):**
   - Interactive: FR→EN + EN→FR
   - STT/TTS: Both active (listen & speak)
   - **For verbs:** Use random learned conjugations from that point
     - Example Day 21 (Passé Composé introduced): Future conjugation questions use present OR passé composé
     - Example Day 61 (Futur Simple introduced): Questions can mix présent + PC + futur proche
5. ✅ **Spaced repetition:** Learned words reappear in future days/months with new contexts

---

## PROGRAM REQUIREMENTS (From User Feedback)

### Database Changes:
- [ ] Create `learned_vocabulary` table
  - Fields: word_id, french_word, english_translation, cefr_level, day_introduced, word_type (noun/verb/adj/adv), example_sentence
- [ ] Extend existing vocabulary practice to pull from `learned_vocabulary`
- [ ] Track conjugation forms per verb (tenses learned to date)

### Vocabulary Practice Feature Updates:
- [ ] Bidirectional display (FR↔EN option toggling)
- [ ] STT: Student listens to native speaker pronunciation
- [ ] TTS: Student records & gets feedback
- [ ] **Verb conjugation mode (NEW):** If word is verb, randomly select 1 learned tense → ask conjugation for random pronoun
  - Only use tenses introduced by that day
  - Show which tense in brackets: "(Présent)" or "(Passé Composé)" etc.
- [ ] Multiple choice display (4 options)
- [ ] Visual recognition mode (match word to image)

### Application Integration:
- [ ] `vocabulary_loader.py`: Load 5 words/day from curriculum (not 10)
- [ ] `db_vocabulary.py`: Add `learned_vocabulary` table + functions
- [ ] `api_helpers.py`: New endpoint `/api/vocabulary/conjugate` for verb conjugation mode
- [ ] Progress tracking: Visual bar shows % of month complete (20 days/month)

---

## MONTH-BY-MONTH BREAKDOWN (High-Level)

### MONTH 1: A1.1 - Foundation (Days 1-20)
**Grammar Topics (One per day, 4 days/week + 1 review day):**
- Week 1: être, avoir, -ER verbs, articles
- Week 2: -IR/-RE verbs, gender/number, noun agreement
- Week 3: Basic adjectives, adjective placement, questions
- Week 4: Negation, imperatives, time expressions

**Vocabulary Domain:** Greetings, numbers, colors, basic descriptions, family, daily objects  
**Speaking Tier:** 1 (script-based, repetition)  
**Assessment:** Daily quiz (5-8Q) + Weekly quiz (20-30Q) + Month-end exam (mock DELF A1)  
**Vocabulary Count:** 100 words (5/day × 20 days)

---

### MONTH 2: A1.2 - Past & Near Future (Days 21-40)
**Grammar Topics:**
- Week 1: Passé composé (avoir), past participles, irregular forms
- Week 2: Passé composé (être), agreement rules, negation in PC
- Week 3: Futur proche (aller + infinitive), imperatives, polite requests
- Week 4: Possessive adjectives, complex negation, time expressions with past/future

**Vocabulary Domain:** Food, restaurants, family professions, past events, travel  
**Speaking Tier:** 1→2 (transition from script to guided)  
**Assessment:** Daily + Weekly + Month-end exam (A1.2 full skills)  
**Vocabulary Count:** 100 words  

---

### MONTH 3: A2.1 - Imperfect & Comparisons (Days 41-60)
**Grammar Topics:**
- Week 1: Imparfait (all regular verbs), common irregulars (être, avoir, faire)
- Week 2: Passé composé vs. Imparfait (contrast), narrative building
- Week 3: Comparatives, superlatives, equality expressions
- Week 4: Relative pronouns (qui, que, où), complex sentences

**Vocabulary Domain:** Travel, shopping, locations, preferences, comparisons  
**Authentic Content Start:** Week 1 (RFI/TV5 materials introduced)  
**Speaking Tier:** 2 (guided with constraints)  
**Assessment:** Daily + Weekly + Month-end exam (A2.1 full skills)  
**Vocabulary Count:** 100 words  

---

### MONTH 4: A2.2 - Conditionals & Complex Pronouns (Days 61-80)
**Grammar Topics:**
- Week 1: Futur simple (regular + irregular), predictions vs. immediate future
- Week 2: Conditionnel présent, polite requests, hypotheticals, si-clauses
- Week 3: Pronouns Y & EN (location & quantity replacement)
- Week 4: Reflexive verbs, indirect speech intro, complex pronouns

**Vocabulary Domain:** Restaurant scenarios, shopping situations, daily routines, wishes/hypotheticals  
**Speaking Tier:** 2 (guided, more complex scenarios)  
**Assessment:** Daily + Weekly + **MONTH-END COMPREHENSIVE EXAM (A2.2 full DELF mock)**  
**Vocabulary Count:** 100 words  

---

### MONTH 5: B1.1 - Subjunctive Introduction & Perfect Tenses (Days 81-100)
**Grammar Topics:**
- Week 1: Passé simple (reading comprehension intro), present perfect (avoir+been doing)
- Week 2: Subjonctif présent (formation + common uses: il faut que, vouloir que, croire que)
- Week 3: Complex relative pronouns (dont, lequel, duquel), demonstrative pronouns (celui, celle)
- Week 4: Advanced indirect speech, reported vs. direct speech

**Vocabulary Domain:** Opinions, emotions, necessities, abstract concepts, literature/reading  
**Speaking Tier:** 2→3 (transition to freer conversation)  
**Assessment:** Daily + Weekly + Month-end exam (B1.1 skills)  
**Vocabulary Count:** 100 words  

---

### MONTH 6: B1.2 - Passive Voice & Complex Structures (Days 101-120)
**Grammar Topics:**
- Week 1: Passive voice (présent, passé composé, futur simple)
- Week 2: Participle phrases, gerunds (en + participe), absolute clauses
- Week 3: Advanced si-clauses, conditionals with past tenses
- Week 4: Literary devices, complex conjunctions (bien que, pourvu que, à moins que)

**Vocabulary Domain:** Academic topics, media vocabulary, advanced narratives, social issues  
**Speaking Tier:** 3 (free conversation, minimal scaffolding)  
**Assessment:** Daily + Weekly + Month-end exam (B1.2 skills)  
**Vocabulary Count:** 100 words  

---

### MONTH 7: B2.1 - Stylistic Variation & Nuance (Days 121-140)
**Grammar Topics:**
- Week 1: Conditionnel passé (past hypothetical), mixed conditionals
- Week 2: Subjunctive beyond basic uses, subjunctive after expressions of doubt
- Week 3: Register shifts (formal/informal), stylistic pronouns (on vs. nous)
- Week 4: Advanced discourse markers, argumentative structures

**Vocabulary Domain:** Professional vocabulary, nuanced expressions, persuasive language, cultural references  
**Authentic Content:** 70% authentic (news, essays, videos)  
**Speaking Tier:** 3 (debate, argumentation)  
**Assessment:** Daily + Weekly + Month-end exam (B2.1 skills)  
**Vocabulary Count:** 100 words  

---

### MONTH 8: B2.2 - Advanced Fluency & Specialization (Days 141-160)
**Grammar Topics:**
- Week 1: Coordination & subordination mastery, complex sentence structure
- Week 2: Metaphor, metonymy, stylistic devices in French literature
- Week 3: Register variation in professional contexts, specialized vocabulary fields
- Week 4: Dialect awareness (Québecois, Belgian French, African French variations)

**Vocabulary Domain:** Specialized fields (business, literature, culture, science), regional vocabulary  
**Authentic Content:** 90% authentic (literature excerpts, interviews, podcasts)  
**Speaking Tier:** 3+ (native-like fluency attempts)  
**Assessment:** Daily + Weekly + Month-end exam (B2.2 skills + DALF mock)  
**Vocabulary Count:** 100 words  

---

### MONTHS 9-12: Advanced Consolidation & Specialization (Days 161-240)
**Pattern:** User selects 1 specialization path:
- **Path A:** Business French (commerce, negotiation, professional communication)
- **Path B:** Literary French (classic literature, poetry analysis)
- **Path C:** Cultural French (cinema, history, philosophy, social studies)
- **Path D:** Conversational Mastery (dialectology, regional speech, authentic narratives)

Each path deepens grammar already learned, focusing on specialization vocabulary (100 words/month per path).

---

## DAILY LESSON STRUCTURE (Revised Format)

### FORMAT (Same as Week 15, with vocabulary updates):

**Day Structure (30 mins total):**
1. **GRAMMAR (10 min):** New topic or reinforcement
2. **VOCABULARY (5 min):** 5 words with example sentences
3. **EXAMPLES (Curriculum):** 50 pre-written sentences (10 shown as samples)
4. **SPEAKING (10 min):** Tier-based scenario
5. **QUIZ (5 min):** 5-8 random questions from 50-question bank

---

### VOCABULARY SECTION (REVISED - New Format)

**5 vocabulary words per day, structured with examples:**

```markdown
## Vocabulary (Day X)

**Word 1: Le café (The café)**
- Type: Noun (masculine)
- English: The café / Coffee shop
- CEFR Level: A1.1
- Pronunciation: luh kah-fay
- **Example sentence:** "Je vais **au café** à 9h le matin." (I go to the café at 9 AM)
- Context: Social/Locations
- Part of learned_vocabulary: ✅ (added Day 1)

**Word 2: Aller (To go)**
- Type: Verb (irregular -ER)
- English: To go
- CEFR Level: A1.1
- Pronunciation: ah-lay
- **Example sentence:** "Je **vais** à l'école chaque jour." (I **go** to school every day.)
- Context: Daily actions
- Conjugation forms (as of this day):
  - Présent: je vais, tu vas, il/elle va, nous allons, vous allez, ils/elles vont
- Part of learned_vocabulary: ✅ (added Day 1)

**Word 3: Bonjour (Hello/Good day)**
- Type: Interjection
- English: Hello / Good day
- CEFR Level: A1.1
- Pronunciation: bon-zhoor
- **Example sentence:** "**Bonjour**! Ça va?" (**Hello**! How are you?)
- Context: Greetings
- Part of learned_vocabulary: ✅ (added Day 1)

**Word 4: Français (French)**
- Type: Adjective / Nationality
- English: French
- CEFR Level: A1.1
- Pronunciation: frahn-say
- **Example sentence:** "Je suis **français**." (I am **French**.)
- Context: Nationality/Identity
- Part of learned_vocabulary: ✅ (added Day 1)

**Word 5: Eau (Water)**
- Type: Noun (feminine)
- English: Water
- CEFR Level: A1.1
- Pronunciation: oh
- **Example sentence:** "Je veux une bouteille d'**eau**, s'il vous plaît." (I want a bottle of **water**, please.)
- Context: Beverages/Restaurant
- Part of learned_vocabulary: ✅ (added Day 1)
```

---

## VOCABULARY PRACTICE APP FEATURE (Details)

### Mode 1: Bidirectional Translation
```
Prompt (French→English randomized):
"Translate to English: Café"
Answer: "The café" or "café" or "coffee shop" → ✅ Accept all
→ Mark as learned (spaced repetition)
→ Next appearance: Day 8-15 (if at Day 1)
```

### Mode 2: Bidirectional with STT/TTS
```
Prompt: "Listen to pronunciation and repeat:"
[Audio plays] "Café"
Student speaks into microphone
Feedback: "Good! Your pronunciation matches."
```

### Mode 3: Verb Conjugation (NEW)
```
Day 21+ (Passé Composé introduced):
Verb: "Aller"
Learned tenses: Présent (Day 1), Passé Composé (Day 21)

Prompt: "Conjugate 'aller' for 'je' in Passé Composé"
Expected answer: "Je suis allé"
Feedback: "Correct! Aller uses être as auxiliary in PC."

Day 61+ (Futur Simple introduced):
Learned tenses: Présent, Passé Composé, Futur Proche, Futur Simple
Prompt: "Conjugate 'aller' for 'nous' in Futur Simple"
Expected answer: "Nous allons" [wait, this is présent]
Correction: "Actually, Futur Simple: 'Nous irons'"
```

### Mode 4: Multiple Choice Context
```
Prompt: "Choose correct: Je ____ au café."
Options: a) suis b) vais c) ai d) veux
Answer: b) vais
Feedback: "Excellent! Aller (to go) is the correct verb here."
```

### Mode 5: Visual Recognition (If image available)
```
Display: Image of café
Prompt: "What is this place?"
Options: a) Restaurant b) Café c) Bibliotheque d) Gare
Answer: b) Café
```

---

## ASSESSMENT FRAMEWORK (Revised for Monthly Format)

### Daily Assessment:
- **5-8 random questions** from 50-question bank
- Mix of types: conjugation, fill_blank, listening, multiple_choice, translation
- Pass threshold: 70%
- Time: 5 minutes

### Weekly Assessment (Days 5, 10, 15, 20):
- **20-30 questions** covering all content from that week
- All 4 skills: La compréhension orale, compréhension écrite, production orale, production écrite
- Pass threshold: 70%
- Time: 20-30 minutes

### Monthly Exam (Day 20 of each month):
- **Comprehensive DELF-aligned mock exam**
- Component 1 (Listening): 25-30 min
- Component 2 (Reading): 30-45 min
- Component 3 (Writing): 30-45 min
- Component 4 (Speaking): 15-20 min
- Total: 100 points (25 per component)
- Pass: ≥50 points
- Pass recommendation: Move to next month
- Fail: Remedial option (optional retake)

### Vocabulary Tracking:
- Each learned word marked with introduction day
- Spaced repetition: Reappear every 7, 14, 30 days
- Vocabulary mastery % calculated per month
- Goal: 95% vocabulary retention

---

## MONTHLY BREAKDOWN: DETAILED GRAMMAR PROGRESSION

### MONTH 1: A1.1 (Days 1-20)

| Week | Focus | Grammar Topics |
|------|-------|---|
| 1 | Foundation | être, avoir, regular -ER verbs, present tense basics |
| 2 | Verb Families | -IR verbs, -RE verbs, irregular stems (aller) |
| 3 | Nouns & Adjectives | Gender (M/F), number (S/P), article agreement, adjective placement |
| 4 | Communication | Basic questions, negation (ne...pas), imperatives, greetings |

**Cumulative vocabulary by week end:**
- Week 1: 25 words (greetings, personal pronouns, identity)
- Week 2: 50 words (+ daily activities, family)
- Week 3: 75 words (+ colors, adjectives, objects)
- Week 4: 100 words (+ time, numbers, basic verbs)

---

### MONTH 2: A1.2 (Days 21-40)

| Week | Focus | Grammar Topics |
|------|-------|---|
| 1 | Past Actions | Passé composé with avoir, past participle patterns, irregular forms |
| 2 | More Past | Passé composé with être, agreement rules, negation in PC |
| 3 | Future Plans | Futur proche (aller + inf), immediate future vs. plans |
| 4 | Possession & Politeness | Possessive adjectives, complex negation, polite requests |

**Vocabulary:** Food/dining (25), travel/locations (25), family relations (25), time/temporal (25)

---

### MONTH 3: A2.1 (Days 41-60)

| Week | Focus | Grammar Topics |
|------|-------|---|
| 1 | Habitual Past | Imparfait formation, irregular stems, uses (habit, state, background) |
| 2 | Narratives | Passé composé vs. Imparfait contrast, narrative structures, transitions |
| 3 | Comparisons | Comparatives (plus...que, moins...que, aussi...que), superlatives (le plus) |
| 4 | Complex Sentences | Relative pronouns (qui, que, où), embedded clauses |

**Vocabulary:** Travel/transport (25), shopping (25), descriptions/adjectives (25), emotions/states (25)

---

### MONTH 4: A2.2 (Days 61-80)

| Week | Focus | Grammar Topics |
|------|-------|---|
| 1 | Future Plans | Futur simple (regular + irregular), when to use each future form |
| 2 | Hypothetical | Conditionnel présent, polite requests, si-clauses (imparfait + cond) |
| 3 | Advanced Pronouns | Pronouns Y & EN, combined pronouns, complex pronoun placement |
| 4 | Daily Routines | Reflexive verbs (se, me, te), indirect speech (il dit que...), complex narratives |

**Vocabulary:** Restaurants/menus (25), shopping transactions (25), routines/actions (25), wishes/hypotheticals (25)

---

### MONTHS 5-8: B1.1 → B2.2 (Days 81-160)

**Progressive complexity:**
- Month 5: Subjunctive intro, past perfect, advanced pronouns
- Month 6: Passive voice, participle clauses, literary structures
- Month 7: Stylistic variation, register shifts, argumentative language
- Month 8: Mastery consolidation, specialized vocabulary, dialect awareness

**Vocabulary per month:** 100 words per specialization path

---

### MONTHS 9-12: Specialization (Days 161-240)

**User selects 1 path:**
- **Business French:** Professional vocabulary, negotiation, formal correspondence
- **Literary French:** Classic texts, poetry, literary analysis
- **Cultural French:** Cinema, history, philosophy, contemporary France
- **Conversational Mastery:** Regional dialects, authentic speech patterns

**100 vocabulary words per path per month**

---

## FILE ORGANIZATION (Implementation)

```
NEW_CURRICULUM_REDESIGNED/
├── Month_1_A1.1.md (Days 1-20)
├── Month_2_A1.2.md (Days 21-40)
├── Month_3_A2.1.md (Days 41-60)
├── Month_4_A2.2.md (Days 61-80)
├── Month_5_B1.1.md (Days 81-100)
├── Month_6_B1.2.md (Days 101-120)
├── Month_7_B2.1.md (Days 121-140)
├── Month_8_B2.2.md (Days 141-160)
├── Specialization_Paths/
│   ├── Month_9_BusinessFrench.md (Days 161-180)
│   ├── Month_10_BusinessFrench.md (Days 181-200)
│   ├── Month_11_BusinessFrench.md (Days 201-220)
│   ├── Month_12_BusinessFrench.md (Days 221-240)
│   ├── [Alternative: LiteraryFrench / CulturalFrench / ConversationalMastery paths]
└── CURRICULUM_MASTER_INDEX.md (metadata + vocabulary tracking)
```

---

## NEXT SESSION PLAN

### Deliverable per Session:
- **Session 1 (Current):** Overall plan (DONE ✅)
- **Session 2:** Month 1 complete (Days 1-20, 100 words, all details, 4 weeks)
- **Session 3:** Month 2 complete (Days 21-40)
- **Session 4:** Month 3 complete (Days 41-60)
- **Session 5:** Month 4 complete (Days 61-80)
- **Sessions 6-9:** Months 5-8 (one per session)
- **Session 10:** Choose specialization path
- **Sessions 11-14:** Months 9-12 (specialization, one per session)

**Total estimated sessions:** 14-16 sessions for complete 12-month curriculum

---

## DATABASE STRUCTURE (Program Requirements)

### New Table: `learned_vocabulary`
```sql
CREATE TABLE learned_vocabulary (
  word_id INT PRIMARY KEY,
  french_word VARCHAR(100),
  english_translation VARCHAR(200),
  word_type ENUM('noun', 'verb', 'adjective', 'adverb', 'preposition', 'interjection'),
  cefr_level ENUM('A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2'),
  day_introduced INT,
  month_introduced INT,
  example_sentence VARCHAR(500),
  pronunciation VARCHAR(100),
  times_practiced INT DEFAULT 0,
  proficiency_score FLOAT DEFAULT 0.0 (0.0-1.0),
  last_reviewed DATE,
  is_verb BOOLEAN,
  verb_type VARCHAR(50) (if verb: regular_er, regular_ir, regular_re, irregular),
  context_domain VARCHAR(100) (e.g., "Greetings", "Food", "Travel")
);
```

### Verb Conjugation Tracking:
```sql
CREATE TABLE verb_conjugations (
  conjugation_id INT PRIMARY KEY,
  word_id INT (foreign key to learned_vocabulary),
  tense VARCHAR(50) (présent, PC, futur proche, futur simple, imparfait, conditionnel, subjonctif),
  day_introduced INT,
  je VARCHAR(50),
  tu VARCHAR(50),
  il_elle_on VARCHAR(50),
  nous VARCHAR(50),
  vous VARCHAR(50),
  ils_elles VARCHAR(50)
);
```

---

## STATUS

✅ **PLAN COMPLETED AND SAVED**

**Next Step:** Session 2 → User requests Month 1 (Days 1-20) with all details

---

## SUMMARY OF CHANGES FROM PHASE 1 FEEDBACK

| Feedback | Change | Status |
|----------|--------|--------|
| Context sentences for vocab | Added example sentence per word | ✅ Implemented |
| 10 words → 5 words | Reduced vocab/day: 5 not 10 | ✅ Implemented |
| Vocabulary database | `learned_vocabulary` table specified | ✅ Designed |
| Verb conjugation in practice | Random conjugation from learned tenses | ✅ Specified |
| Month-based not week-based | Plan reorganized by 12 months × 20 days | ✅ Implemented |
| Monthly delivery format | 1 month per session (Days 1-20, 4 weeks) | ✅ Structured |
| Program requirements doc | All feature requests documented | ✅ Captured |

