---

# **📘 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)**

## **AI French Tutor \- "Le Professeur Strict"**

**Version:** 1.0  
 **Date:** 06.02.2026  
**Project Duration:** 9 months (A1 → B2)

---

## **1\. EXECUTIVE SUMMARY**

### **1.1 Project Vision**

Uzun soluklu, kişiselleştirilmiş, CEFR standartlarına uygun bir Fransızca öğrenme platformu. Öğrenci ilerlemesini takip eden, zayıf noktaları tespit edip özel çalışma planları sunan, "kıl hoca" karakterinde bir AI öğretmen.

### **1.2 Core Problem**

* Mevcut uygulamalar (Busuu, Duolingo) tekrara düşüyor  
* Aynı örnekler ezberlenince ilerleme durağanlaşıyor  
* Gramer derinliği yetersiz  
* Kişiselleştirilmiş müfredat yok  
* Sınav sistemi statik

### **1.3 Solution**

Generative AI destekli, her seferinde farklı sorular üreten, öğrenci performansına göre adapte olan, gramer odaklı, okuma hedefli bir öğretmen sistemi.

---

## **2\. FUNCTIONAL REQUIREMENTS**

### **2.1 User Profile & Learning Path**

**FR-001: CEFR Level System**

* Seviyeler: A1.1, A1.2, A2.1, A2.2, B1.1, B1.2, B2.1, B2.2  
* Her seviye: 4-5 hafta  
* Toplam süre: \~36 hafta (9 ay)
* Tempo: A1 hizli ilerler, A2/B1 dengeli, B2 daha yavas ve daha fazla tekrar

**FR-002: Study Schedule**

* Hafta içi: 5 gün × 30 dakika \= 150 dk/hafta  
* Hafta sonu: 2 gün × 2 ders × 30 dk \= 120 dk/hafta  
* **Toplam:** 270 dakika/hafta (\~4.5 saat)
* Hafta sonu oturumlari: 1 oturum review + SRS, 1 oturum 45 dk sinav

**FR-003: User Preferences**

* Öğrenme stili: Text \+ Ses \+ Pratik dengeli (minimal görsel)  
* Hedef: Kitap/gazete okuma yetkinliği  
* Gramer: İngilizce karşılaştırmalı, bol örnekli  
* Konuşma: Günlük diyalog \+ senaryo bazlı

---

### 2.1.2 Dynamic Lesson Generation System

**FR-004: Curriculum-Driven Lesson Generation**

* **Purpose:** Generate lessons dynamically from structured curriculum files instead of static database storage
* **Inputs:** Week number (1-52), day number (1-7), student level, student weaknesses
* **Process:**
  1. Load curriculum file (`New_Curriculum/wk{N}.md`) for requested week
  2. Parse curriculum structure: learning outcomes, grammar target, vocabulary set, speaking scenario, homework task
  3. Build system prompt (roles, course scope, big picture)
  4. Build lesson generation prompt (curriculum context + student profile)
  5. Call Gemini API with complete context
  6. Validate and return generated lesson JSON

* **Output:** Complete lesson JSON with:
  * Grammar section (explanation, form, 5+ examples, conjugation table, error focus)
  * Vocabulary section (21 words with translations, examples, pronunciation tips)
  * Speaking section (scenario prompt, targets, expected elements)
  * Quiz section (3-5 questions with explanations)
  * Homework section (prompt, requirements, rubric, estimated time)
  * Session metadata (duration estimates, pace recommendations)

* **Key Benefits:**
  * No lesson storage limit (infinite content generation)
  * No week restriction (students can start at any week)
  * Fresh examples each time (prevents memorization)
  * Curriculum-aligned (AI follows structured weekly plans)
  * Personalized (adapts to student weaknesses and level)

**FR-005: Curriculum File Structure**

* Location: `New_Curriculum/wk{1-52}.md` (52-week progression A1.1 → B2.2)
* Required sections:
  * Learning Outcomes (CEFR descriptors for the week)
  * Grammar Target (form, complexity, prerequisites, 7-step scaffolding sequence)
  * Vocabulary Set (21 words with semantic domain)
  * Speaking Scenario (domain, prompt in French, AI role, targets)
  * Reading/Listening Component (type, content description, comprehension tasks)
  * Homework Assignment (type, task description, detailed rubric with pass criteria)

* Consistency Requirement: All files must follow same markdown format for reliable parsing

**FR-006: System Prompt (Big Picture Context)**

* **Content:** Explains to AI:
  * Its role as rigorous French tutor ("strict professor")
  * Course scope (52 weeks, A1 → B2, CEFR-aligned)
  * Student context (current level, completed weeks, known weaknesses)
  * Course philosophy (grammar-focused, practical scenarios, error correction)
  * Constraints (follow curriculum exactly, provide specific feedback, maintain difficulty)

* **Used in:** Every lesson generation call
* **Token cost:** ~300 tokens per call
* **Purpose:** Frames all subsequent AI responses with consistent perspective and constraints

**FR-007: Lesson Generation Prompt (Main Curriculum-to-Lesson Transformation)**

* **Content:** Instructs AI to:
  * Transform curriculum metadata into structured lesson JSON
  * Include all 21 vocabulary words in examples
  * Provide 5+ progressive examples for grammar
  * Adapt difficulty if student has related weaknesses
  * Follow scaffolding steps from curriculum exactly
  * Return ONLY valid JSON (no markdown, no extra text)

