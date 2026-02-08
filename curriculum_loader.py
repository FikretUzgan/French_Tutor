"""
Curriculum Loader Module

Handles parsing of curriculum markdown files from New_Curriculum/
Extracts structured data for lesson generation.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


CURRICULUM_DIR = Path(__file__).parent / "New_Curriculum"


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
