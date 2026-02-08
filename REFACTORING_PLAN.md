# Code Refactoring Plan - Breaking Down Large Files

## Overview
Refactoring large files into logical, focused modules for better maintainability and performance.

## Files to Refactor

### 1. main.py (1850 lines) → 4 files

**Structure:**
```
main.py (core app + imports)
├── api_models.py (all Pydantic models)
├── api_helpers.py (helper functions)
├── api_routes/
│   ├── __init__.py
│   ├── lessons.py (lesson endpoints)
│   ├── vocabulary.py (vocabulary endpoints)
│   ├── homework.py (homework endpoints)
│   ├── speaking.py (speaking endpoints)
│   ├── exams.py (exam endpoints)
│   ├── audio.py (audio/TTS endpoints)
│   └── settings.py (settings/mode endpoints)
```

**Benefits:**
- Easier to locate and modify specific endpoints
- Clearer separation of concerns
- Faster IDE indexing
- Easier testing of specific features

### 2. db.py (1456 lines) → 6 files

**Structure:**
```
db_core.py (connection management, schema)
├── db_lessons.py (lesson and progress operations)
├── db_homework.py (homework submissions and feedback)
├── db_exams.py (exam management)
├── db_srs.py (SRS scheduling and vocabulary)
└── db_utils.py (shared utilities, settings)
```

**Benefits:**
- Each domain has one focused file
- Easier to understand data relationships
- Faster to implement new features per domain
- Clearer API boundaries

### 3. app.js (1680 lines) → 6 files

**Structure:**
```
app.js (core initialization + tab management)
├── app-core.js (utilities, mode checking, setup)
├── app-lessons.js (lesson generation and display)
├── app-vocab.js (vocabulary practice)
├── app-speaking.js (speaking practice)
├── app-homework.js (homework submission)
└── app-exams.js (quiz/exam display and submission)
```

**Benefits:**
- Features are self-contained
- Easier to test individual features
- Clear dependencies between modules
- Faster page load (can lazy-load modules)

### 4. style.css (1408 lines) → 3 files

**Structure:**
```
style.css (imports all others)
├── style-layout.css (grid, flexbox, container layouts)
├── style-components.css (buttons, cards, forms)
├── style-responsive.css (media queries, mobile)
└── style-animations.css (transitions, keyframes)
```

**Benefits:**
- Easy to locate styling for specific components
- Responsive styles in one place
- Animations grouped together
- Faster CSS parsing (smaller files)

## Implementation Order

1. ✅ **api_models.py** - Extract all Pydantic models from main.py
2. ✅ **api_helpers.py** - Extract all helper functions from main.py
3. ✅ **db_core.py** - Extract connection and init from db.py
4. ✅ **Other db_*.py files** - Split db.py by domain
5. ✅ **style-*.css files** - Split style.css by feature
6. ✅ **app-*.js files** - Split app.js by feature
7. ✅ **api_routes/** - Move endpoints to separate files
8. Update **main.py** - Import from new modules

## Migration Checklist

- [ ] Create new files with content
- [ ] Update imports in main files
- [ ] Test all endpoints work correctly
- [ ] Verify no circular imports
- [ ] Check browser console for JS errors
- [ ] Validate CSS still loads correctly
- [ ] Update IDE project structure
- [ ] Commit changes to version control

## Expected Outcome

**Before:**
- 4 large files (5,794 total lines)
- Hard to navigate
- IDE sluggish
- Difficult to test individual features
- High merge conflict risk

**After:**
- 20 focused files (5,794 total lines, but organized)
- Easy navigation (Ctrl+F over small file)
- IDE responsive
- Individual feature testing possible
- Lower merge conflict risk
- Clearer code ownership

## Notes

- Maintain exact same functionality - only reorganizing code
- Keep all external APIs unchanged  
- Update import statements in consuming files
- Consider creating __init__.py files for packages
- May add utility functions during reorganization
