"""
Load sample lesson into database
"""
import json
from pathlib import Path
import db

# Load sample lesson
lesson_path = Path("data/sample_lesson_a2.json")
with open(lesson_path, "r", encoding="utf-8") as f:
    lesson_data = json.load(f)

# Convert to database format
lesson_id = "a2_1_imparfait_passe_compose"

# Save lesson using existing schema
db.save_lesson(
    lesson_id=lesson_id,
    level=lesson_data["level"],
    theme=lesson_data["theme"],
    week_number=1,
    grammar_explanation=json.dumps(lesson_data["grammar"], ensure_ascii=False),
    vocabulary=json.dumps(lesson_data["vocabulary"], ensure_ascii=False),
    speaking_prompt=json.dumps(lesson_data["speaking"], ensure_ascii=False),
    homework_prompt=lesson_data["homework"],
    quiz_questions=json.dumps(lesson_data["quiz"], ensure_ascii=False)
)

# Initialize progress tracking
db.init_lesson_progress(lesson_id)

print(f"✅ Sample lesson '{lesson_id}' loaded successfully!")
print(f"   Level: {lesson_data['level']}")
print(f"   Theme: {lesson_data['theme']}")
