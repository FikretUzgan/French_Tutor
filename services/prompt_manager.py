"""
Prompt Manager Service
Constructs complete prompts by combining templates with student data.
Handles formatting of student profile, curriculum data, and personalization info.
Refactored from prompt_builders.py.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import core.prompts as prompts


def build_system_prompt(
    student_level: str,
    completed_weeks: Optional[List[int]] = None,
    weaknesses: Optional[List[str]] = None
) -> str:
    """
    Build the system prompt for lesson generation.
    """
    prompt = prompts.get_system_prompt()
    
    # Customize system prompt based on level
    if student_level.startswith('A1'):
        level_note = "\n[Level Note: A1 learner - keep explanations very simple, use lots of English translations, use present tense mostly, celebrate small wins]"
    elif student_level.startswith('A2'):
        level_note = "\n[Level Note: A2 learner - introduce past tense, increase complexity slightly, expect 1-2 minute interactions]"
    elif student_level.startswith('B1'):
        level_note = "\n[Level Note: B1 learner - focus on accuracy, introduce subjunctive, longer interactions OK, discuss reasoning]"
    else:
        level_note = "\n[Level Note: B2 learner - advanced topics, subtle grammar distinctions, complex interactions expected]"
    
    return prompt + level_note


def build_lesson_generation_context(
    week_number: int,
    day_number: int,
    curriculum_data: Dict[str, Any],
    student_profile: Dict[str, Any],
    weaknesses_data: Optional[List[Dict[str, Any]]] = None,
    attempt_number: int = 1,
    variation_seed: int = None
) -> str:
    """
    Build the complete lesson generation prompt with all context.
    """
    student_level = student_profile.get('level', 'A1.1')
    completed_weeks = student_profile.get('completed_weeks', [])
    
    # Format weaknesses for prompt
    weaknesses_list = []
    struggled_topics = []
    if weaknesses_data:
        for weakness in weaknesses_data:
            topic = weakness.get('topic', 'Unknown')
            error_count = weakness.get('error_count', 1)
            weaknesses_list.append(f"{topic} (encountered {error_count} times)")
            if error_count >= 2:
                struggled_topics.append(topic)
    
    # Get current ISO timestamp
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Get the theme
    curriculum_theme = curriculum_data.get('theme', 'General')
    
    # Build the prompt using the template (now with variation support)
    prompt = prompts.get_lesson_generation_prompt(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        completed_weeks=completed_weeks,
        weaknesses=weaknesses_list,
        struggled_topics=struggled_topics,
        curriculum_data=curriculum_data,
        curriculum_theme=curriculum_theme,
        timestamp=timestamp,
        attempt_number=attempt_number,
        variation_seed=variation_seed
    )
    
    # If student has significant weaknesses, add the personalization sub-prompt
    if struggled_topics:
        personalization = prompts.WEAKNESS_PERSONALIZATION_SUBPROMPT.format(
            weaknesses_list='\n'.join([f"- {w}" for w in weaknesses_list])
        )
        prompt += "\n\n" + personalization
    
    return prompt


def build_homework_evaluation_prompt(
    week_number: int,
    day_number: int,
    student_level: str,
    homework_assignment: Dict[str, Any],
    student_submission: str,
    lesson_content: Dict[str, Any],
    submission_id: str
) -> str:
    """
    Build prompt for evaluating homework submission.
    """
    prompt = prompts.get_homework_evaluation_prompt(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        homework_assignment=homework_assignment,
        student_submission=student_submission,
        lesson_content=lesson_content,
        submission_id=submission_id
    )
    
    return prompt


def build_speaking_feedback_prompt(
    scenario_domain: str,
    target_phrases: List[str],
    interaction_tier: int,
    student_transcription: str,
    scenario_details: Dict[str, Any]
) -> str:
    """
    Build prompt for evaluating a speaking practice interaction.
    """
    target_skill = ', '.join(target_phrases[:2]) if target_phrases else 'General interaction'
    
    prompt = prompts.get_speaking_feedback_prompt(
        scenario=scenario_domain,
        target_skill=target_skill,
        interaction_tier=interaction_tier,
        student_transcription=student_transcription,
        scenario_details=scenario_details
    )
    
    return prompt


def build_quiz_evaluation_prompt(
    week_number: int,
    day_number: int,
    student_level: str,
    grammar_target: str,
    quiz_questions: List[Dict[str, Any]],
    student_answers: Dict[str, str],
    quiz_id: str
) -> str:
    """
    Build prompt for evaluating quiz responses.
    """
    prompt = prompts.get_quiz_evaluation_prompt(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        grammar_target=grammar_target,
        quiz_questions=quiz_questions,
        student_answers=student_answers,
        quiz_id=quiz_id
    )
    
    return prompt


def estimate_prompt_tokens(prompt_text: str) -> int:
    """
    Rough estimate of token count for a prompt.
    """
    return len(prompt_text) // 4


def validate_prompt_token_budget(
    system_prompt: str,
    lesson_prompt: str,
    max_total_tokens: int = 4000
) -> Dict[str, Any]:
    """
    Check if prompts fit within token budget for Gemini API.
    """
    system_tokens = estimate_prompt_tokens(system_prompt)
    lesson_tokens = estimate_prompt_tokens(lesson_prompt)
    total = system_tokens + lesson_tokens
    
    return {
        'fits_budget': total <= max_total_tokens,
        'system_tokens': system_tokens,
        'lesson_tokens': lesson_tokens,
        'total_tokens': total,
        'max_allowed': max_total_tokens,
        'warning': f"Total {total} tokens exceeds budget of {max_total_tokens}" if total > max_total_tokens else None
    }
