# Yeni Müfredat Sistemi Test Kılavuzu

## 🚀 Programı Başlatma

### 1. Sunucuyu Başlatın
```powershell
# Terminal'de:
uvicorn main:app --reload --port 8000
```

VEYA VS Code'da:
```
Tasks → Start FastAPI server
```

### 2. Tarayıcıda Açın
```
http://localhost:8000
```

---

## 🧪 Test Adımları

### Test 1: Week 1 Day 1 - Verb Être
1. **Lessons** sekmesine gidin
2. **Week** dropdown'dan `Week 1` seçin
3. **Day 1** butonuna tıklayın
4. **Load Lesson** butonuna tıklayın

**Beklenen Sonuç:**
- ✅ Lesson yüklenir (AI değil, FIXED content)
- ✅ Grammar Section görünür: 5-paragraph açıklama
  - **Paragraph 1:** Definition (Être nedir?)
  - **Paragraph 2:** Formation (Conjugation table)
  - **Paragraph 3:** Common Patterns (Use cases)
  - **Paragraph 4:** Real-World Dialogues (2 örnek sahne)
  - **Paragraph 5:** Common Errors (❌ → ✅)

- ✅ Vocabulary Section: 5 kelime
  - **Bonjour** - Hello (/bon-zhoor/)
  - **Je** - I (/zhuh/)
  - **Être** - To be (/eh-truh/)
  - **Français/Française** - French
  - **Et** - And
  - Her kelime **example sentence** ile gösterilir

