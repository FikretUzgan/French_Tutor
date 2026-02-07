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
  5. **AI response:** Text feedback + suggestions
  6. **TTS playback:** Piper reads AI response aloud
  7. **Retry allowed:** Student can attempt again with new scenario or same
  
* **Key Design Decisions:**
  * **No audio sent to AI:** Only STT transcription sent (saves tokens on free tier)
  * **Local STT/TTS:** Whisper.cpp + Piper run locally (no API costs)
  * **Interactive, not evaluative:** Not stored in database, just practice
  * **Immediate feedback:** Real-time text + voice response
  * **Multiple attempts:** Students can retry scenarios until satisfied
  
* **Difference from Homework Audio:**
  * Speaking practice: STT → text → AI (text-based conversation)
  * Homework audio: Raw audio stored + STT comparison for pronunciation scoring
  
* **UI Pattern:**
  * Push-to-talk button (hold to record, release to stop)
  * Transcription displayed in real-time
  * AI response shown as text + spoken via TTS
  * "Try again" button for retry

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

sql  
vocabulary (  
    id, word, translation, example\_sentence,  
    level, learned\_date, last\_review\_date,  
    review\_count, success\_rate, next\_review\_date  
)  
\`\`\`

\---

\#\#\# 2.6 Content Recommendations

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
\- \*\*NFR-003:\*\* TTS (Piper) ses üretimi \< 1 saniye

\#\#\# 3.2 Usability  
\- \*\*NFR-010:\*\* Streamlit web arayüzü  
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
│              FRONTEND (Streamlit)                   │  
│  ┌─────────────┬─────────────┬──────────────┐      │  
│  │ Ders Ekranı │ Sınav Ekranı│ Rapor Ekranı │      │  
│  └─────────────┴─────────────┴──────────────┘      │  
└───────────────────┬─────────────────────────────────┘  
                    │  
┌───────────────────▼─────────────────────────────────┐  
│           BUSINESS LOGIC (Python)                   │  
│  ┌──────────────────────────────────────────┐      │  
│  │   LessonPlanner (LangGraph Agent)        │      │  
│  │   ExamGenerator (Dynamic Questions)      │      │  
│  │   PerformanceAnalyzer (Weakness Tracker) │      │  
│  │   HomeworkManager (Mandatory Checks)     │      │  
│  └──────────────────────────────────────────┘      │  
└───────────────────┬─────────────────────────────────┘  
                    │  
    ┌───────────────┼───────────────┬────────────────┐  
    │               │               │                │  
┌───▼────┐    ┌────▼─────┐   ┌────▼────┐    ┌──────▼──────┐  
│ Gemini │    │ Whisper  │   │  Piper  │    │   SQLite    │  
│  API   │    │   STT    │   │   TTS   │    │  \+ChromaDB  │  
│ (Free) │    │ (Lokal)  │   │ (Lokal) │    │   (Lokal)   │  
└────────┘    └──────────┘   └─────────┘    └─────────────┘

### **4.2 Technology Stack**

| Component | Technology | Justification |
| ----- | ----- | ----- |
| Frontend | Streamlit | Hızlı prototip, Python entegrasyonu |
| AI Agent | LangGraph \+ Gemini 2.0 Flash | Multi-agent orchestration |
| STT | Whisper.cpp (medium model) | Lokal, hızlı, Fransızca destekli |
| TTS | Piper (fr\_FR-siwis-medium) | Doğal ses, hızlı |
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
    \- Weak topics  
    \- Already learned vocabulary  
    """  
      
    def generate\_lesson(self, user\_id, level):  
        \# 1\. Get user's weak topics  
        weak\_topics \= self.db.get\_weak\_topics(user\_id)  
          
        \# 2\. Get learned vocabulary  
        learned\_vocab \= self.db.get\_vocabulary(user\_id)  
          
        \# 3\. Get curriculum for this level  
        curriculum \= self.load\_curriculum(level)  
          
        \# 4\. Generate lesson with Gemini  
        prompt \= f"""  
        You are a strict French teacher.  
        Student level: {level}  
        Weak topics: {weak\_topics}  
        Learned words: {len(learned\_vocab)}  
          
        Create today's lesson:  
        1\. Grammar topic (compare with English)  
        2\. 3 new vocabulary words (not in: {learned\_vocab})  
        3\. Speaking scenario (daily life or role-play)  
        4\. 1 homework assignment  
          
        Return JSON format.  
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
 pip install streamlit langchain langgraph google-generativeai  
  pip install whisper-cpp-python piper-tts  
  pip install chromadb sqlalchemy sounddevice scipy

* Proje klasör yapısı oluştur  
* Git repo başlat

**Week 2: STT/TTS Integration**

* Whisper.cpp medium model indir  
* Piper fr\_FR model indir  
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

* Streamlit tema özelleştirme  
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

---

## **10\. FUTURE ENHANCEMENTS (Post-MVP)**

* Mobile app (React Native)  
* Multiplayer mode (leaderboard)  
* Native speaker video integration  
* C1-C2 levels  
* Other languages (Spanish, German)  
* Premium features (live tutoring)

---

## **11\. APPENDIX**

### **11.1 Quick Start Commands**

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
streamlit run app.py

### **11.2 Environment Variables**

bash  
\# .env  
GEMINI\_API\_KEY\=your\_api\_key\_here  
DATABASE\_PATH\=./data/student.db  
WHISPER\_MODEL\_PATH\=./models/ggml-medium.bin  
PIPER\_MODEL\_PATH\=./models/fr\_FR-siwis-medium  
---

## **12\. SIGN-OFF**

**Project Owner:** \[Fikret Uzgan\]  
 **Start Date:** 06.02.2026  
 **Target Completion:** 06.11.2026 (9 months)

