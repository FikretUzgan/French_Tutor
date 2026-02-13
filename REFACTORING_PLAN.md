# Refactoring Plan: Modularization & Optimization

## 1. Goal

Refactor the monolithic `main.py` and optimize core architectural components (DB, AI prompts) to improve maintainability, testing, and scalability. This plan is based on the recent code review.

## 2. Architecture Overview

### Current State

- **Monolithic**: `main.py` (>2000 lines) handles everything.
- **Scattered Prompts**: AI prompts embedded in string literals.
- **Inefficient DB**: New connection per query.

### Target State

```text
app/
├── main.py                 # App entry point (minimal)
├── routers/                # API Routes
│   ├── lessons.py
│   ├── vocabulary.py
│   └── ...
├── services/               # Business Logic
│   ├── ai_service.py       # Logic from lesson_generator.py
│   └── audio_service.py
└── core/                   # Infrastructure
    ├── database.py         # Connection pooling/context manager
    ├── config.py
    └── prompts.py          # Centralized prompts
```

## 3. Implementation Steps

### Phase 1: Foundation (Infrastructure)

1. **Create Directory Structure**: `routers/`, `services/`, `core/`.
2. **Centralize Config**: Move `load_dotenv` and env var loading to `core/config.py`.
3. **Database Layer**:
    - Create `core/database.py`.
    - Implement a context manager for DB connections to fix the "new connection per call" inefficiency.
    - Refactor `db_*.py` files to use this new context manager.

### Phase 2: Core Logic Extraction

4. **Prompts**: Extract all prompt strings from `main.py` and `lesson_generator.py` into `core/prompts.py`.
2. **Schemas**: Move Pydantic models from `main.py` to `core/schemas.py` (or `api_models.py` moved to `core/`).
3. **AI Service**:
    - Refactor `lesson_generator.py` into `services/ai_service.py`.
    - Create `services/audio_service.py` for Whisper/TTS logic.

### Phase 3: API Refactoring (The Split)

7. **Routers**: Break down `main.py` endpoints into:
    - `routers/lessons.py`
    - `routers/vocabulary.py`
    - `routers/homework.py`
    - `routers/speaking.py`
    - `routers/system.py` (health, mode, settings)
2. **Main Entry**: Clean up `main.py` to only import and include these routers.

### Phase 4: Modernization (Optional but Recommended)

9. **Dependency Injection**: Use FastAPI `Depends` for getting DB sessions and Services.
2. **Error Handling**: Implement global exception handlers in `main.py`.

## 4. Verification

- **Test Routes**: Verify critical paths (`/api/lessons`, `/api/health`) work after each router migration.
- **Check Database**: Ensure connections are correctly closed (no file lock errors).
- **AI Generation**: Confirm lesson generation still works with the moved logic.