- ✅ Quiz Section: 8-10 soru (50'den rastgele)
  - Her soru **content identifiers** ile:
    - `[listening, dialogue]`
    - `[conjugation, fill_blank]`
    - `[reading, comprehension]`
  - Sorular her defasında farklı (random selection)

---

### Test 2: Week 1 Day 2 - Être Plural Forms
1. Week 1 seçili kalsın
2. **Day 2** butonuna tıklayın
3. **Load Lesson** tıklayın

**Beklenen Sonuç:**
- Grammar: Nous sommes, Vous êtes, Ils/Elles sont
- Vocabulary: 5 YENİ kelime (cumulative: 10 kelime)
- Quiz: Farklı 8-10 soru

---

### Test 3: Week 2 Day 1 - Regular -IR Verbs
1. **Week** dropdown → `Week 2`
2. **Day 1** tıklayın
3. **Load Lesson**

**Beklenen Sonuç:**
- Grammar: Finir, Choisir conjugations
- Content identifiers: Yeni tiplerde sorular (verb conjugation focus)

---

## 📚 Müfredat Kapsamı

### Şu An Hazır Olan Haftalar:
- ✅ Week 1 (A1.1) - Days 1-5: Être, Avoir, -ER verbs
- ✅ Week 2 (A1.1) - Days 6-10: -IR/-RE verbs, negation, questions
- ✅ Week 3 (A1.1) - Days 11-15: Gender, number, adjectives
- ✅ Week 4 (A1.1) - Days 16-20: Questions, negation, imperatives
- ✅ Week 5 (A1.2) - Days 21-25: Passé Composé (avoir)
- ✅ Week 6 (A1.2) - Days 26-30: Passé Composé (être)
- ✅ Week 7 (A1.2) - Days 31-35: Futur Proche

**Total:** 7 weeks × 5 days = **35 lessons** ✅

---

## 🔍 Content Identifiers Listesi

Programda görünecek soru tipleri:

### Grammar Practice
- `conjugation` - Fiil çekimi soruları
- `fill_blank` - Boşluk doldurma
- `agreement` - Cinsiyet/sayı uyumu
- `word_order` - Kelime sırası

### Vocabulary
- `vocabulary` - Kelime tanıma
- `semantic_field` - İlgili kelimeler

### Reading
- `reading` - Okuma anlama
- `reading_comprehension` - Detaylı anlama soruları

### Listening
- `listening` - Dinleme soruları
- `listen_identify` - Ses ile tanıma
- `listen_gist` - Ana fikir

### Speaking
- `speaking` - Konuşma pratiği
- `dialogue_production` - Diyalog oluşturma
- `pronunciation_drill` - Telaffuz

### Writing
- `writing` - Yazma pratiği
- `sentence_construction` - Cümle kurma
- `translation` - Çeviri

---

## 🎯 Yeni Sistemin Avantajları

### 1. FIXED Content (AI Yok)
- ✅ Gramer açıklamaları her zaman aynı kalitede
- ✅ Vocabulary örnekleri elle yazılmış
- ✅ Quiz soruları test edilmiş
- ✅ API hatası yok, token limiti yok

### 2. Content Identifiers
- ✅ Her soru tipi etiketlenmiş
- ✅ Çeşitlilik garantili (listening + reading + grammar mix)
- ✅ Analiz mümkün: "Kullanıcı hangi soru tipinde zayıf?"

### 3. Scalable
- ✅ 50 soru/gün pool (8-10 gösterilir)
- ✅ Her defasında farklı sorular
- ✅ Tekrar yok (veya çok az)

### 4. Gramer Kalitesi
- ✅ 5-paragraph format (Babbel style)
  - Definition
  - Formation (tables)
  - Common Patterns
  - Real-World Examples
  - Common Errors

---

## 🐛 Olası Hatalar ve Çözümler

### Hata: "Curriculum file not found for Week X Day Y"
**Sebep:** Week 8+ henüz yazılmadı
**Çözüm:** Sadece Week 1-7 test edin

### Hata: "Grammar explanation not available"
**Sebep:** Curriculum dosyasında GRAMMAR SECTION yok
**Çözüm:** Curriculum dosyasını kontrol edin (### GRAMMAR SECTION başlığı var mı?)

### Hata: Quiz questions boş
**Sebep:** EXAMPLES SECTION parse edilemedi
**Çözüm:** quiz_parser.py log'larına bakın

---

## 📊 Database Schema (Gelecek İçin)

Content identifiers için database eklentileri:

```sql
-- Lessons tablosuna ekle:
ALTER TABLE lessons ADD COLUMN content_identifiers TEXT;  -- JSON array

-- Lesson progress'e ekle:
ALTER TABLE lesson_progress ADD COLUMN shown_questions TEXT;  -- JSON: [1, 5, 12, ...]

-- Weakness tracking (content identifier bazlı):
CREATE TABLE content_weaknesses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    content_identifier TEXT,  -- 'conjugation', 'listening', etc.
    accuracy REAL,  -- 0.0 - 1.0
    total_attempts INTEGER,
    last_practiced TEXT
);
```

---

## ✨ Sonraki Adımlar

1. **Week 8-52 müfredatını tamamlayın** (aynı format)
2. **Quiz display UI'ını geliştirin** - Content identifier badge'leri gösterin
3. **Speaking tier evaluation** - Tier 1/2/3 prompts
4. **Homework system** - Text + audio submission ve AI grading
5. **Monthly exams** - DELF-aligned comprehensive tests

---

## 🎓 Kullanım Örnekleri

### Ders Görünümü:

```
╔════════════════════════════════════════════════════════╗
║  WEEK 1 DAY 1 - Verb Être (I am, You are)            ║
║  Level: A1.1 | Duration: 30 minutes | Speaking Tier: 1║
╚════════════════════════════════════════════════════════╝

📖 GRAMMAR SECTION
─────────────────────────────────────────────────────────
1. Definition: What is Être?
   The verb être means "to be" in English...

2. Formation & Basic Conjugation
   ┌─────────┬──────┬─────────┬────────────────┐
   │ Pronoun │ Être │ English │ Example        │
   ├─────────┼──────┼─────────┼────────────────┤
   │ je      │ suis │ I am    │ Je suis Marie  │
   │ tu      │ es   │ you are │ Tu es français │
   └─────────┴──────┴─────────┴────────────────┘

📝 VOCABULARY (5 WORDS)
─────────────────────────────────────────────────────────
1. Bonjour (bon-zhoor) - Hello
   "Bonjour! Comment ça va?" (Hello! How are you?)

2. Je (zhuh) - I
   "Je suis Marie." (I am Marie.)

❓ QUIZ (8 questions from pool of 50)
─────────────────────────────────────────────────────────
Q1. [listening, dialogue, gist] 🎧
    Audio: "Bonjour! Je suis Marie."
    Task: What is the person's name?
    → Answer: _________

Q2. [conjugation, fill_blank] ✍️
    Je _____ Pierre. (I am Pierre.)
    → Answer: _________
```

---

## 🎉 Tebrikler!

Yeni müfredat sistemi hazır ve çalışıyor! 

Şimdi Week 8-52'yi yazmaya devam edebilir veya programı test edebilirsiniz.

**Not:** Gramer açıklamaları ve kelimeler elle yazılmış (AI yok), bu yüzden:
- ✅ Kalite tutarlı
- ✅ Token limiti yok
- ✅ Maliyet yok
- ✅ Hız garanti