* **Input Variables:**
  * Curriculum JSON (parsed from wk{N}.md)
  * Learning outcomes for the week
  * Grammar target with scaffolding steps
  * Vocabulary set (all 21 words)
  * Speaking scenario requirements
  * Homework task and rubric
  * Student level and weaknesses

* **Output:** Valid JSON with lesson structure (see FR-004)
* **Token cost:** ~2000-3000 tokens per call
* **Failure modes & handling:**
  * Invalid JSON → Parse error, show user "Lesson generation failed, please retry"
  * Missing sections → Validate response schema before returning
  * Hallucinated content → Prompt includes "Do NOT deviate from curriculum"

**FR-008: Weakness Personalization Subprompt (Adaptive Scaffolding)**

* **Content:** When student has documented weaknesses:
  * Add extra examples specifically targeting the weakness
  * Provide clear English parallels for confusing topics
  * Include focused homework exercise for weakness topic
  * Test weakness explicitly in quiz question
  * Mark weakness in speaking targets for conscious attention

* **Trigger:** Only included if `student_weaknesses[]` is non-empty
* **Combined with:** LESSON_GENERATION_PROMPT as additional instruction
* **Purpose:** Provide extra scaffolding while maintaining rigor (not lowering standards)

**FR-009: Homework Evaluation Prompt (Automatic Grading Logic)**

* **Content:** Instructs AI to evaluate student homework against rubric:
  * Score text for grammar, vocabulary, content quality (0-100)
  * Score audio transcript for pronunciation, rhythm, clarity (0-100)
  * Apply pass criteria (text ≥70% AND audio ≥60%)
  * Provide specific corrections with explanations
  * Highlight strengths and suggest next focus area

* **Used in:** POST `/api/homework/submit` endpoint
* **Output:** JSON with text_score, audio_score, passed flag, detailed feedback, corrections list
* **Grading scale:** 90-100=excellent, 75-89=good, 70-74=passing, <70=needs revision

---

### **2.2 Lesson Structure**

**FR-010: Lesson Components (30 dakika)**

┌─────────────────────────────────────────┐  
│ 1\. Gramer Konusu (10 dk)                │  
│    \- İngilizce ile karşılaştırma        │  
│    \- 5+ örnek cümle                     │  
│    \- Conjugation tablosu                │  
├─────────────────────────────────────────┤  
│ 2\. Yeni Kelimeler (5 dk)                │  
│    \- 3 kelime/ders                      │  
│    \- Her biri örnek cümlede             │  
│    \- Telaffuz (TTS)                     │  
├─────────────────────────────────────────┤  
│ 3\. Konuşma Pratiği (10 dk)              │  
│    \- Senaryo verilir                    │  
│    \- Öğrenci sesli yanıt verir (STT)    │  
│    \- AI değerlendirir                   │  
├─────────────────────────────────────────┤  
│ 4\. Mini Quiz (5 dk)                     │  
│    \- 3-5 soru (çoktan seçmeli/boşluk)   │  
│    \- Anlık feedback                     │  
└─────────────────────────────────────────┘

* Hedef: 27 kelime/hafta (3 kelime x 9 oturum)

**FR-011: Homework System**

* Her ders sonunda 1 ödev verilir  
* Türler: Çeviri, kompozisyon, gramer alıştırması  
* Teslim formatı: text + audio zorunlu  
  * **Audio Options:**
        * **Record:** Yerel Python tabanlı ses kaydı (sounddevice) - 1/2/4/6/8/10 dk preset + custom (dakika)
    * **Upload:** MP3, WAV, OGG, FLAC, M4A formatlarında dosya yükleme
  * Min text length: 50 karakter
  * Max audio: 25 MB
* Deadline: bir sonraki dersten önce  
* **Zorunlu:** Teslim etmeden yeni derse geçilemez  
* AI otomatik değerlendirir \+ detaylı feedback (gramer, kelime, telaffuz)

**FR-012: Homework Evaluation Logic**

* **Text Evaluation (İçerik Değerlendirmesi):**
  * AI verilen ödevi doğru yanıtlayıp yanıtlamadığını kontrol eder
  * Gramer doğruluğu (conjugation, gender agreement, syntax)
  * Kelime seçimi ve kullanımı (uygun kelimeler, context)
  * İçerik kalitesi (ödev talimatlarına uygunluk)
  * **Min passing score:** 70%
  
* **Audio Evaluation (Telaffuz Değerlendirmesi):**
  * AI kullanıcının teslim ettiği metni okuyup okumadığını kontrol eder
  * Metne karşı STT (Speech-to-Text) transkript karşılaştırması
  * Telaffuz kalitesi (aksanlar, ses tonları, akıcılık)
  * Ritim ve vurgu (prosody)
  * **Min passing score:** 60%
  
* **Pass Criteria:**
  * Text score >= 70% AND Audio score >= 60% → **Geçti**
  * Aksi halde → **Tekrar gerekli** (ödev tekrarlanmalı)
  
* **Feedback Structure:**
  ```python
  feedback = {
      "grammar_feedback": "Conjugation errors in passé composé...",
      "vocabulary_feedback": "Good word choices, but 'travail' should be...",
      "pronunciation_feedback": "Rhythm is good, but 'r' sounds need work...",
      "overall_feedback": "Strong attempt. Focus on verb conjugation.",
      "text_score": 75,
      "audio_score": 65,
      "passed": True
  }
  ```

**FR-013: Speaking Practice Flow (Interactive)**

