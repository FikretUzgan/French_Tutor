---

# **📘 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)**

## **AI French Tutor \- "Le Professeur Strict"**

**Version:** 2.0 (Updated for Fixed Curriculum Approach)  
 **Date:** 12.02.2026  
**Project Duration:** 12 months (52 weeks, A1.1 → B2.2 + Specialization Paths)

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

**Fixed Curriculum + AI Evaluation** yaklaşımı: Manuel hazırlanmış, kaliteli 52-haftalık müfredat (Week_1-52.md) tüm ders içeriğini sağlar (grammar, vocabulary, examples, quiz questions). AI sadece interaktif değerlendirme için kullanılır (speaking practice feedback, homework grading, exam scoring). Bu yaklaşım tutarlı içerik kalitesi, öğrenme çıktılarının öngörülebilirliği ve AI API maliyetlerinin düşüklüğünü garanti eder.

---

## **2\. FUNCTIONAL REQUIREMENTS**

### **2.1 User Profile & Learning Path**

**FR-001: CEFR Level System**

* Seviyeler: A1.1, A1.2, A2.1, A2.2, B1.1, B1.2, B2.1, B2.2 + Specialization Paths  
* Yapı: 52 hafta (12 ay), 5 gün/hafta = 20 gün/ay
* Vocabulary: 5 kelime/gün × 20 gün/ay = 100 kelime/ay × 12 ay = **1,200 toplam kelime**
* Monthly exams: Ayda 1 comprehensive exam (Days 20, 40, 60, 80, 100, 120, 140, 160)
* Tempo: A1 hizli ilerler (Month 1-2), A2/B1 dengeli (Month 3-6), B2 daha yavas ve daha fazla tekrar (Month 7-8), Specialization paths (Month 9-12)

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

### 2.1.2 Fixed Curriculum Loading System

**FR-004: Curriculum Content Loading (Fixed Content Approach)**

* **Purpose:** Load pre-authored lesson content from curriculum files (NO AI generation for lessons)
* **Inputs:** Week number (1-52), day number (1-5)
* **Process:**
  1. Load curriculum file (`Research/NEW_CURRICULUM_REDESIGNED/Week_{N}_*.md`) for requested week
  2. Parse fixed content: metadata, pre-written grammar (400+ words), vocabulary (5 words), examples (50), speaking prompts (fixed), quiz questions (50, pre-written)
  3. Extract content_identifiers from metadata for quiz question selection
  4. Return lesson object with all fixed content (NO AI generation)

* **Output:** Complete lesson object with:
  * Grammar section (pre-written 5-paragraph structure, 400+ words, conjugation tables)
  * Vocabulary section (5 words with French/English, gender, example sentences)
  * Examples section (50 pre-written progressive sentences)
  * Speaking section (fixed tier-appropriate prompts from curriculum)
  * Quiz section (50 pre-written questions, 8 shown per attempt)
  * Metadata (content_identifiers, speaking_tier, day number)

* **Key Benefits:**
  * Consistent content quality (manually authored by curriculum experts)
  * Predictable learning outcomes (no AI hallucination risk)
  * Low API costs (AI used only for evaluation, not content generation)
  * Scalable (52 curriculum files serve unlimited students)
  * Transparent (all content reviewable before deployment)

**FR-005: Curriculum File Structure (Fixed Content Files)**

* Location: `Research/NEW_CURRICULUM_REDESIGNED/Week_{N}_*.md` (52 files, Week 1-52)
* Each file contains: **5 days (Monday-Friday)** of complete lesson content
* Required sections per day:
  * **Metadata:** Day number, grammar topic, content_identifiers (exercise types), speaking_tier (1/2/3)
  * **Grammar Section:** Pre-written 5-paragraph explanation (400+ words minimum)
  * **Vocabulary:** 5 words with French/English, gender, plural, example sentences
  * **Examples:** 50 pre-written progressive sentences (statements, questions, negatives)
  * **Speaking Prompts:** Fixed tier-appropriate prompts (script-based → guided → free)
  * **Quiz Questions:** 50 pre-written questions with answer keys (multiple formats)
