# Known Issues - End of Session 3 (Feb 8, 2026)

## Status: INCOMPLETE - Multiple Critical Issues Remaining

---

## CRITICAL ISSUES (Blocking Features)

### 1. **Speaking Practice Causes Gemini API Error**
- **Error**: `module 'google.generativeai' has no attribute 'Client'`
- **Location**: When user clicks "Open Speaking Practice" button in lesson
- **Root Cause**: Incorrect import or version mismatch with google-generativeai library
- **Current Behavior**: Error appears, feature unusable
- **Affects**: Speaking practice tab completely broken
- **Fix Required**: 
  - Check main.py imports for google.generativeai
  - Verify API client initialization method
  - Use correct client API (likely `genai.GenerativeModel()` not `genai.Client()`)
- **Priority**: 🔴 CRITICAL

### 2. **Speaking Practice Not Embedded in Lesson Modal**
- **Current Behavior**: Opens separate speaking tab (if it worked)
- **Expected**: Should open within/alongside the lesson modal, not replace it
- **User Journey Broken**: No way to return to lesson after jumping to speaking tab
- **Fix Required**: 
  - Keep lesson modal open
  - Show speaking practice as overlay or side panel
  - Add "Back to Lesson" button on speaking practice
  - Add "to Speaking Practice" button that doesn't close lesson
- **Priority**: 🔴 CRITICAL

### 3. **Quiz Still Shows 0/5 Score Even with Correct Answers**
- **Reported**: "Score is 0/5 even when I answer correctly"
- **Likely Cause**: Quiz validation rewrite may have missed edge cases
- **Affects**: Quiz grading completely broken
- **Testing Notes**: 
  - Tested with: "Je suis turc" (correct answer)
  - Multiple choice and text answers both report 0/5
  - Correct answers ARE shown in review (that part works)
  - Scoring logic not correctly identifying correct answers
- **Debug Required**: 
  - Add console logging to submitQuiz() function
  - Check answer comparison logic
  - Verify question.correct_answer format from AI
  - Test both formats (index-based and string-based)
- **Priority**: 🔴 CRITICAL

### 4. **Audio-Based Quiz Questions Not Implemented**
- **Reported**: "Audio question is not there. No listen button for audio-based question"
- **Issue**: Quiz questions should have audio option to listen before answering
- **Current**: Text-only questions
- **Missing Features**:
  - Play audio of multiple choice options
  - Listen button for question text itself
  - Ability to replay audio
- **Implementation Needed**: Add `playLessonTTS()` calls to quiz options
- **Priority**: 🟡 HIGH (Feature request, not blocking)

---

## MAJOR ISSUES (Features Not Working Properly)

### 5. **Grammar Explanations Still Shallow**
- **Reported**: "Grammar did not improve same single sentence"
- **Current Output Example**: 
  ```
  "Avoir" means "to have". It is used for age: J'ai + number + ans = I am ... years old.
  ```
- **Expected Output**: 3-5 paragraphs with:
  - Detailed explanation of usage
  - Full conjugation table (je, tu, il/elle/on, nous, vous, ils/elles)
  - 6-8 examples covering all forms
  - Key rules and patterns
- **Root Cause**: AI not following enhanced prompt instructions
- **Why AI Example Didn't Help**: 
  - Example format provided may not match what AI generates
  - May need different prompt phrasing
  - AI model may be truncating output
  - Lesson might be cached from old generation
- **Fixes to Try**:
  - Make grammar requirements even MORE explicit in prompt
  - Try adding "Generate AT LEAST 500 words for grammar" requirement
  - Add JSON structure requirements (min/max lengths)
  - Test with fresh lesson generation (delete old cache)
  - Break grammar into sections with explicit word count requirements
- **Priority**: 🔴 CRITICAL (Core feature)

### 6. **Vocabulary Cards - 2 Items Missing Listen Button**
- **Reported**: "Again 2 items missing listening function in vocabulary but in different location"
- **Pattern**: Inconsistent - different items affected than before
- **Previous Location**: "je m'appelle", "comment t'appelles-tu" 
- **Current Location**: Unknown (need to check new lesson)
- **Root Cause**: Variable vocabulary structure from AI generation
- **Most Likely**: 
  - AI generating some vocab items without `word` property
  - Items have `front` property but parser doesn't catch it
  - Empty or null text values
  - Special characters or formatting breaking parser
- **Debug Steps**:
  - Log all vocabulary items to console
  - Check exact JSON structure for problematic items
  - Verify parser handles all edge cases
  - Add more fallback properties
- **Code Location**: `createInteractiveVocabulary()` in static/app.js (lines 1362-1437)
- **Priority**: 🟡 HIGH (User experience affected)

### 7. **Grammar Sentences Lack Listen Button**
- **Confusion Note**: Not sure what this means from user
- **Possible Interpretation**: 
  - Grammar explanation examples should have TTS?
  - Or conjugation examples need audio playback?
- **Needs Clarification**: What does user expect to hear?
- **Current State**: Grammar examples are text-only
- **Potential Fix**: Add "Listen to pronunciation" button for grammar examples
- **Priority**: 🟡 MEDIUM (Clarification needed)

