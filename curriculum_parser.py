"""
Curriculum Parser - Loads lessons directly from NEW_CURRICULUM_REDESIGNED format
No AI generation - pure parsing of pre-written curriculum markdown files
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

REDESIGNED_CURRICULUM_DIR = Path(__file__).parent / "Research" / "NEW_CURRICULUM_REDESIGNED"

# CEFR levels for each week
WEEK_LEVELS = {
    1: "A1.1", 2: "A1.1", 3: "A1.1", 4: "A1.1", 5: "A1.2",
    6: "A1.2", 7: "A1.2", 8: "A1.2", 9: "A2.1", 10: "A2.1",
    11: "A2.1", 12: "A2.1", 13: "A2.2", 14: "A2.2", 15: "A2.2",
    16: "A2.2", 17: "B1.1", 18: "B1.1", 19: "B1.1", 20: "B1.1",
    21: "B1.2", 22: "B1.2"
}

def get_level_for_week(week: int) -> str:
    """Get CEFR level for a given week."""
    return WEEK_LEVELS.get(week, "A1.1")


def load_redesigned_curriculum_day(week: int, day: int) -> Dict[str, Any]:
    """
    Load a single day's lesson directly from the redesigned curriculum.
    
    Args:
        week: Week number (1-52)
        day: Day within week (1-5)
    
    Returns:
        Dictionary with lesson content
    """
    level = get_level_for_week(week)
    
    # Calculate absolute day number in curriculum
    # Week 1 = Days 1-5, Week 2 = Days 6-10, Week 9 = Days 41-45, etc.
    absolute_day = (week - 1) * 5 + day
    
    # Determine filename (Week_X_A1.X.md)
    filename = f"Week_{week}_{level}.md"
    filepath = REDESIGNED_CURRICULUM_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Curriculum file not found: {filepath}")
    
    logger.info(f"Loading Week {week} Day {day} (absolute day {absolute_day}) from {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the DAY section using absolute day number
    day_pattern = rf"## DAY {absolute_day}\s*[-–—]\s*([^\n]+).*?(?=## DAY|\Z)"
    day_match = re.search(day_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not day_match:
        raise ValueError(f"Day {absolute_day} not found in Week {week} curriculum (file: {filename})")
    
    day_content = day_match.group(0)
    
    # Parse components
    lesson_id = f"week_{week}_day_{day}"
    grammar = parse_grammar_section(day_content)
    vocabulary = parse_vocabulary_section(day_content)
    examples = parse_examples_section(day_content)
    speaking = parse_speaking_prompt(day_content, vocabulary)
    
    return {
        'lesson_id': lesson_id,
        'week': week,
        'day': day,
        'level': level,
        'theme': f"Week {week} - Day {day}",
        'grammar': grammar,
        'vocabulary': vocabulary,
        'examples': examples,
        'speaking': speaking,
        'homework': {
            'prompt': f"Complete the exercises from Day {day} of Week {week}"
        },
        'quiz': {
            'questions': parse_quiz_questions(examples)
        },
        'is_curriculum': True
    }


def parse_grammar_section(day_content: str) -> Dict[str, Any]:
    """Extract grammar explanation from DAY section."""
    pattern = r"### GRAMMAR SECTION.*?(?=### VOCABULARY|### EXAMPLES|\Z)"
    match = re.search(pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {'explanation': 'No grammar section found'}
    
    section = match.group(0)
    
    # Extract explanation paragraphs (everything from "#### Explanation" to the next ### section or end)
    explanation_pattern = r"#### Explanation(.*?)(?=\n###|\Z)"
    exp_match = re.search(explanation_pattern, section, re.DOTALL)
    
    explanation = ""
    if exp_match:
        # Get ALL content from Explanation section (full curriculum content)
        text = exp_match.group(1).strip()
        # Remove markdown separators (---, ***, ___) that might appear at the end
        text = re.sub(r'\n+\s*(?:---|___|\*\*\*)\s*\n*$', '', text)
        # Don't limit paragraphs - return everything in the explanation
        explanation = text

    # #region agent log
    try:
        import json as _json
        from pathlib import Path as _Path
        _logpath = _Path(__file__).resolve().parent / ".cursor" / "debug.log"
        _logpath.parent.mkdir(parents=True, exist_ok=True)
        _log = {"id": "grammar_parser", "timestamp": __import__("time").time() * 1000, "location": "curriculum_parser.parse_grammar_section", "message": "explanation after parse", "data": {"len": len(explanation), "tail": explanation[-250:] if len(explanation) > 250 else explanation, "has_leaving": "I'm leaving" in explanation or "leaving" in explanation[-100:]}, "hypothesisId": "A"}
        with open(_logpath, "a", encoding="utf-8") as _f:
            _f.write(_json.dumps(_log, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # #endregion

    return {
        'explanation': explanation,
        'full_section': section  # Store full section (no truncation)
    }


def parse_vocabulary_section(day_content: str) -> List[Dict[str, str]]:
    """Extract vocabulary words from DAY section."""
    pattern = r"### VOCABULARY.*?(?=### EXAMPLES|---|\Z)"
    match = re.search(pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return []
    
    section = match.group(0)
    
    # Find word blocks (Word 1: ..., Word 2: ..., etc.)
    word_pattern = r"\*\*Word \d+:\s*([^*]+)\*\*.*?(?=\*\*Word|\Z)"
    word_matches = re.finditer(word_pattern, section, re.DOTALL)
    
    words = []
    for word_match in word_matches:
        word_block = word_match.group(0)
        
        # Extract word name
        name_match = re.search(r"Word \d+:\s*([^*\n]+)", word_block)
        word_name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract definition/translation
        english_match = re.search(r"English:\s*([^\n]+)", word_block)
        english = english_match.group(1).strip() if english_match else ""
        
        # Extract example sentence
        example_match = re.search(r"\*\*Example sentence:\*\*\s*([^\n]+(?:\n[^\n]*)?)", word_block)
        example = example_match.group(1).strip() if example_match else ""
        
        words.append({
            'word': word_name,
            'english': english,
            'example': example
        })
    
    return words


def parse_examples_section(day_content: str) -> List[Dict[str, str]]:
    """Extract example sentences and exercises."""
    pattern = r"### EXAMPLES.*?(?=\n###|---|\Z)"
    match = re.search(pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return []
    
    section = match.group(0)
    
    # Extract numbered examples (format: "1. French sentence (English translation)")
    example_pattern = r"^\s*\d+\.\s+(.+?)(?=^\s*\d+\.|\n---|\Z)"
    examples = []
    
    for ex_match in re.finditer(example_pattern, section, re.MULTILINE | re.DOTALL):
        content = ex_match.group(1).strip()
        if content:
            examples.append({
                'content': content,
                'text': content
            })
    
    return examples


def parse_speaking_prompt(day_content: str, vocabulary: List[Dict]) -> Dict[str, Any]:
    """Create a speaking prompt based on day content and vocabulary."""
    # Extract first vocabulary word for context
    vocab_words = [v['word'] for v in vocabulary[:3]]
    
    return {
        'prompt': f"Practice pronouncing these words: {', '.join(vocab_words)}",
        'scenario': 'Vocabulary pronunciation practice',
        'example_response': f"Repeat each word clearly: {vocab_words[0] if vocab_words else 'bonjour'}"
    }


def parse_quiz_questions(examples: List[Dict]) -> List[Dict[str, str]]:
    """Extract quiz questions from examples."""
    quiz_qs = []
    
    for i, example in enumerate(examples[:10]):  # Use first 10 examples as quiz base
        quiz_qs.append({
            'id': f"q_{i+1}",
            'question': f"Exercise {i+1}",
            'type': 'exercise'
        })
    
    return quiz_qs


def load_all_weeks_metadata() -> List[Dict[str, Any]]:
    """Get metadata for all available weeks in curriculum."""
    weeks = []
    
    for week_num in range(1, 53):
        level = get_level_for_week(week_num)
        weeks.append({
            'week': week_num,
            'level': level,
            'title': f'Week {week_num} - {level}'
        })
    
    return weeks