* Monthly exam structure: Day 20, 40, 60, 80, 100, 120, 140, 160 = comprehensive exams (4 sections)
* Consistency: All 52 files follow identical markdown structure for curriculum_loader.py parsing

**FR-006: AI Evaluation Prompts (Speaking/Homework/Exam Feedback Only)**

* **Purpose:** AI evaluates student performance, DOES NOT generate content
* **Use Cases:**
  1. **Speaking Practice Evaluation:** Analyze STT transcription → score pronunciation/grammar/fluency
  2. **Homework Grading:** Evaluate text+audio submission → provide detailed feedback
  3. **Exam Scoring:** Score written/speaking exam sections → generate rubric-based results

* **Evaluation Framework:**
  * Speaking Tier 1 (Months 1-2): Script adherence (0-100), basic pronunciation (0-100)
  * Speaking Tier 2 (Months 3-6): Grammar accuracy (0-100), scenario completion (0-100)
  * Speaking Tier 3 (Months 7-12): Fluency (0-100), complexity (0-100), naturalness (0-100)
  
* **Token cost:** ~500-1000 tokens per evaluation call (MUCH lower than content generation)
* **API usage:** Only when student submits speaking/homework/exam (not every lesson view)

**FR-007: Quiz Question Selection Logic (Fixed Bank, Not Generated)**

* **Purpose:** Select 8 questions from 50-question fixed bank per day
* **Selection Algorithm:**
  1. Parse 50 pre-written quiz questions from curriculum file
  2. Extract question metadata: type (multiple_choice, fill_blank, conjugation), answer key, content_identifier
  3. Filter by content_identifier variety (ensure mix of exercise types per attempt)
  4. Track shown_questions in lesson_progress table to avoid repeats
  5. Randomize order of selected 8 questions
  6. Display questions with immediate feedback (correct/incorrect)

* **Question Formats (all pre-written in curriculum files):**
  * Multiple choice (4 options with distractors)
  * Fill-in-blank (conjugation, vocabulary)
  * Translation (EN→FR, FR→EN)
  * Error detection (identify grammar mistakes)
  
* **Benefits:**
  * Consistent difficulty (questions manually calibrated)
  * No AI generation errors (all questions human-verified)
  * Variety across attempts (50-question pool → 15+ unique quiz sets)

**FR-008: Homework Evaluation Prompt (AI Grading with Fixed Rubric)****

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

  * Hedef: 100 kelime/ay (5 kelime/gün × 20 gün)

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

**FR-013: On-Demand Grammar Expansion (Optional Future Feature)**

* **Purpose:** Allow learners to request ADDITIONAL grammar explanation beyond fixed curriculum content
* **UI Controls:**
  * "More Explanation" button within lesson grammar section
  * "More Examples" button within lesson grammar section
* **Behavior:**
  * Calls AI to generate SUPPLEMENTARY explanation (does NOT replace fixed content)
  * Appends AI-generated examples to existing curriculum content
  * Preserves original fixed curriculum content
* **Constraints:**
  * Must stay aligned with the current day's grammar topic
  * Must avoid repeating examples from curriculum file
  * Clear indication this is "AI-generated supplement" (not curriculum content)
* **Fallback:** If AI expansion fails, show friendly error and keep existing curriculum content

**FR-014: Grammar Reference Tab (Fixed Content Library)****

* **Purpose:** Provide a fixed, searchable grammar reference separate from dynamic lessons
* **Content:** Curated, non-AI grammar explanations organized by topic (tenses, pronouns, negation, questions, etc.)
* **UI:** A dedicated "Grammar" tab with topic selector and quick examples
* **Use Cases:**
  * Students reviewing a specific grammar topic outside the lesson flow
  * Reliable reference when AI output is insufficient
  * Standardized explanations for consistency across lessons
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
* **Flow Architecture:**
  1. **Scenario presented:** Load fixed speaking prompt from curriculum file (text + TTS audio)
  2. **Push-to-talk recording:** Student holds button to speak (sounddevice)
  3. **STT conversion:** Whisper.cpp converts speech → text locally
  4. **AI evaluation:** Send transcribed text to Gemini API for speaking feedback
  5. **AI response:** Text feedback + suggestions in **French only**
  6. **TTS playback:** gTTS reads AI response aloud (symbols/emoji stripped)
  7. **Retry allowed:** Student can attempt same prompt again or proceed
  
  * **Difference from Homework Audio:**
  * Speaking practice: STT → text → AI evaluation (interactive feedback)
  * Homework audio: Raw audio stored + STT comparison + AI grading (formal assessment)
  