* **Purpose:** In-lesson practice with immediate feedback, multiple retries allowed
* **Duration:** 10 minutes per lesson (Section 3 of lesson structure)
* **Flow Architecture (Token-efficient for free tier):**
  1. **Scenario presented:** AI generates speaking scenario (text + TTS audio)
  2. **Push-to-talk recording:** Student holds button to speak (sounddevice)
  3. **STT conversion:** Whisper.cpp converts speech → text locally
  4. **Text-based AI evaluation:** Send transcribed text to Gemini API (not audio)
  5. **AI response:** Text feedback + suggestions in **French only**
  6. **TTS playback:** gTTS reads AI response aloud (symbols/emoji stripped)
  7. **Retry allowed:** Student can attempt again with new scenario or same
  
* **Key Design Decisions:**
  * **No audio sent to AI:** Only STT transcription sent (saves tokens on free tier)
  * **Local STT + cloud TTS:** Whisper runs locally, gTTS used for TTS
  * **Interactive, not evaluative:** Not stored in database, just practice
  * **Immediate feedback:** Real-time text + voice response
  * **Multiple attempts:** Students can retry scenarios until satisfied
  * **French-only feedback:** Prevent mixed-language TTS output
  * **TTS sanitization:** Remove emoji/symbols so TTS reads only text
  
* **Difference from Homework Audio:**
  * Speaking practice: STT → text → AI (text-based conversation)
  * Homework audio: Raw audio stored + STT comparison for pronunciation scoring
  
* **UI Pattern - Push-to-Talk (Walkie-Talkie Style):**
  * Single prominent "Push to Talk" button (microphone icon)
  * **Two input methods:**
    * **Mouse:** Click and hold button to record, release to stop
    * **Keyboard:** Press and hold SPACE to record, release to stop
  * Visual feedback: Button becomes highlighted/pressed when active
  * Recording status indicator: "🎤 Recording... speak now!"
  * Transcription displayed after recording completes
  * AI response shown as text + spoken via TTS
  * "Try again" button for retry with new scenario
  * No manual "Stop" button—purely press/hold activation

**FR-014: Interactive Lesson Flow (Weekly Plan Driven)**

* **Purpose:** Start lesson uses the weekly plan as the source of truth for the session.
* **Inputs:** Weekly plan (grammar target, vocabulary set, speaking scenario, mini-quiz).
* **Flow:**
  1. Load weekly plan by level and week number.
  2. Present grammar explanation and examples from the plan.
  3. Run vocabulary practice using plan vocabulary (FR->EN / EN->FR).
  4. Run speaking scenario using plan prompt and targets.
  5. Run mini-quiz using plan questions and immediate feedback.
  6. Mark section completion (complete/skip/retry) and persist progress.
* **Requirements:**
  * AI must follow the weekly plan sequence and scope.
  * User input is required at each section (response or skip).
  * Responses are logged for progress tracking and weakness analysis.
  * Lesson can resume from the last completed section.

---

### **2.3 Exam System**

**FR-020: Weekly Exams**

* Her hafta sonu seviye sınavı  
* Süre: 45 dakika  
* Sinav hafta sonu oturumlarindan birini degistirir (30 dk yerine 45 dk)
* Soru tipleri:  
  * Çoktan seçmeli (gramer) \- %30  
  * Boşluk doldurma (kelime) \- %20  
  * Çeviri (TR→FR, FR→TR) \- %20  
  * Konuşma (senaryo) \- %15  
  * Okuma parçası \+ sorular \- %15

**FR-021: Pass/Fail Criteria**