---

## MINOR ISSUES (Polish/Enhancement)

### 8. **Quiz Display Still Shows Multiple Forms**
- **Reported**: Was supposed to hide answer forms in question text
- **Example**: "Form a question: Are you a student? → Es-tu étudiant ? / Tu es étudiant ?"
- **Status**: May or may not be fixed (depends on new AI generation)
- **Confirmation Needed**: Generate new lesson and check quiz format
- **Priority**: 🟡 HIGH (If still appearing)

### 9. **Back Button Sometimes Grayed Out**
- **Reported**: "Back button is grayed out but it should not be"
- **Current Code**: 
  ```javascript
  ${lessonState.currentSection === 0 ? 'disabled' : ''}
  ```
- **Status**: Appears correct in code, may be fixed now
- **Confirmation Needed**: Test by going Back from section 1
- **Priority**: 🟢 LOW (Likely already fixed)

---

## UNRESOLVED ITEMS FROM PREVIOUS SESSIONS

These were mentioned but not fully addressed:

### 10. **First-Time User Flow**
- First visit should show tutorial/setup modal
- App setup/level selection not tested

### 11. **Performance**
- Large lessons might be slow
- No optimization for slow connections

### 12. **Error Handling**
- No graceful fallbacks when Gemini API fails
- No offline mode

---

## NEXT SESSION ACTION ITEMS

### Immediate (Session 4)

**Priority 1 - Fix Quiz Scoring:**
```
1. Add debug logging to submitQuiz():
   - Log all questions parsed
   - Log all student answers collected
   - Log comparison for each question
   - Log final score calculation

2. Test with known correct/incorrect answers
3. Check question.correct_answer format from actual lesson JSON
4. Verify answer collection for both radio inputs and text inputs
```

**Priority 2 - Fix Speaking Practice Error:**
```
1. Check main.py imports:
   - Find: import google.generativeai
   - Verify correct client initialization
   - May need: genai.configure(api_key=...) + genai.GenerativeModel()
   
2. Wrap speaking practice in try/except
3. Embed practice within lesson modal (don't close lesson)
4. Add return path to lesson
```

**Priority 3 - Improve Grammar Generation:**
```
1. Update ai_prompts.py further:
   - Add explicit min/max length requirements
   - Break grammar into required sections
   - Add "MUST BE AT LEAST 500 CHARACTERS" for explanation
   - Add section headers in template
   
2. Delete cached lessons and regenerate
3. Verify output quality before accepting
```

**Priority 4 - Fix Remaining Vocab Issues:**
```
1. Generate new lesson
2. Log vocab parser output to console
3. Identify exact structure of problematic items
4. Add additional fallback properties if needed
```

### Medium Priority (Session 4-5)

- [ ] Add audio playback to quiz questions
- [ ] Add listen buttons to grammar examples
- [ ] Quiz question format verification (no answer revelation)
- [ ] Test homework submission with dynamic lessons
- [ ] Test SRS vocabulary scheduling

### Investigation Needed

- [ ] Why AI grammar not responding to prompt improvements
- [ ] Why vocabulary items have inconsistent structure
- [ ] Google Generative AI client compatibility issues
- [ ] Quiz correct_answer format from Gemini API

---

## Testing Checklist for Next Session

- [ ] Generate fresh lesson (Week 1, Day 1)
- [ ] Check grammar: >500 words, all conjugations
- [ ] Check vocabulary: ALL items have Listen button
- [ ] Check quiz: Score >0 when answering correctly
- [ ] Check speaking practice: Opens, has no error, doesn't break lesson flow
- [ ] Check back button: Not grayed out inappropriately
- [ ] Test quiz submission: Correct answers display after

---

## Code References

**Files Needing Investigation:**
- `main.py` - Google Generative AI client setup (line ~?)
- `static/app.js` - submitQuiz() function (lines 1572-1728)
- `static/app.js` - createInteractiveVocabulary() (lines 1362-1437)
- `ai_prompts.py` - LESSON_GENERATION_PROMPT (line 40+)

**API Endpoints to Check:**
- `POST /api/lessons/generate` - Verify response structure
- `POST /api/speaking/evaluate` - Has error with google client

---

## Session Summary

**Completed:**
- ✅ Removed redundant UI buttons
- ✅ Fixed quiz validation logic (partially - scoring still broken)
- ✅ Improved vocab parsing (partially - 2 items still failing)
- ✅ Enhanced AI prompts (grammar not responding to improvements)
- ✅ Improved speaking practice navigation (partially - now has error)

**Not Completed:**
- ❌ Grammar explanations remain shallow
- ❌ Quiz scoring shows 0/5
- ❌ Speaking practice has Gemini API error
- ❌ Speaking practice not embedded in lesson
- ❌ Audio quiz questions missing
- ❌ Vocabulary still has 2 items without listening

**Root Causes Identified:**
- AI model not following enhanced prompt instructions
- Google Generative AI client initialization error
- Vocabulary structure inconsistency from AI generation
- Quiz validation edge cases not covered

**Recommendation:**
Debug quiz scoring and speaking practice error first in next session. These are blocking core features.