* **Key Design Decisions:**
  * **Fixed speaking prompts:** All scenarios pre-written in curriculum files (no AI generation)
  * **AI evaluates only:** AI analyzes student's transcribed response, provides feedback
  * **No audio sent to AI:** Only STT transcription sent (saves tokens)
  * **Local STT + cloud TTS:** Whisper runs locally, gTTS used for TTS
  * **Interactive, not evaluative:** Not stored in database, just practice
  * **Immediate feedback:** Real-time text + voice response
  * **Multiple attempts:** Students can retry same prompt until satisfied
  * **French-only feedback:** Prevent mixed-language TTS output
  * **TTS sanitization:** Remove emoji/symbols so TTS reads only text
  
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

**FR-015: Interactive Lesson Flow (Fixed Curriculum Content Display)**

* **Purpose:** Display lesson content from curriculum files, no AI generation
* **Inputs:** Week number, day number
* **Flow:**
  1. Load curriculum file (Week_{N}_*.md) and parse day content
  2. Display pre-written grammar explanation (400+ words, 5-paragraph structure)
  3. Display vocabulary (5 words with examples, TTS playback available)
  4. Display 50 example sentences (progressive: statements, questions, negatives)
  5. Load speaking prompt from curriculum (fixed, tier-appropriate)
  6. Load quiz questions (select 8 from 50-question fixed bank)
  7. Mark section completion (complete/skip) and persist progress
* **Requirements:**
  * All content sourced from curriculum files (NO AI generation)
  * User input required for quiz answers and speaking practice
  * Responses logged for progress tracking and weakness analysis
  * Lesson can resume from last completed section

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

**FR-043: Lesson Review with Question Rotation**

Students can review previously completed lessons with different quiz questions:

- **Review Trigger:** Student clicks "Review" button on lesson card
- **Content Display:** Same fixed curriculum content (grammar, vocabulary, examples)
- **Quiz Variation:** System selects DIFFERENT 8 questions from 50-question fixed bank
  - Track which questions already shown in previous attempts
  - Rotate to questions 9-16, 17-24, etc. on subsequent reviews
  - Ensures variety without AI generation
- **Speaking Practice:** Same fixed prompt (students can retry for better performance)
- **No Requirements:** Review lessons have NO homework blocking
- **Use Case:** Re-learning grammar concepts with different quiz questions
- **Tracking:** Review sessions marked with is_review=true flag and question_ids_shown array

**API Endpoints:**
- GET /api/vocabulary/practice?mode=daily|weak|all&limit=10
- POST /api/vocabulary/check (validates answer, returns feedback)
- POST /api/lessons/{week}/{day}/review (loads same lesson with different quiz questions)

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

### **5.2 Daily Lesson Examples (Fixed Curriculum Content)**

**Month 1, Week 1, Day 1 (A1.1):**
* Grammar: Être conjugation (pre-written 5-paragraph, 400+ words)
* Vocabulary: je, tu, il/elle, nous, vous (5 words with examples)
* Examples: 50 progressive sentences (Je suis étudiant., Tu es français?, ...)
* Speaking: "Introduce yourself" (fixed Tier 1 script-based prompt)
* Quiz: 8 questions from 50-question bank (conjugation, fill_blank)

