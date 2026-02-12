"""
Quiz Parser Module

Parses quiz questions from curriculum examples section.
Handles content identifier extraction and question selection.
"""

import random
from typing import Dict, List, Any, Optional
import curriculum_loader


def get_quiz_questions(week_number: int, day_number: int, count: int = 8) -> List[Dict[str, Any]]:
    """
    Get quiz questions for a specific day.
    Randomly selects {count} questions from the 50 available examples.
    
    Args:
        week_number: Week number (1-52)
        day_number: Day number (1-7)
        count: Number of questions to select (default 8-10)
    
    Returns:
        List of question dicts with content_identifiers, text, task, answer
    
    Example output:
    [
        {
            'number': 1,
            'content_identifiers': ['listening', 'dialogue', 'gist'],
            'text': 'Bonjour! Je suis Marie.',
            'task': 'What is the person's name?',
            'answer': 'Marie',
            'question_type': 'listening'  # primary type
        },
        ...
    ]
    """
    # Load curriculum day
    try:
        day_data = curriculum_loader.load_redesigned_curriculum_day(week_number, day_number)
    except (FileNotFoundError, ValueError) as e:
        # Fallback: return empty list if curriculum not found
        return []
    
    examples = day_data.get('examples', [])
    
    if not examples:
        return []
    
    # Randomly select {count} questions from available examples
    # Ensure variety of content identifiers
    selected = _select_diverse_questions(examples, count)
    
    # Format questions for quiz display
    quiz_questions = []
    for idx, example in enumerate(selected, 1):
        identifiers = example.get('content_identifiers', [])
        
        quiz_questions.append({
            'number': idx,  # Re-number for quiz (1-8)
            'original_number': example.get('number', 0),
            'content_identifiers': identifiers,
            'text': example.get('text', ''),
            'task': example.get('task', ''),
            'answer': example.get('answer', ''),
            'question_type': _determine_primary_type(identifiers)
        })
    
    return quiz_questions


def _select_diverse_questions(examples: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    """
    Select questions while ensuring diversity of content identifiers.
    
    Strategy:
    1. Group examples by primary content identifier
    2. Select proportionally from each group
    3. Fill remaining slots randomly
    """
    if len(examples) <= count:
        return examples
    
    # Group by primary content type
    groups = {}
    for example in examples:
        identifiers = example.get('content_identifiers', [])
        primary_type = _determine_primary_type(identifiers)
        
        if primary_type not in groups:
            groups[primary_type] = []
        groups[primary_type].append(example)
    
    # Calculate how many from each group
    group_names = list(groups.keys())
    selections_per_group = max(1, count // len(group_names))
    
    selected = []
    
    # Select from each group
    for group_name in group_names:
        group_examples = groups[group_name]
        num_to_select = min(selections_per_group, len(group_examples))
        selected.extend(random.sample(group_examples, num_to_select))
    
    # Fill remaining slots if needed
    remaining = count - len(selected)
    if remaining > 0:
        unselected = [ex for ex in examples if ex not in selected]
        if unselected:
            selected.extend(random.sample(unselected, min(remaining, len(unselected))))
    
    # Shuffle to avoid grouping by type
    random.shuffle(selected)
    
    return selected[:count]


def _determine_primary_type(identifiers: List[str]) -> str:
    """
    Determine the primary content type from a list of identifiers.
    
    Priority order:
    1. listening (audio-based)
    2. reading (comprehension)
    3. speaking (production)
    4. writing (production)
    5. conjugation (grammar)
    6. fill_blank (grammar)
    7. Other types
    """
    if not identifiers:
        return 'unknown'
    
    # Priority mapping
    priority = {
        'listening': 10,
        'listen_identify': 10,
        'listen_gist': 10,
        'audio_dialogue': 10,
        'reading': 9,
        'reading_comprehension': 9,
        'speaking': 8,
        'dialogue_production': 8,
        'writing': 7,
        'conjugation': 6,
        'fill_blank': 5,
        'vocabulary': 4,
        'matching': 3,
        'word_order': 3
    }
    
    # Find highest priority identifier
    best_type = identifiers[0]  # fallback
    best_priority = priority.get(identifiers[0].lower(), 0)
    
    for identifier in identifiers:
        identifier_lower = identifier.lower().strip()
        current_priority = priority.get(identifier_lower, 0)
        if current_priority > best_priority:
            best_priority = current_priority
            best_type = identifier_lower
    
    return best_type


def format_question_for_display(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a quiz question for frontend display.
    
    Adds UI-specific fields like:
    - question_html: Formatted question text
    - has_audio: Whether TTS should be used
    - answer_type: 'text', 'multiple_choice', etc.
    """
    question_type = question.get('question_type', 'unknown')
    
    # Determine if audio should be played
    has_audio = any(
        audio_type in question_type 
        for audio_type in ['listening', 'audio', 'pronunciation']
    )
    
    # Determine answer input type
    answer_type = 'text'  # default
    if 'matching' in question_type:
        answer_type = 'matching'
    elif 'multiple_choice' in question_type:
        answer_type = 'multiple_choice'
    elif question_type in ['fill_blank', 'conjugation']:
        answer_type = 'short_answer'
    
    # Build formatted question HTML
    question_html = _build_question_html(question)
    
    return {
        **question,  # Include all original fields
        'question_html': question_html,
        'has_audio': has_audio,
        'answer_type': answer_type,
        'audio_text': question.get('text', '') if has_audio else None
    }


def _build_question_html(question: Dict[str, Any]) -> str:
    """Build HTML-formatted question text."""
    text = question.get('text', '')
    task = question.get('task', '')
    
    # If there's both text and task, show both
    if text and task:
        return f'<p class="question-text">{text}</p><p class="question-task"><strong>Task:</strong> {task}</p>'
    
    # If only task, show that
    if task:
        return f'<p class="question-task">{task}</p>'
    
    # If only text, show that
    if text:
        return f'<p class="question-text">{text}</p>'
    
    return '<p>Question text not available</p>'


def get_content_identifier_stats(week_number: int, day_number: int) -> Dict[str, int]:
    """
    Get statistics on content identifier distribution for a day.
    Useful for analytics and ensuring balanced question types.
    
    Returns:
        Dict mapping content_identifier → count
        Example: {'listening': 12, 'conjugation': 8, 'fill_blank': 10, ...}
    """
    try:
        day_data = curriculum_loader.load_redesigned_curriculum_day(week_number, day_number)
    except (FileNotFoundError, ValueError):
        return {}
    
    examples = day_data.get('examples', [])
    
    # Count all identifiers (one example can have multiple)
    identifier_counts = {}
    
    for example in examples:
        for identifier in example.get('content_identifiers', []):
            identifier = identifier.strip()
            identifier_counts[identifier] = identifier_counts.get(identifier, 0) + 1
    
    return identifier_counts
