"""
Curriculum Loader Module

Handles parsing of curriculum markdown files from:
- New_Curriculum/ (old weekly format - DEPRECATED)
- Research/NEW_CURRICULUM_REDESIGNED/ (new daily format - PRIMARY)

NEW FORMAT (Redesigned):
- Files: Week_X_A1.X.md (e.g., Week_1_A1.1.md)
- Structure: Week overview + DAY 1-5 sections
- Each day: Metadata, Grammar (5-paragraph), Vocabulary (5 words), Examples (50 with content identifiers)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


CURRICULUM_DIR = Path(__file__).parent / "New_Curriculum"  # Old format
REDESIGNED_CURRICULUM_DIR = Path(__file__).parent / "Research" / "NEW_CURRICULUM_REDESIGNED"  # New format


def load_curriculum_file(week_number: int) -> Dict[str, Any]:
    """
    Load and parse a curriculum file for a given week.
    
    Args:
        week_number: Week number (1-52)
    
    Returns:
        Dictionary containing parsed curriculum data
    
    Raises:
        FileNotFoundError: If the curriculum file doesn't exist
        ValueError: If the file contains malformed content
    """
    # Determine filename (handle both wk1.md and Wk1.md naming conventions)
    filename = f"wk{week_number}.md"
    filepath = CURRICULUM_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Curriculum file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse all sections
    data = {
        'week_number': week_number,
        'filepath': str(filepath),
        'learning_outcomes': parse_learning_outcomes(content),
        'grammar_target': parse_grammar_target(content),
        'vocabulary_set': parse_vocabulary_set(content),
        'speaking_scenario': parse_speaking_scenario(content),
        'reading_listening': parse_reading_listening(content),
        'homework_task': parse_homework_task(content),
        'assessment_checkpoint': parse_assessment_checkpoint(content),
        'exam_rubric': parse_exam_rubric(content),
        'theme': parse_theme(content),
        'level': parse_level(content),
    }
    
    return data


def parse_level(content: str) -> str:
    """Extract CEFR level from first heading."""
    match = re.search(r"### .*CEFR Level\s+([A-B][12]\.[12])", content)
    if match:
        return match.group(1)
    # Fallback: try to extract from heading
    match = re.search(r"# Week\s+\d+.*?([A-B][12]\.[12])", content)
    if match:
        return match.group(1)
    return "A1.1"


def parse_theme(content: str) -> str:
    """Extract theme from heading."""
    match = re.search(r"# Week\s+\d+.*?\n\n\*\*Theme:\*\*\s+([^\n]+)", content)
    if match:
        return match.group(1).strip()
    return "General French"


def parse_learning_outcomes(content: str) -> List[str]:
    """
    Extract learning outcomes from the curriculum file.
    
    Returns:
        List of learning outcome strings
    """
    # Find the section with learning outcomes
    pattern = r"### Learning Outcomes.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return []
    
    outcomes_text = match.group(1)
    
    # Extract bullet points (lines starting with - or •)
    outcomes = []
    for line in outcomes_text.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('• '):
            outcome = line[2:].strip()
            if outcome:
                outcomes.append(outcome)
    
    return outcomes


def parse_grammar_target(content: str) -> Dict[str, Any]:
    """
    Extract grammar target information.
    
    Returns:
        Dictionary with 'form', 'complexity', 'prerequisites', 'scaffolding', 'examples'
    """
    pattern = r"### Grammar Target.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'form': 'Unknown',
            'complexity': 5,
            'prerequisites': [],
            'scaffolding': [],
            'examples': []
        }
    
    grammar_section = match.group(1)
    
    # Extract form
    form_match = re.search(r"\*\*Form:\*\*\s+([^\n]+)", grammar_section)
    form = form_match.group(1).strip() if form_match else "Unknown"
    
    # Extract complexity rating
    complexity_match = re.search(r"\*\*Complexity Rating:\*\*\s+(\d+)/10", grammar_section)
    complexity = int(complexity_match.group(1)) if complexity_match else 5
    
    # Extract prerequisites
    prereq_match = re.search(r"\*\*Prerequisite Knowledge:\*\*\s+([^\n]+)", grammar_section)
    prerequisites = [prereq_match.group(1).strip()] if prereq_match else []
    
    # Extract scaffolding steps
    scaffolding = []
    scaff_match = re.search(r"\*\*Scaffolding Steps:\*\*(.*?)(?=\n\n|\n###|\Z)", grammar_section, re.DOTALL)
    if scaff_match:
        scaff_text = scaff_match.group(1)
        # Extract numbered items
        for item in re.findall(r"^\d+\.\s+(.+?)(?=\n\d+\.|\Z)", scaff_text, re.MULTILINE | re.DOTALL):
            scaffolding.append(item.strip())
    
    # Extract examples (look for 6-8 realistic examples section)
    examples = []
    examples_match = re.search(r"6[-–—]+8 realistic examples:?\s*\n(.*?)(?=\n\n|\n###|\n\||\Z)", grammar_section, re.DOTALL)
    if examples_match:
        examples_text = examples_match.group(1)
        for line in examples_text.split('\n'):
            line = line.strip()
            if line and line.startswith('-'):
                example = line[1:].strip()
                if example:
                    examples.append(example)
    else:
        # Try alternative pattern for examples in bullet points
        for line in grammar_section.split('\n'):
            line = line.strip()
            if line.startswith('- ') and any(french_word in line.lower() for french_word in ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils']):
                example = line[2:].strip()
                if example and len(examples) < 8:
                    examples.append(example)
    
    return {
        'form': form,
        'complexity': complexity,
        'prerequisites': prerequisites,
        'scaffolding': scaffolding,
        'examples': examples
    }


def parse_vocabulary_set(content: str) -> List[Dict[str, str]]:
    """
    Extract vocabulary set (should have ~15-21 words with definitions).
    
    Returns:
        List of dicts with 'word' and 'definition' keys
    """
    pattern = r"### Vocabulary Set.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return []
    
    vocab_section = match.group(1)
    vocab_items = []
    
    # Parse numbered or bulleted vocabulary items
    # Format: "1. word – definition" or "- word – definition"
    for line in vocab_section.split('\n'):
        line = line.strip()
        
        # Try numbered format (1. word – definition)
        num_match = re.match(r"^\d+\.\s+(.+?)\s+[-–—]\s+(.+)$", line)
        if num_match:
            word = num_match.group(1).strip()
            definition = num_match.group(2).strip()
            vocab_items.append({'word': word, 'definition': definition})
            continue
        
        # Try bullet format (- word – definition)
        bullet_match = re.match(r"^[-•]\s+(.+?)\s+[-–—]\s+(.+)$", line)
        if bullet_match:
            word = bullet_match.group(1).strip()
            definition = bullet_match.group(2).strip()
            vocab_items.append({'word': word, 'definition': definition})
            continue
        
        # Try inline format (all on one line, separated by " – ")
        # Format: "word – word – word – ..." or "word - definition, word - definition"
        if '–' in line and not line.startswith('**'):
            # Check if it's a simple list (no definitions, just words)
            parts = [p.strip() for p in line.split('–')]
            if len(parts) > 2:  # Likely a list of words only
                for word in parts:
                    if word and not any(keyword in word.lower() for keyword in ['semantic', 'domain', 'vocabulary']):
                        vocab_items.append({'word': word, 'definition': ''})
    
    return vocab_items


def parse_speaking_scenario(content: str) -> Dict[str, Any]:
    """
    Extract speaking scenario information.
    
    Returns:
        Dictionary with 'domain', 'example_interaction', 'interaction_tier'
    """
    pattern = r"### Speaking Scenario.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'domain': 'General conversation',
            'example_interaction': [],
            'interaction_tier': 1
        }
    
    scenario_section = match.group(1)
    
    # Extract domain
    domain_match = re.search(r"\*\*Domain:\*\*\s+([^\n]+)", scenario_section)
    domain = domain_match.group(1).strip() if domain_match else "General conversation"
    
    # Extract interaction tier from earlier in the file
    tier_match = re.search(r"\*\*Tier:\*\*\s+(\d+)", content)
    tier = int(tier_match.group(1)) if tier_match else 1
    
    # Extract example interaction
    interaction = []
    interaction_match = re.search(
        r"(?:Example interaction|dialogue|conversation):?\s*\n(.*?)(?=\n\n|\n###|\Z)",
        scenario_section,
        re.DOTALL | re.IGNORECASE
    )
    if interaction_match:
        interaction_text = interaction_match.group(1)
        for line in interaction_text.split('\n'):
            line = line.strip()
            if line:
                interaction.append(line)
    
    return {
        'domain': domain,
        'example_interaction': interaction,
        'interaction_tier': tier
    }


def parse_reading_listening(content: str) -> Dict[str, Any]:
    """
    Extract reading/listening component.
    
    Returns:
        Dictionary with 'text', 'listening_tasks'
    """
    pattern = r"### Reading/Listening Component.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'type': 'unknown',
            'text': '',
            'listening_tasks': []
        }
    
    section = match.group(1)
    
    # Extract type
    type_match = re.search(r"\*\*Type:\*\*\s+([^\n]+)", section)
    text_type = type_match.group(1).strip() if type_match else "unknown"
    
    # Extract text example
    text_example = ''
    text_match = re.search(r"(?:Text example|text).*?:\s*\n(.*?)(?=\n\n|\*\*|\Z)", section, re.DOTALL)
    if text_match:
        text_example = text_match.group(1).strip()
    
    # Extract listening/reading tasks
    tasks = []
    tasks_match = re.search(r"(?:Listening task|Reading task|answers?|questions?):\s*\n(.*?)(?=\n\n|\Z)", section, re.DOTALL | re.IGNORECASE)
    if tasks_match:
        tasks_text = tasks_match.group(1)
        for line in tasks_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                if line[0].isdigit():
                    task = re.sub(r'^\d+\.\s*', '', line)
                else:
                    task = re.sub(r'^[-•]\s*', '', line)
                tasks.append(task)
    
    return {
        'type': text_type,
        'text': text_example,
        'listening_tasks': tasks
    }


def parse_homework_task(content: str) -> Dict[str, Any]:
    """
    Extract homework assignment information.
    
    Returns:
        Dictionary with 'type', 'task_description', 'rubric', 'pass_threshold'
    """
    pattern = r"### Homework Assignment.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'type': 'unknown',
            'task_description': '',
            'rubric': [],
            'pass_threshold': 4
        }
    
    section = match.group(1)
    
    # Extract type
    type_match = re.search(r"\*\*Type:\*\*\s+([^\n]+)", section)
    hw_type = type_match.group(1).strip() if type_match else "unknown"
    
    # Extract task description
    task_desc = ''
    task_match = re.search(r"\*\*Task:\*\*\s*\n+(.*?)(?=\n\n\*\*Rubric|\Z)", section, re.DOTALL)
    if task_match:
        task_desc = task_match.group(1).strip()
    else:
        # Fallback: try simpler pattern without requiring double newline
        task_match = re.search(r"\*\*Task:\*\*\s*\n+(.*?)(?=\n\*\*|\Z)", section, re.DOTALL)
        if task_match:
            task_desc = task_match.group(1).strip()
    
    # Extract rubric (checkbox items)
    rubric = []
    rubric_match = re.search(r"(?:\*\*)?Rubric.*?criteria.*?:?\s*\n(.*?)(?=\n\*\*|\Z)", section, re.DOTALL | re.IGNORECASE)
    if rubric_match:
        rubric_text = rubric_match.group(1)
        for line in rubric_text.split('\n'):
            line = line.strip()
            # Extract checkbox items (- [ ] criterion)
            if line.startswith('- [') or line.startswith('- '):
                criterion = re.sub(r'^-\s*\[\s*\]\s*', '', line).strip()
                if criterion:
                    rubric.append(criterion)
    
    # Extract pass threshold
    pass_threshold = 4
    threshold_match = re.search(r"Pass Threshold:\s*(\d+)/", section)
    if threshold_match:
        pass_threshold = int(threshold_match.group(1))
    
    return {
        'type': hw_type,
        'task_description': task_desc,
        'rubric': rubric,
        'pass_threshold': pass_threshold
    }


def parse_assessment_checkpoint(content: str) -> Dict[str, Any]:
    """
    Extract assessment checkpoint (mini-quiz) questions.
    
    Returns:
        Dictionary with 'question_count', 'questions'
    """
    pattern = r"### Assessment Checkpoint.*?\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'question_count': 0,
            'questions': []
        }
    
    section = match.group(1)
    
    # Extract numbered questions
    questions = []
    for line in section.split('\n'):
        line = line.strip()
        # Match "1. question → expected_answer" or "1. question"
        q_match = re.match(r"^\d+\.\s+(.+?)(?:\s+[-–—>]+\s+(.+))?$", line)
        if q_match:
            question = q_match.group(1)
            answer = q_match.group(2) if q_match.group(2) else ''
            questions.append({
                'question': question,
                'expected_answer': answer
            })
    
    return {
        'question_count': len(questions),
        'questions': questions
    }


def parse_exam_rubric(content: str) -> Dict[str, Any]:
    """
    Extract exam rubric (scoring criteria).
    
    Returns:
        Dictionary with rubric criteria
    """
    pattern = r"(?:### )?Weekly Exam Rubric.*?\n(.*?)(?=\n###|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return {
            'criteria': [],
            'pass_percentage': 70
        }
    
    section = match.group(1)
    
    # Extract criteria (usually "Criteria (0-4):" format)
    criteria = []
    for line in section.split('\n'):
        line = line.strip()
        # Match "- Accuracy (0-4): description"
        criterion_match = re.match(r"^[-•]\s*(.+?)\s*\((\d+)-(\d+)\)\s*:\s*(.+)$", line)
        if criterion_match:
            criteria.append({
                'name': criterion_match.group(1),
                'min_score': int(criterion_match.group(2)),
                'max_score': int(criterion_match.group(3)),
                'description': criterion_match.group(4)
            })
    
    # Extract pass percentage
    pass_match = re.search(r"Pass:\s*(\d+)/10\s*\((\d+)%\)", section)
    pass_percentage = 70
    if pass_match:
        pass_percentage = int(pass_match.group(2))
    
    return {
        'criteria': criteria,
        'pass_percentage': pass_percentage
    }


def validate_curriculum(curriculum_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate that all required sections are present and well-formed.
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check required sections
    if not curriculum_data.get('learning_outcomes'):
        errors.append("Learning outcomes not found or empty")
    
    if not curriculum_data.get('grammar_target', {}).get('form'):
        errors.append("Grammar target form not found")
    
    vocab = curriculum_data.get('vocabulary_set', [])
    if not vocab:
        errors.append("Vocabulary set not found or empty")
    elif len(vocab) < 15:
        errors.append(f"Vocabulary set has {len(vocab)} words; expected at least 15")
    
    if not curriculum_data.get('speaking_scenario', {}).get('domain'):
        errors.append("Speaking scenario domain not found")
    
    if not curriculum_data.get('homework_task', {}).get('task_description'):
        errors.append("Homework task description not found")
    
    if not curriculum_data.get('assessment_checkpoint', {}).get('questions'):
        errors.append("Assessment checkpoint questions not found")
    
    return len(errors) == 0, errors


# =============================================================================
# NEW CURRICULUM SYSTEM (Research/NEW_CURRICULUM_REDESIGNED/)
# =============================================================================

def load_redesigned_curriculum_day(week_number: int, day_number: int) -> Dict[str, Any]:
    """
    Load and parse a SINGLE DAY from the redesigned curriculum format.
    
    Args:
        week_number: Week number (1-52)
        day_number: Day number (1-7)
    
    Returns:
        Dictionary containing parsed day lesson data:
        {
            'week_number': int,
            'day_number': int,
            'cefr_level': str,
            'grammar_topic': str,
            'vocabulary_domain': str,
            'content_identifiers': [str],
            'speaking_tier': int,
            'duration': str,
            'grammar_explanation': str (5-paragraph format),
            'vocabulary': [{'word': str, 'type': str, 'english': str, 'pronunciation': str, 'example': str}],
            'examples': [{'content_identifiers': [str], 'text': str, 'task': str, 'answer': str}],
            'filepath': str
        }
    
    Raises:
        FileNotFoundError: If the curriculum file doesn't exist
        ValueError: If the day section is not found
    """
    # Determine filename pattern: Week_X_A1.X.md
    # Week 1-4: A1.1, Week 5-8: A1.2, etc.
    cefr_level = _determine_cefr_level(week_number)
    filename = f"Week_{week_number}_{cefr_level}.md"
    filepath = REDESIGNED_CURRICULUM_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Redesigned curriculum file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Calculate overall day number
    # Week 1 → Day 1-5, Week 2 → Day 6-10, Week 3 → Day 11-15, etc.
    overall_day_number = (week_number - 1) * 5 + day_number
    
    # Extract the DAY section using overall day number
    day_pattern = rf"##\s+DAY\s+{overall_day_number}\s*-[^\n]+\n(.*?)(?=\n##\s+DAY\s+\d+|$)"
    day_match = re.search(day_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not day_match:
        raise ValueError(f"Day {overall_day_number} (Week {week_number} Day {day_number}) not found in {filepath}")
    
    day_content = day_match.group(1)
    
    # Parse metadata
    metadata = _parse_day_metadata(day_content)
    
    # Parse grammar explanation (5-paragraph format)
    grammar_explanation = _parse_day_grammar_explanation(day_content)
    
    # Parse vocabulary (5 words)
    vocabulary = _parse_day_vocabulary(day_content)
    
    # Parse examples (50 examples with content identifiers)
    examples = _parse_day_examples(day_content)
    
    return {
        'week_number': week_number,
        'day_number': day_number,
        'cefr_level': metadata.get('cefr_level', cefr_level),
        'grammar_topic': metadata.get('grammar_topic', ''),
        'vocabulary_domain': metadata.get('vocabulary_domain', ''),
        'content_identifiers': metadata.get('content_identifiers', []),
        'speaking_tier': metadata.get('speaking_tier', 1),
        'duration': metadata.get('duration', '30 minutes'),
        'grammar_explanation': grammar_explanation,
        'vocabulary': vocabulary,
        'examples': examples,
        'filepath': str(filepath)
    }


def _determine_cefr_level(week_number: int) -> str:
    """Determine CEFR level based on week number (Month 1-12 mapping)."""
    if 1 <= week_number <= 4:
        return "A1.1"
    elif 5 <= week_number <= 8:
        return "A1.2"
    elif 9 <= week_number <= 16:
        return "A2.1"
    elif 17 <= week_number <= 24:
        return "A2.2"
    elif 25 <= week_number <= 32:
        return "B1.1"
    elif 33 <= week_number <= 40:
        return "B1.2"
    elif 41 <= week_number <= 48:
        return "B2.1"
    else:  # 49-52
        return "B2.2"


def _parse_day_metadata(day_content: str) -> Dict[str, Any]:
    """Parse metadata section from a day."""
    metadata = {}
    
    # CEFR Level
    cefr_match = re.search(r"\*\*CEFR Level:\*\*\s+([A-B][12]\.[12])", day_content)
    if cefr_match:
        metadata['cefr_level'] = cefr_match.group(1)
    
    # Grammar Topic
    grammar_match = re.search(r"\*\*Grammar Topic:\*\*\s+([^\n]+)", day_content)
    if grammar_match:
        metadata['grammar_topic'] = grammar_match.group(1).strip()
    
    # Vocabulary Domain
    vocab_match = re.search(r"\*\*Vocabulary Domain:\*\*\s+([^\n]+)", day_content)
    if vocab_match:
        metadata['vocabulary_domain'] = vocab_match.group(1).strip()
    
    # Content Identifiers (comma-separated list)
    content_match = re.search(r"\*\*Content Identifiers:\*\*\s+([^\n]+)", day_content)
    if content_match:
        identifiers_str = content_match.group(1).strip()
        metadata['content_identifiers'] = [i.strip() for i in identifiers_str.split(',')]
    
    # Speaking Tier
    tier_match = re.search(r"\*\*Speaking Tier:\*\*\s+(\d+)", day_content)
    if tier_match:
        metadata['speaking_tier'] = int(tier_match.group(1))
    
    # Duration
    duration_match = re.search(r"\*\*Duration:\*\*\s+([^\n]+)", day_content)
    if duration_match:
        metadata['duration'] = duration_match.group(1).strip()
    
    return metadata


def _parse_day_grammar_explanation(day_content: str) -> str:
    """
    Parse the 5-paragraph grammar explanation.
    Returns the full text of the grammar section (FIXED content).
    """
    # Find GRAMMAR SECTION
    grammar_pattern = r"###\s+GRAMMAR SECTION[^\n]*\n+(.*?)(?=\n###\s+VOCABULARY SECTION|$)"
    grammar_match = re.search(grammar_pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if grammar_match:
        return grammar_match.group(1).strip()
    
    return "Grammar explanation not found."


def _parse_day_vocabulary(day_content: str) -> List[Dict[str, str]]:
    """
    Parse the 5 vocabulary words from VOCABULARY SECTION.
    
    Returns:
        List of dicts with keys: word, type, english, pronunciation, example, context
    """
    vocab_items = []
    
    # Find VOCABULARY SECTION
    vocab_pattern = r"###\s+VOCABULARY SECTION[^\n]*\n+(.*?)(?=\n###\s+EXAMPLES SECTION|$)"
    vocab_match = re.search(vocab_pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if not vocab_match:
        return []
    
    vocab_section = vocab_match.group(1)
    
    # Parse each word block (Word 1:, Word 2:, etc.)
    word_blocks = re.findall(
        r"\*\*Word\s+\d+:\s+([^\*]+?)\*\*\s*\n(.*?)(?=\n\*\*Word\s+\d+:|$)",
        vocab_section,
        re.DOTALL
    )
    
    for word, details in word_blocks:
        word = word.strip()
        
        # Extract type
        type_match = re.search(r"-\s+Type:\s+([^\n]+)", details)
        word_type = type_match.group(1).strip() if type_match else ""
        
        # Extract English
        english_match = re.search(r"-\s+English:\s+([^\n]+)", details)
        english = english_match.group(1).strip() if english_match else ""
        
        # Extract pronunciation
        pron_match = re.search(r"-\s+Pronunciation:\s+([^\n]+)", details)
        pronunciation = pron_match.group(1).strip() if pron_match else ""
        
        # Extract example sentence
        example_match = re.search(r'-\s+\*\*Example sentence:\*\*\s+["\"]([^"\"]+)["\"]', details)
        example = example_match.group(1).strip() if example_match else ""
        
        # Extract context
        context_match = re.search(r"-\s+Context:\s+([^\n]+)", details)
        context = context_match.group(1).strip() if context_match else ""
        
        vocab_items.append({
            'word': word,
            'type': word_type,
            'english': english,
            'pronunciation': pronunciation,
            'example': example,
            'context': context
        })
    
    return vocab_items


def _parse_day_examples(day_content: str) -> List[Dict[str, Any]]:
    """
    Parse the 50 example questions from EXAMPLES SECTION.
    
    Returns:
        List of dicts with keys: content_identifiers (list), text, task, answer, number
    """
    examples = []
    
    # Find EXAMPLES SECTION
    examples_pattern = r"###\s+EXAMPLES SECTION[^\n]*\n+(.*?)(?=\n###\s+[A-Z]+\s+SECTION|$)"
    examples_match = re.search(examples_pattern, day_content, re.DOTALL | re.IGNORECASE)
    
    if not examples_match:
        return []
    
    examples_section = examples_match.group(1)
    
    # Parse numbered examples with pattern:
    # 1. **[content_id1, content_id2]**
    #    - Sentence/Task: "..."
    #    - Answer: ...
    
    # Alternative simpler pattern - just capture numbered items with brackets
    example_blocks = re.findall(
        r"(\d+)\.\s+\*\*\[([^\]]+)\]\*\*\s*\n(.*?)(?=\n\d+\.\s+\*\*\[|$)",
        examples_section,
        re.DOTALL
    )
    
    for number, identifiers_str, details in example_blocks:
        # Parse content identifiers
        identifiers = [i.strip() for i in identifiers_str.split(',')]
        
        # Try to extract different fields
        # Could be: Audio, Sentence, Task, Question, Answer
        text = ""
        task = ""
        answer = ""
        
        # Look for "Sentence:", "Task:", "Question:", "Audio:", etc.
        sentence_match = re.search(r'-\s+(?:Sentence|Text|Audio|Question):\s+["\']([^"\']+)["\']', details)
        if sentence_match:
            text = sentence_match.group(1).strip()
        
        task_match = re.search(r'-\s+Task:\s+["\']([^"\']+)["\']', details)
        if task_match:
            task = task_match.group(1).strip()
        
        answer_match = re.search(r"-\s+Answer:\s+(.+?)(?=\n|$)", details)
        if answer_match:
            answer = answer_match.group(1).strip()
        
        examples.append({
            'number': int(number),
            'content_identifiers': identifiers,
            'text': text,
            'task': task,
            'answer': answer
        })
    
    return examples