**Month 2, Week 5, Day 21 (A1.2):**
* Grammar: Passé composé with avoir (pre-written with conjugation table)
* Vocabulary: manger, parler, finir, choisir, regarder (5 words)
* Examples: 50 sentences (J'ai mangé une pomme., ...)
* Speaking: "Describe what you did yesterday" (Tier 1 guided)
* Quiz: 8 questions from 50-question bank

**Month 6, Week 24, Day 120 (B1.2 - Monthly Exam):**
* Comprehensive exam (DELF-aligned, 4 sections)
* Listening (25pts), Reading (25pts), Writing (25pts), Speaking (25pts)
* Pass threshold: 50/100 points
* Duration: 60-90 minutes

---

## **6. AI EVALUATION SYSTEM DESIGN (NOT Content Generation)**

### **6.1 Curriculum Loader (Fixed Content Parser)**

```python
class CurriculumLoader:
    """
    Loads pre-authored lesson content from curriculum files.
    NO AI generation - all content pre-written in markdown files.
    """
    
    def load_lesson(self, week, day):
        # 1. Load curriculum file
        file_path = f"Research/NEW_CURRICULUM_REDESIGNED/Week_{week}_*.md"
        curriculum_text = self.read_file(file_path)
        
        # 2. Parse sections (markdown parsing)
        metadata = self.parse_metadata(curriculum_text, day)
        grammar = self.parse_grammar_section(curriculum_text, day)
        vocabulary = self.parse_vocabulary(curriculum_text, day)  # 5 words
        examples = self.parse_examples(curriculum_text, day)      # 50 sentences
        speaking_prompt = self.parse_speaking(curriculum_text, day)
        quiz_questions = self.parse_quiz(curriculum_text, day)    # 50 questions
        
        # 3. Return lesson object
        return {
            "week": week,
            "day": day,
            "grammar": grammar,                # Pre-written 400+ words
            "vocabulary": vocabulary,          # Fixed 5 words
            "examples": examples,              # Fixed 50 sentences
            "speaking_prompt": speaking_prompt,# Fixed tier-appropriate prompt
            "quiz_pool": quiz_questions,      # Fixed 50 questions
            "content_identifiers": metadata["content_identifiers"],
            "speaking_tier": metadata["speaking_tier"]
        }

### **6.2 AI Evaluation Agent (Speaking/Homework/Exam Grading)**

```python
class AIEvaluator:
    """
    Evaluates student performance using Gemini API.
    DOES NOT generate content - only evaluates student responses.
    """
    
    def evaluate_speaking(self, student_transcript, speaking_tier, expected_targets):
        # AI evaluates transcribed speaking response
        prompt = f"""
        Evaluate this French speaking response:
        
        Student transcript: "{student_transcript}"
        Speaking tier: {speaking_tier}
        Expected elements: {expected_targets}
        
        Provide:
        - Grammar accuracy (0-100)
        - Vocabulary usage (0-100)
        - Fluency assessment for tier {speaking_tier}
        - Specific corrections with explanations
        """
        
        return self.gemini_api.evaluate(prompt)
    
    def evaluate_homework(self, text_submission, audio_transcript, rubric):
        # AI grades homework against fixed rubric
        prompt = f"""
        Evaluate this French homework:
        
        Text submission: "{text_submission}"
        Audio transcript: "{audio_transcript}"
        Rubric: {rubric}
        
        Score:
        - Text quality (grammar, vocabulary, content) → 0-100
        - Pronunciation (audio vs text comparison) → 0-100
        - Pass criteria: text >= 70 AND audio >= 60
        
        Provide detailed feedback with corrections.
        """
        
        return self.gemini_api.evaluate(prompt)

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

## **7. IMPLEMENTATION ROADMAP (12 Months - 52 Weeks)**

### **Phase 1: Foundation (Weeks 1-4)**

**Week 1: Environment Setup**

* Python 3.11+ kurulumu  
* Virtual environment oluştur  
* Dependencies yükle:

```bash
pip install fastapi uvicorn[standard] python-multipart python-dotenv google-generativeai
pip install openai-whisper gTTS
pip install sqlalchemy sounddevice scipy

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

```bash
# .env
GEMINI_API_KEY=your_api_key_here
DATABASE_PATH=./data/student.db
WHISPER_MODEL_PATH=./models/ggml-medium.bin
```

---

## **13. SIGN-OFF**

**Project Owner:** [Fikret Uzgan]  
**Version:** 2.0 (Updated for Fixed Curriculum Approach)  
**Start Date:** 06.02.2026  
**Updated:** 12.02.2026  
**Target Completion:** 06.02.2027 (12 months, 52 weeks)  
**Status Update:** Fixed curriculum approach adopted - AI used for evaluation only (speaking/homework/exam feedback), not content generation. All 52 weeks of curriculum pre-authored in markdown files.
