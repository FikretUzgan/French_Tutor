"""
Prompt Context Builders

Functions to construct complete prompts by combining templates with student data.
Handles formatting of student profile, curriculum data, and personalization info.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import ai_prompts


def build_system_prompt(
    student_level: str,
    completed_weeks: Optional[List[int]] = None,
    weaknesses: Optional[List[str]] = None
) -> str:
    """
    Build the system prompt for lesson generation.
    
    The system prompt sets the AI's overall context and teaching approach.
    It includes the student level to adjust tone/complexity.
    
    Args:
        student_level: CEFR level (e.g., 'A1.1', 'B2.2')
        completed_weeks: List of completed week numbers (affects tone)
        weaknesses: List of weakness descriptions (affects emphasis)
    
    Returns:
        The system prompt string
    
    Token count: ~450 tokens (relatively constant)
    """
    prompt = ai_prompts.get_system_prompt()
    
    # Customize system prompt based on level
    if student_level.startswith('A1'):
        # For absolute beginners, emphasize very clear explanations
        level_note = "\n[Level Note: A1 learner - keep explanations very simple, use lots of English translations, use present tense mostly, celebrate small wins]"
    elif student_level.startswith('A2'):
        # For A2, they can handle more explanation, some past tense
        level_note = "\n[Level Note: A2 learner - introduce past tense, increase complexity slightly, expect 1-2 minute interactions]"
    elif student_level.startswith('B1'):
        # For B1, focus on nuance and accuracy
        level_note = "\n[Level Note: B1 learner - focus on accuracy, introduce subjunctive, longer interactions OK, discuss reasoning]"
    else:
        # For B2, advanced materials
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
    
    This is the main prompt that asks the AI to generate a lesson. It includes:
    - The curriculum for the week
    - Student's profile (level, completed weeks)
    - Student's documented weaknesses
    - Variation instructions based on attempt number
    - Detailed expectations for output format
    
    Args:
        week_number: Week number (1-52)
        day_number: Day number (1-7)
        curriculum_data: Parsed curriculum (from curriculum_loader.load_curriculum_file)
        student_profile: Dict with 'level', 'completed_weeks'
        weaknesses_data: List of dicts with {'topic': str, 'error_count': int}
        attempt_number: Which generation attempt (1, 2, 3, 4+) — drives content variation
        variation_seed: Random seed for variation pool selection
    
    Returns:
        The complete prompt string for Gemini API
    
    Token count: ~1000-1500 tokens (varies with student context and attempt)
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
    prompt = ai_prompts.get_lesson_generation_prompt(
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
        personalization = ai_prompts.WEAKNESS_PERSONALIZATION_SUBPROMPT.format(
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
    
    Args:
        week_number: Week number
        day_number: Day number
        student_level: CEFR level
        homework_assignment: Homework assignment from curriculum/lesson
        student_submission: The student's submitted text
        lesson_content: The lesson that was taught
        submission_id: Unique ID for this submission
    
    Returns:
        The evaluation prompt
    
    Token count: ~800-1000 tokens
    """
    prompt = ai_prompts.get_homework_evaluation_prompt(
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
    
    Args:
        scenario_domain: The scenario type (e.g., 'Coffee shop order')
        target_phrases: List of target phrases for this interaction
        interaction_tier: Tier 1-3 (difficulty level)
        student_transcription: What the student said
        scenario_details: Full scenario details from lesson
    
    Returns:
        The speaking feedback prompt
    
    Token count: ~500-600 tokens
    """
    target_skill = ', '.join(target_phrases[:2]) if target_phrases else 'General interaction'
    
    prompt = ai_prompts.get_speaking_feedback_prompt(
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
    
    Args:
        week_number: Week number
        day_number: Day number
        student_level: CEFR level
        grammar_target: The grammar structure being tested
        quiz_questions: The quiz questions
        student_answers: Dict mapping question_id to student's answer
        quiz_id: Unique ID for this quiz attempt
    
    Returns:
        The quiz evaluation prompt
    
    Token count: ~400-500 tokens
    """
    prompt = ai_prompts.get_quiz_evaluation_prompt(
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
    
    Uses the heuristic: ~4 characters per token (approximate).
    Gemini API typically uses 1 token per ~4 English characters.
    
    Args:
        prompt_text: The prompt text
    
    Returns:
        Estimated token count
    """
    return len(prompt_text) // 4


def validate_prompt_token_budget(
    system_prompt: str,
    lesson_prompt: str,
    max_total_tokens: int = 4000
) -> Dict[str, Any]:
    """
    Check if prompts fit within token budget for Gemini API.
    
    Args:
        system_prompt: The system prompt
        lesson_prompt: The lesson generation prompt
        max_total_tokens: Maximum allowed total tokens (default 4000, can go to 30000 for pro)
    
    Returns:
        Dict with 'fits_budget', 'system_tokens', 'lesson_tokens', 'total_tokens'
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


def format_student_weaknesses(weaknesses_list: List[str]) -> str:
    """
    Format a list of weaknesses nicely for display in prompts.
    
    Args:
        weaknesses_list: List of weakness/topic strings
    
    Returns:
        Formatted string
    """
    if not weaknesses_list:
        return "No documented weaknesses yet"
    
    return '\n'.join([f"- {w}" for w in weaknesses_list])


def format_curriculum_for_prompt(curriculum_data: Dict[str, Any]) -> str:
    """
    Format curriculum data for inclusion in prompts.
    
    Args:
        curriculum_data: The parsed curriculum from curriculum_loader
    
    Returns:
        Nicely formatted curriculum string for prompts
    """
    return ai_prompts._format_curriculum_for_display(curriculum_data)


def format_student_for_prompt(student_profile: Dict[str, Any]) -> str:
    """
    Format student profile for inclusion in prompts.
    
    Args:
        student_profile: Dict with student data
    
    Returns:
        Formatted student summary
    """
    parts = []
    
    level = student_profile.get('level', 'Unknown')
    parts.append(f"Current Level: {level}")
    
    completed = student_profile.get('completed_weeks', [])
    if completed:
        parts.append(f"Completed Weeks: {', '.join(map(str, completed))}")
    else:
        parts.append("Completed Weeks: None yet (starting fresh)")
    
    user_id = student_profile.get('user_id', 1)
    parts.append(f"User ID: {user_id}")
    
    return '\n'.join(parts)
