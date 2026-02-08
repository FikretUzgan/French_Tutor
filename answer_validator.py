"""
Smart answer validator for French language learning.
Handles punctuation normalization, accent detection, and comparison logic.
"""

import unicodedata
import re
from typing import Dict, List, Tuple


def normalize_punctuation(text: str) -> str:
    """Remove punctuation marks from text.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Text with punctuation removed (., , ? ! ; : - etc.)
    """
    # Remove common punctuation
    text = text.replace('.', '')
    text = text.replace(',', '')
    text = text.replace('?', '')
    text = text.replace('!', '')
    text = text.replace(';', '')
    text = text.replace(':', '')
    text = text.replace('-', '')
    text = text.replace('"', '')
    text = text.replace("'", '')
    text = text.replace('«', '')
    text = text.replace('»', '')
    return text.strip()


def normalize_accents(text: str) -> str:
    """Remove all accents from French text.
    
    Args:
        text: Input text with accents
        
    Returns:
        Text with accents removed (é→e, è→e, etc.)
    """
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def has_accent_difference(correct: str, student: str) -> bool:
    """Check if texts differ only in accents.
    
    Args:
        correct: Correct answer
        student: Student answer
        
    Returns:
        True if they match when accents are removed
    """
    return normalize_accents(correct.lower()) == normalize_accents(student.lower())


def validate_answer(correct: str, student: str) -> Dict[str, any]:
    """Validate a student answer against the correct answer.
    
    Returns a dict with:
    - is_correct: True if perfect match
    - is_close: True if close (punctuation/accent only)
    - warnings: List of issues (accent, punctuation differences)
    - errors: List of critical errors  
    - feedback: Human-readable feedback
    
    Args:
        correct: The correct answer
        student: The student's answer
        
    Returns:
        Validation result dict
    """
    correct_clean = normalize_punctuation(correct).lower()
    student_clean = normalize_punctuation(student).lower()
    
    result = {
        'is_correct': False,
        'is_close': False,
        'warnings': [],
        'errors': [],
        'feedback': ''
    }
    
    # Perfect match (ignoring case and punctuation)
    if correct_clean == student_clean:
        result['is_correct'] = True
        result['feedback'] = '✓ Correct!'
        return result
    
    # Check if only difference is accents
    if has_accent_difference(correct_clean, student_clean):
        result['is_close'] = True
        result['warnings'].append('accent_difference')
        result['feedback'] = '⚠ Correct, but check accents: é, è, ê, ë, ç, etc.'
        return result
    
    # Check for minor punctuation/spacing issues
    correct_words = correct_clean.split()
    student_words = student_clean.split()
    
    if len(correct_words) != len(student_words):
        result['errors'].append('wrong_word_count')
        result['feedback'] = f'✗ Expected {len(correct_words)} words, got {len(student_words)}'
        return result
    
    # Word-by-word comparison
    word_errors = []
    for i, (correct_word, student_word) in enumerate(zip(correct_words, student_words)):
        if correct_word != student_word:
            if normalize_accents(correct_word) == normalize_accents(student_word):
                result['warnings'].append(f'word_{i}_accent')
            else:
                word_errors.append(i)
    
    if word_errors:
        if len(word_errors) == 1:
            result['errors'].append(f'word_{word_errors[0]}')
            result['feedback'] = f'✗ Word {word_errors[0] + 1} is incorrect'
        else:
            result['errors'].append('multiple_words')
            result['feedback'] = f'✗ {len(word_errors)} words are incorrect'
        return result
    
    if result['warnings']:
        result['is_close'] = True
        result['feedback'] = '⚠ Close! Check accents on some words'
        return result
    
    # Complete mismatch
    result['errors'].append('completely_wrong')
    result['feedback'] = '✗ Incorrect answer'
    return result


def compare_answers(correct: str, student: str) -> Tuple[bool, str]:
    """Simple comparison returning pass/fail and message.
    
    Args:
        correct: Correct answer
        student: Student answer
        
    Returns:
        Tuple of (passed: bool, message: str)
    """
    result = validate_answer(correct, student)
    
    if result['is_correct']:
        return True, 'Correct!'
    elif result['is_close']:
        return True, f"Close! {result['feedback']}"
    else:
        return False, result['feedback']