python  
PASS\_CONDITIONS \= {  
    "overall\_score": \>= 70%,  
    "critical\_topics": {  
        "conjugation": \>= 70%,  
        "vocabulary\_retention": \>= 70%,  
        "reading_comprehension": \>= 70%,  
        "speaking": \>= 70%  
    }  
}  
\`\`\`  
\- Genel %70 \+ kritik konular %70 → \*\*Geçti\*\*  
\- Aksi halde → \*\*Kaldı\*\*

\*\*FR-022: Fail Scenario\*\*  
\- AI detaylı analiz raporu sunar  
\- Zayıf konular belirlenir  
\- Özel çalışma planı oluşturulur  
\- 3\-5 ek ders \+ mini sınav  
\- Ek dersler takvimi uzatir (hafta kaydirma)  
\- Tekrar sınav (farklı sorularla)

\*\*FR-023: Dynamic Question Generation\*\*  
\- Her sınav denemesinde \*\*farklı sorular\*\*  
\- AI aynı konuyu farklı şekilde sorar  
\- Ezber önleme mekanizması

\---

\#\#\# 2.4 Weakness Analysis Module

\*\*FR-030: Performance Tracking\*\*  
\- Her soru/yanıt kaydedilir  
\- Yanlış cevaplar etiketlenir (gramer konusu, kelime, vb.)  
\- Haftalık rapor:  
\`\`\`  
  ┌─────────────────────────────────┐  
  │ Zayıf Konular                   │  
  ├─────────────────────────────────┤  
  │ 1\. Passé Composé (12 hata)      │  
  │ 2\. Pronouns Y/EN (8 hata)       │  
  │ 3\. Subjonctif (5 hata)          │  
  └─────────────────────────────────┘

**FR-031: Free Practice Mode**

* Öğrenci istediği zaman erişebilir  
* Zayıf konuları seçer  
* AI özel dersler verir  
* Sadece o konuya odaklanır  
* Progress kaydedilir

---

### **2.5 Vocabulary Management**

**FR-040: Spaced Repetition System (SRS)**

* Anki algoritması (SM-2)  
* Varsayilan SM-2 parametreleri: grade 0-5, ease factor baslangic 2.5, min 1.3  
* Gunluk review limiti: 50 kart  
* Kelimeler otomatik tekrar edilir  
* Başarı durumuna göre interval artar:  
  * İlk tekrar: 1 gün sonra  
  * İkinci: 3 gün sonra  
  * Üçüncü: 7 gün sonra  
  * vs.

**FR-041: Vocabulary Database**

```sql
vocabulary (
    id, word, translation, example_sentence,
    level, learned_date, last_review_date,
    review_count, success_rate, next_review_date
)
```

**FR-042: Vocabulary Practice Modes**

The system provides three modes for vocabulary practice:

1. **Daily Review (SRS-Based)**
   - Automatically loads vocabulary items due for review based on SM-2 algorithm
   - Maximum 50 items per day (daily cap)
   - Items come from lessons in srs_schedule table with next_review_date <= today
   - Focuses on spaced repetition for long-term retention

2. **Weak Areas Practice**
   - Loads vocabulary from lessons related to topics in weakness_tracking table
   - Targets topics where student has low accuracy (error_count > success_count)
   - Helps student strengthen specific weak points
   - Configurable limit (default: 10 questions)

3. **Comprehensive Review (All Vocabulary)**
   - Loads vocabulary from all completed lessons
   - Useful for general practice and preparation before exams
   - No filtering by SRS schedule or weaknesses
   - Configurable limit (default: 10 questions)

**Practice Format:**
- Multiple choice questions (3 options per question)
- Two question types randomized:
  - French → English: "What does 'un cahier' mean in English?"
  - English → French: "How do you say 'notebook' in French?"
- Incorrect answers tracked in weakness_tracking for adaptive learning
- Real-time feedback with correct answer shown

**FR-043: Lesson Review with Fresh Examples**

Students can review previously completed lessons with AI-generated fresh content:

- **Review Trigger:** Student clicks "Review" button on lesson card
- **AI Generation:** System calls generate_lesson_ai() with same topic but requests NEW examples
- **Content Changes:**
  - Same grammar topic and explanation
  - NEW example sentences (different from original lesson)
  - NEW vocabulary items (3 fresh words)
  - NEW speaking practice prompt
- **No Requirements:** Review lessons have NO homework and NO exam sections
- **Use Case:** Re-learning grammar concepts without static repetition
- **Tracking:** Review lessons marked with is_review=true flag and original_lesson_id reference

**API Endpoints:**
- GET /api/vocabulary/practice?mode=daily|weak|all&limit=10
- POST /api/vocabulary/check (validates answer, returns feedback)
- POST /api/lessons/{lesson_id}/review (generates fresh review lesson)

**FR-044: Enhanced MCQ Distractors (Future Enhancement)**

Improve multiple choice question quality by using real vocabulary as distractors:

- **Current State:** Placeholder distractors ("option A", "mot B", "option C")
- **Target State:** Real French words from other lessons as distractors
- **Implementation:**
  - Query vocabulary from lessons at similar CEFR level
  - Select semantically unrelated words (avoid synonyms or related concepts)
  - Ensure distractors are plausible but clearly incorrect
  - Maintain 3-option format (1 correct + 2 realistic distractors)
- **Benefit:** More realistic practice, prevents students from eliminating obviously fake options

**FR-045: Fill-in-Blank Question Type (Future Enhancement)**

Add cloze exercises to vocabulary practice for variety:

- **Question Format:** "Elle lit un ____ dans la bibliothèque." → Options: [livre, cahier, stylo]
- **Generation:**
  - Extract sentences from lesson examples
  - Blank out target vocabulary word
  - Provide 3 options (correct word + 2 distractors from same word class)
- **Mixing:** Alternate between MCQ translation and fill-in-blank within practice sessions
- **Benefit:** Tests vocabulary in context, not just isolated translation

**FR-046: Vocabulary Statistics Dashboard (Future Enhancement)**

Provide comprehensive vocabulary mastery overview:

- **Metrics to Display:**
  - Total vocabulary learned (by CEFR level)
  - Mastery percentage (words with ease_factor >= 2.5)
  - Words due for review today/this week
  - Weak words list (low success rate in weakness_tracking)
  - SRS schedule calendar (heatmap of upcoming reviews)
  - Learning velocity (words learned per week)
- **Visualizations:**
  - Progress bars by level (A1/A2/B1/B2)
  - Pie chart: Mastered vs In Progress vs Struggling
  - Line graph: Vocabulary growth over time
- **Actionable Insights:** Highlight specific words needing attention

**FR-047: Audio Pronunciation in Vocabulary Practice (Future Enhancement)**

Add TTS playback to help students hear correct pronunciation:

- **Trigger:** Speaker icon next to French word in flashcard
- **Implementation:** Call existing sanitize_tts_text() + gTTS pipeline
- **Caching:** Store generated MP3 files to avoid regenerating on each practice; reuse cached file if already generated
- **Format:** Small inline audio player beneath the question for quick replay
- **Benefit:** Reinforces listening skills and correct pronunciation during vocab review

---

### 2.6 Content Recommendations

\*\*FR-050: Podcast/Video Suggestions\*\*  
\- Her seviyeye uygun içerik önerileri  
\- İsteğe bağlı, ilerleme için zorunlu değil  
\- A1: "InnerFrench" (beginner-friendly)  
\- A2: "Coffee Break French"  
\- B1: "News in Slow French"  
\- B2: France Culture podcasts

\*\*FR-051: Reading Material\*\*  
\- Seviyeye göre makale önerileri  
\- B1+: Le Monde Diplomatique  
\- B2: Literatür önerileri (Le Petit Prince, etc.)

\---

\#\#\# 2.7 Motivation & Gamification

\*\*FR-060: Simple Gamification\*\*  
\- \*\*Streak Counter:\*\* Günlük ders yapma serisi  
\- \*\*Level Up:\*\* Her seviye tamamlandığında badge  
\- \*\*Progress Bar:\*\* Mevcut seviyede ilerleme %

\*\*FR-061: Strict Teacher Personality\*\*  
\- Ödevi teslim etmezse: "Ödevini yapmadan devam edemezsin\!"  
\- Sınavda başarısız: "Maalesef yeterli değil. Şu konuları tekrar çalışmalısın..."  
\- Başarılı olunca: "Aferin\! Artık bir seviye daha ilerliyorsun."  
\- Motivasyonel ama disiplinli ton

\---

\#\# 3\. NON-FUNCTIONAL REQUIREMENTS

\#\#\# 3.1 Performance  
\- \*\*NFR-001:\*\* Ders yükleme süresi \< 2 saniye  
\- \*\*NFR-002:\*\* STT (Whisper) yanıt süresi \< 3 saniye  
\- \*\*NFR-003:\*\* TTS (gTTS) ses üretimi \< 2 saniye

\#\#\# 3.2 Usability  
\- \*\*NFR-010:\*\* FastAPI tabanli web arayuzu (HTML/CSS/JS)  
\- \*\*NFR-011:\*\* Responsive tasarım (1280×720 minimum)  
\- \*\*NFR-012:\*\* Push-to-talk mikrofon butonu

\#\#\# 3.3 Reliability  
\- \*\*NFR-020:\*\* Tüm veriler lokal SQLite'da  
\- \*\*NFR-021:\*\* Otomatik yedekleme (her ders sonunda)  
\- \*\*NFR-022:\*\* AI API hatalarında fallback mesajı

\#\#\# 3.4 Security  
\- \*\*NFR-030:\*\* Gemini API key güvenli saklanır (.env)  
\- \*\*NFR-031:\*\* Kullanıcı verileri şifrelenmez (lokal olduğu için)

\---

\#\# 4\. TECHNICAL ARCHITECTURE

\#\#\# 4.1 System Overview  
\`\`\`  
┌─────────────────────────────────────────────────────┐  
│      FRONTEND (HTML/CSS/JS via FastAPI)             │  
│  ┌─────────────┬─────────────┬──────────────┐      │  
│  │ Ders Ekranı │ Sınav Ekranı│ Rapor Ekranı │      │  
│  └─────────────┴─────────────┴──────────────┘      │  
└───────────────────┬─────────────────────────────────┘  
                    │  
┌───────────────────▼─────────────────────────────────┐  
│           BUSINESS LOGIC (FastAPI)                  │  
│  ┌──────────────────────────────────────────┐      │  
│  │   LessonPlanner (Prompt-based)           │      │  
│  │   ExamGenerator (Dynamic Questions)      │      │  
│  │   PerformanceAnalyzer (Weakness Tracker) │      │  
│  │   HomeworkManager (Mandatory Checks)     │      │  
│  └──────────────────────────────────────────┘      │  
└───────────────────┬─────────────────────────────────┘  
                    │  
    ┌───────────────┼───────────────┬────────────────┐  
    │               │               │                │  
┌───▼────┐    ┌────▼─────┐   ┌────▼────┐    ┌──────▼──────┐  
│ Gemini │    │ Whisper  │   │  gTTS   │    │   SQLite    │  
│  API   │    │   STT    │   │   TTS   │    │  \+ChromaDB  │  
│ (Free) │    │ (Lokal)  │   │ (Cloud)│    │   (Lokal)   │  
└────────┘    └──────────┘   └─────────┘    └─────────────┘

### **4.2 Technology Stack**

| Component | Technology | Justification |
| ----- | ----- | ----- |
| Frontend | FastAPI + HTML/CSS/JS (Vanilla) | Hızli, hafif, REST API tabanli |
| AI Agent | Gemini 2.5 Flash | Hizli, ucuz, free-tier uyumlu |
| STT | Whisper (base model) | Lokal, hızlı, Fransızca destekli |
| TTS | gTTS | Basit, stabil, Fransizca icin yeterli |
| Database | SQLite | Basit, lokal, yeterli |
| Vector DB | ChromaDB | Semantic search (SRS için) |
| Audio Recording | sounddevice | Lokal Python tabanlı ses kaydı, güvenilir |
| Audio File I/O | soundfile | WAV format, ses dosyası işleme |

---

### **4.3 Database Schema**

sql  
\-- User Progress  
CREATE TABLE user\_profile (  
    id INTEGER PRIMARY KEY,  
    current\_level TEXT,  \-- A1.1, A1.2, etc.  
    started\_date DATE,  
    last\_login\_date DATE,  
    total\_study\_minutes INTEGER,  
    streak\_days INTEGER  
);

\-- Lessons  
CREATE TABLE lessons (  
    id INTEGER PRIMARY KEY,  
    level TEXT,  
    week\_number INTEGER,  
    lesson\_number INTEGER,  
    grammar\_topic TEXT,  
    vocabulary JSON,  \-- \[{word, translation, example}\]  
    speaking\_scenario TEXT,  
    homework\_prompt TEXT,  
    completed BOOLEAN,  
    completed\_date DATE  
);

\-- Homework Submissions  
CREATE TABLE homework (  
    id INTEGER PRIMARY KEY,  
    lesson\_id INTEGER,  
    submission\_text TEXT,  
    audio\_path TEXT,  
    ai\_feedback TEXT,  -- JSON: {grammar_feedback, vocabulary_feedback, pronunciation_feedback, overall_feedback}  
    text\_score FLOAT,   -- Text evaluation (0-100)  
    audio\_score FLOAT,  -- Pronunciation evaluation (0-100)  
    passed BOOLEAN,      -- True if text_score >= 70 AND audio_score >= 60  
    submitted\_date DATE,  
    FOREIGN KEY (lesson\_id) REFERENCES lessons(id)  
);

\-- Exam Results  
CREATE TABLE exams (  
    id INTEGER PRIMARY KEY,  
    level TEXT,  
    attempt\_number INTEGER,  
    overall\_score FLOAT,  
    conjugation\_score FLOAT,  
    vocabulary\_score FLOAT,  
    reading\_score FLOAT,  
    speaking\_score FLOAT,  
    passed BOOLEAN,  
    exam\_date DATE,  
    detailed\_report JSON  
);

\-- Practice Errors (Weakness Tracking)  
CREATE TABLE practice\_errors (  
    id INTEGER PRIMARY KEY,  
    grammar\_topic TEXT,  
    error\_type TEXT,  \-- conjugation, gender, syntax  
    question TEXT,  
    user\_answer TEXT,  
    correct\_answer TEXT,  
    timestamp DATETIME  
);

\-- Vocabulary (SRS)  
CREATE TABLE vocabulary (  
    id INTEGER PRIMARY KEY,  
    word TEXT,  
    translation TEXT,  
    example\_sentence TEXT,  
    level TEXT,  
    learned\_date DATE,  
    last\_review\_date DATE,  
    next\_review\_date DATE,  
    review\_count INTEGER,  
    success\_rate FLOAT  
);  
\`\`\`

\---

\#\# 5\. CEFR A1 → B2 CURRICULUM BREAKDOWN

\#\#\# 5.1 Level Structure  
\`\`\`  
A1 (Beginner) - 9 weeks  
├── A1.1 (Week 1-4): Basic Greetings, Present Tense, Basic Vocabulary  
└── A1.2 (Week 5-9): Past Tense (Passé Composé), Questions, Daily Routines

A2 (Elementary) - 9 weeks  
├── A2.1 (Week 10-13): Imparfait, Future Tense, Comparisons  
└── A2.2 (Week 14-18): Conditional, Pronouns (Y, EN), Intermediate Vocabulary

B1 (Intermediate) - 9 weeks  
├── B1.1 (Week 19-22): Subjonctif, Complex Sentences, Formal Writing  
└── B1.2 (Week 23-27): Passive Voice, Literary Tenses, News Reading

B2 (Upper Intermediate) - 9 weeks  
├── B2.1 (Week 28-31): Advanced Grammar, Idiomatic Expressions  
└── B2.2 (Week 32-36): Literature Analysis, Complex Argumentation

### **5.2 Weekly Theme Examples**

**A1.1 Week 1:**

* Grammar: Être/Avoir conjugation  
* Vocabulary: Bonjour, merci, au revoir  
* Speaking: Se présenter (Introducing yourself)  
* Homework: Write 5 sentences about yourself

**A2.1 Week 10:**

* Grammar: Imparfait vs Passé Composé  
* Vocabulary: Weather expressions  
* Speaking: Describe a childhood memory  
* Homework: Write a short story (past tense)

**B1.2 Week 24:**

* Grammar: Subjonctif usage after "bien que", "pour que"  
* Vocabulary: Political terms  
* Speaking: Debate a social issue  
* Homework: Write an opinion article (200 words)

---

## **6\. AI AGENT DESIGN**

### **6.1 Lesson Planner Agent**

python  
class LessonPlannerAgent:  
    """  
    Generates personalized lessons based on:  
    \- Current CEFR level  
    \- Past performance  
    ### **3.1 Performance  
    - **NFR-001:** Ders yükleme süresi < 2 saniye  
    - **NFR-002:** STT (Whisper) yanıt süresi < 3 saniye  
    - **NFR-003:** TTS (gTTS) ses üretimi < 2 saniye
      
    ### **3.2 Usability  
    - **NFR-010:** FastAPI tabanli web arayuzu (HTML/CSS/JS)  
    - **NFR-011:** Responsive tasarım (1280×720 minimum)  
    - **NFR-012:** Push-to-talk mikrofon butonu
    │      FRONTEND (HTML/CSS/JS via FastAPI)             │  
          
    │           BUSINESS LOGIC (FastAPI)                  │  
        \# 2\. Get learned vocabulary  
    │  │   LessonPlanner (Prompt-based)           │      │  
        learned\_vocab \= self.db.get\_vocabulary(user\_id)  
    │ Gemini │    │ Whisper  │   │  gTTS   │    │   SQLite    │  
          
    │ (Free) │    │ (Lokal)  │   │ (Cloud)│    │   (Lokal)   │  
        \# 3\. Get curriculum for this level  
        curriculum \= self.load\_curriculum(level)  
          
    | Component | Technology | Justification |
    | ----- | ----- | ----- |
    | Frontend | FastAPI + HTML/CSS/JS (Vanilla) | Hızli, hafif, REST API tabanli |
    | AI Agent | Gemini 2.5 Flash | Hizli, ucuz, free-tier uyumlu |
    | STT | Whisper (base model) | Lokal, hızlı, Fransızca destekli |
    | TTS | gTTS | Basit, stabil, Fransizca icin yeterli |
        \# 4\. Generate lesson with Gemini  
        prompt \= f"""  
    * Dependencies yükle:

    bash  
     pip install fastapi uvicorn[standard] python-multipart python-dotenv google-genai  
      pip install openai-whisper gTTS  
      pip install chromadb sqlalchemy sounddevice scipy
    * Whisper base model indir (auto-download)  
    * gTTS icin local model gerekmez  
    * Frontend CSS tema özelleştirme  
        1\. Grammar topic (compare with English)  
    # Run app  
    uvicorn main:app --reload
    GEMINI\_API\_KEY\=your\_api\_key\_here  
    DATABASE\_PATH\=./data/student.db  
    WHISPER\_MODEL\_PATH\=./models/ggml-medium.bin  
        """  
          
        response \= self.llm.invoke(prompt)  
        return json.loads(response)

### **6.2 Exam Generator Agent**

python  
class ExamGeneratorAgent:  
    """  
    Creates unique exams each attempt.  
    Avoids memorization by varying:  
    \- Question phrasing  
    \- Example sentences  
    \- Distractors in multiple choice  
    """  
      
    def generate\_exam(self, level, attempt\_number):  
        topics \= self.get\_level\_topics(level)  
          
        prompt \= f"""  
        Generate a French exam for {level} (attempt \#{attempt\_number}).  
          
        Include:  
        \- 10 multiple choice (grammar/conjugation)  
        \- 5 fill-in-the-blank (vocabulary)  
        \- 3 translation questions (TR→FR)  
        \- 1 reading passage \+ 3 questions  
        \- 1 speaking scenario  
          
        IMPORTANT: Create entirely NEW questions, different from previous attempts.  
        """  
          
        return self.llm.invoke(prompt)

### **6.3 Strict Teacher Prompts**

python  
TEACHER\_PROMPTS \= {  
    "homework\_missing": """  
        Ödevini henüz teslim etmedin\! Devam etmek için önce ödevini yapmalısın.  
        Bugün ders yok, sadece ödev.  
    """,  
      
    "exam\_failed": """  
        Maalesef sınavdan geçemedin. Genel notun {overall}% ama şu konularda   
        yetersizsin: {weak\_topics}.  
          
        Önce bu konuları çalışmalısın. Sana özel bir çalışma planı hazırladım.  
    """,  
      
    "exam\_passed": """  
        Tebrikler\! Sınavdan {score}% ile geçtin. Artık {next\_level} seviyesine   
        geçebilirsin. Hazır mısın?  
    """,  
      
    "mistake\_feedback": """  
        Yanlış\! Doğru cevap: "{correct}".   
        Senin cevabın "{user\_answer}" → Hata: {error\_type}.  
          
        Açıklama: {explanation}  
    """  
}

## **7\. IMPLEMENTATION ROADMAP (9 Months)**

### **Phase 1: Foundation (Weeks 1-4)**

**Week 1: Environment Setup**

* Python 3.11+ kurulumu  
* Virtual environment oluştur  
* Dependencies yükle:

bash  
 pip install fastapi uvicorn[standard] python-multipart python-dotenv google-genai  
  pip install openai-whisper gTTS  
  pip install chromadb sqlalchemy sounddevice scipy

* Proje klasör yapısı oluştur  
* Git repo başlat

**Week 2: STT/TTS Integration**

* Whisper base model indir (auto-download)  
* gTTS icin local model gerekmez  
* Basit test arayüzü (record → transcribe → speak)  
* Ses kalitesi optimizasyonu

**Week 3: Database Setup**

* SQLite schema oluştur  
* ChromaDB entegrasyonu  
* CRUD fonksiyonları  
* Test data seeding (ilk 50 kelime)

**Week 4: Gemini AI Integration**

* API key setup  
* LangChain \+ LangGraph kurulum  
* İlk basit agent testi  
* Prompt engineering (teacher personality)

---

### **Phase 2: Core Features (Weeks 5-12)**

**Week 5-6: Lesson Module**

* Lesson Planner Agent  
* Gramer açıklama formatı  
* Kelime öğretimi (TTS entegre)  
* Mini quiz sistemi

**Week 7-8: Homework System**

* Homework generator  
* Submission handler (text \+ audio)  
* AI evaluation engine  
* Zorunluluk kontrolü (block next lesson)

**Week 9-10: Exam System**

* Dynamic question generator  
* Multi-format questions (MCQ, fill, translate, speak)  
* Auto-grading  
* Pass/fail logic (overall \+ critical topics)

**Week 11-12: Weakness Analysis**

* Error tracking sistem  
* Weekly report generator  
* Free practice mode  
* Targeted lesson generator (zayıf konular)

---

### **Phase 3: Curriculum & Content (Weeks 13-18)**

**Week 13-14: A1 Curriculum**

* A1.1 müfredat (4 hafta içerik)  
* A1.2 müfredat  
* Kelime havuzu (300 kelime)  
* Konuşma senaryoları (20 adet)

**Week 15-16: A2 Curriculum**

* A2.1 \+ A2.2 müfredat  
* Kelime havuzu (400 kelime)  
* İlk okuma parçaları

**Week 17-18: B1-B2 Skeleton**

* B1 ve B2 ana konular belirleme  
* İleri seviye kelime havuzu  
* Literatür önerileri listesi

---

### **Phase 4: Advanced Features (Weeks 19-22)**

**Week 19-20: Spaced Repetition**

* SRS algoritması (SM-2)  
* Kelime tekrar scheduler  
* Daily review reminder

**Week 21-22: Content Recommendations**

* Podcast/video veritabanı  
* Seviye bazlı filtreleme  
* Otomatik öneriler

---

### **Phase 5: Polish & Testing (Weeks 23-26)**

**Week 23: UI/UX Improvements**

* Frontend CSS tema özelleştirme  
* Progress visualization  
* Gamification elements

**Week 24: Testing**

* Unit tests (critical functions)  
* Integration tests (end-to-end lesson flow)  
* AI response quality testing

**Week 25: Bug Fixes**

* Edge case handling  
* Error messages  
* Performance optimization

**Week 26: Documentation**

* User manual  
* Developer guide  
* API documentation

---

### **Phase 6: Beta & Launch (Weeks 27-36)**

**Week 27-28: Beta Program**

* Beta kullanici alimi (10-20 kisi)  
* Geri bildirim toplama akisi  
* Haftalik iyilestirme dongusu

**Week 29-30: Content Expansion**

* B1/B2 icerik derinlestirme  
* Okuma parcalari havuzu  
* Speaking senaryolari cesitlendirme

**Week 31-32: Reliability & Monitoring**

* Error logging ve raporlama  
* Performans metrikleri dashboard  
* Offline fallback senaryolari

**Week 33-34: Release Prep**

* Setup otomasyonu  
* Kullanici onboarding akisi  
* Son kalite kontrol

**Week 35-36: Launch & Stabilization**

* Ilk public release  
* Hotfix plani  
* 30 gun izleme ve bakim

---

## **8\. SUCCESS METRICS**

### **8.1 Learning Outcomes**

* A1 tamamlama: 9 hafta  
* A2 tamamlama: 18 hafta  
* B1 tamamlama: 27 hafta  
* B2 tamamlama: 36 hafta  
* Kelime dağarcığı: 1500+ kelime (B1 sonunda)  
* Gazete makalesi okuma (B2)

### **8.2 System Performance**

* Lesson generation \< 5 saniye  
* STT accuracy \> 85%  
* Exam question uniqueness \> 90%  
* User retention (günlük kullanım) \> 80%

### **8.3 User Satisfaction**

* Homework completion rate \> 90%  
* Exam pass rate (first attempt) \~70%  
* Streak maintenance \> 7 gün

---

## **9\. RISK MANAGEMENT**

| Risk | Probability | Impact | Mitigation |
| ----- | ----- | ----- | ----- |
| Gemini API rate limit | Medium | High | Implement caching, fallback responses |
| Whisper Turkish accuracy | Low | Medium | Use medium/large model, post-process |
| User burnout | High | High | Flexible study plans, motivational prompts |
| Content repetition | Medium | High | Dynamic generation, large content pool |
| Exam cheating (memorization) | Medium | Medium | Always generate new questions |


## **10\. CURRICULUM INTEGRATION & MODES**

### **10.1 Complete 9-Block Curriculum**

The system includes a full 9-block curriculum from A1.1 to B2.2 Final:

- 9 blocks x 4 weeks = 36 weeks total
- 60 vocabulary words per block = 540 total words
- 20 lessons per week (5 daily + weekend sessions)
- Curriculum source: French_Course_Weekly_Plan.md (updated with all 9 blocks)

### **10.2 Development Mode vs End-User Mode**

**Development Mode** (enabled via `?dev=true`):
- Access ANY lesson from ANY block
- Skip homework requirements
- All content unlocked for testing
- DEV MODE badge visible in header

**End-User Mode** (production default):
- Lessons unlock sequentially
- Homework is a mandatory blocker
- First-time use modal asks starting level (A1.1 through B2.2)
- Progression enforced by level and week

### **10.3 Curriculum UI Updates**

- SRS tab renamed to Curriculum
- Curriculum tab moved to the leftmost position
- Curriculum dashboard replaces SRS dashboard as top-level curriculum view

### **10.4 First-Time Use Flow**

1. On first launch, user is prompted to select a starting level
2. System saves starting level in settings
3. Lessons unlock from that level in end-user mode
4. Development mode bypasses the lock for testing

---

## **11\. FUTURE ENHANCEMENTS (Post-MVP)**

* Mobile app (React Native)  
* Multiplayer mode (leaderboard)  
* Native speaker video integration  
* C1-C2 levels  
* Other languages (Spanish, German)  
* Premium features (live tutoring)


## **12\. APPENDIX**

### **12.1 Quick Start Commands**

bash  
\# Clone project  
git clone \<your-repo\>  
cd french-tutor

\# Setup  
python \-m venv venv  
source venv/bin/activate  \# Windows: venv\\Scripts\\activate  
pip install \-r requirements.txt

\# Download models  
python scripts/download\_models.py

\# Run app  
uvicorn main:app --reload

### **12.2 Environment Variables**

bash  
\# .env  
GEMINI\_API\_KEY\=your\_api\_key\_here  
DATABASE\_PATH\=./data/student.db  
WHISPER\_MODEL\_PATH\=./models/ggml-medium.bin  
---

## **13\. SIGN-OFF**

**Project Owner:** \[Fikret Uzgan\]  
 **Start Date:** 06.02.2026  
 **Target Completion:** 06.11.2026 (9 months)
 **Status Update:** Curriculum integrated, Curriculum tab added, dev/end-user modes defined
