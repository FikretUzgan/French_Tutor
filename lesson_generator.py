"""
Lesson Generator Module

Main logic for generating dynamic lessons using Gemini API.
Handles curriculum loading, prompt building, API calls, and fallback logic.
"""

import json
import logging
import random
import re
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import google.genai as genai
from pathlib import Path
import os

import curriculum_loader
import prompt_builders
import db

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API client
_GENAI_CLIENT = None

def _get_genai_client():
    """Get or create Gemini API client."""
    global _GENAI_CLIENT
    if _GENAI_CLIENT is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            _GENAI_CLIENT = genai.Client(api_key=api_key)
            logger.info("Gemini API client created from GEMINI_API_KEY environment variable")
        else:
            logger.warning("GEMINI_API_KEY environment variable not set")
            raise ValueError("GEMINI_API_KEY environment variable not set")
    return _GENAI_CLIENT


class LessonGenerationError(Exception):
    """Raised when lesson generation fails."""
    pass


def generate_lesson_from_curriculum(
    week_number: int,
    day_number: int,
    student_level: str,
    user_id: int = 1,
    fallback_on_error: bool = True
) -> Tuple[Dict[str, Any], bool]:
    """
    Generate a complete lesson from curriculum using Gemini API.
    
    This is the main entry point for lesson generation. It:
    1. Loads the curriculum
    2. Fetches student profile and weaknesses
    3. Builds system and content prompts
    4. Calls Gemini API
    5. Validates response
    6. Falls back to default lesson if needed
    
    Args:
        week_number: Week number (1-52)
        day_number: Day number (1-7)
        student_level: CEFR level (e.g., 'A1.1', 'B2.2')
        user_id: Student user ID (default 1)
        fallback_on_error: If True, return fallback lesson on API error (default True)
    
    Returns:
        Tuple of (lesson_dict, was_generated_by_api)
        - lesson_dict: The generated or fallback lesson
        - was_generated_by_api: True if AI-generated, False if fallback
    
    Raises:
        LessonGenerationError: If generation fails and fallback_on_error is False
        ValueError: If week/day/level parameters are invalid
    
    Token usage: ~1000-1300 tokens per call
    """
    # Validate parameters
    if not (1 <= week_number <= 52):
        raise ValueError(f"Week must be 1-52, got {week_number}")
    if not (1 <= day_number <= 7):
        raise ValueError(f"Day must be 1-7, got {day_number}")
    
    valid_levels = ['A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2']
    if student_level not in valid_levels:
        raise ValueError(f"Level must be one of {valid_levels}, got {student_level}")
    
    try:
        # Step 1: Load curriculum
        logger.info(f"Loading curriculum for Week {week_number}")
        curriculum_data = curriculum_loader.load_curriculum_file(week_number)
        
        # Validate curriculum
        is_valid, errors = curriculum_loader.validate_curriculum(curriculum_data)
        if not is_valid:
            logger.warning(f"Curriculum validation warnings: {errors}")
            # Continue anyway - some missing sections might be OK
        
        # Step 1b: Determine attempt number (how many times this week/day was generated)
        attempt_number = db.get_lesson_generation_count(user_id, week_number, day_number) + 1
        variation_seed = int(datetime.now(timezone.utc).timestamp()) % 100000
        logger.info(f"Generation attempt #{attempt_number} for Week {week_number} Day {day_number} (seed: {variation_seed})")
        
        # Step 2: Get student profile
        logger.info(f"Fetching student profile for user {user_id}")
        student_profile = db.get_student_profile(user_id)
        if not student_profile:
            # Create a default profile if doesn't exist
            student_profile = {
                'user_id': user_id,
                'level': student_level,
                'completed_weeks': [],
                'started_at': datetime.now(timezone.utc).isoformat()
            }
        else:
            # Override level if provided as parameter
            student_profile['level'] = student_level
        
        # Step 3: Get student weaknesses
        logger.info(f"Fetching weaknesses for user {user_id}")
        weaknesses = db.get_student_weaknesses(user_id, limit=5)
        
        # Step 4: Build prompts (now with attempt_number and variation_seed)
        logger.info(f"Building prompts (attempt #{attempt_number})")
        system_prompt = prompt_builders.build_system_prompt(
            student_level=student_level,
            completed_weeks=student_profile.get('completed_weeks', []),
            weaknesses=[w.get('topic', 'Unknown') for w in weaknesses]
        )
        
        lesson_prompt = prompt_builders.build_lesson_generation_context(
            week_number=week_number,
            day_number=day_number,
            curriculum_data=curriculum_data,
            student_profile=student_profile,
            weaknesses_data=weaknesses,
            attempt_number=attempt_number,
            variation_seed=variation_seed
        )
        
        # Validate token budget (but don't fail, just warn)
        token_info = prompt_builders.validate_prompt_token_budget(
            system_prompt=system_prompt,
            lesson_prompt=lesson_prompt,
            max_total_tokens=4000  # Increased from 3000 to 4000
        )
        logger.info(f"Token usage: {token_info['total_tokens']} / {token_info['max_allowed']}")
        
        if not token_info['fits_budget']:
            logger.warning(f"Prompt token usage: {token_info['total_tokens']} (budget: {token_info['max_allowed']})")
            # For now, continue anyway - Gemini can handle more
        
        # Step 5: Call Gemini API with dynamic temperature based on attempt
        # Higher attempts get higher temperature for more variation
        temperature = min(0.8 + (attempt_number - 1) * 0.15, 1.5)
        logger.info(f"Calling Gemini API for lesson generation (temp={temperature:.2f})")
        lesson_json, api_call_duration = _call_gemini_for_lesson(
            system_prompt=system_prompt,
            lesson_prompt=lesson_prompt,
            temperature=temperature,
            max_tokens=4096  # Increased for richer grammar explanations
        )
        
        # Step 6: Validate response
        logger.info("Validating generated lesson JSON")
        lesson_dict = _validate_lesson_json(lesson_json)
        
        # Step 7: Store in database
        logger.info(f"Storing lesson in database")
        lesson_id = lesson_dict.get('lesson_id', f"week_{week_number}_day_{day_number}")
        db.store_generated_lesson(
            user_id=user_id,
            lesson_id=lesson_id,
            week=week_number,
            day=day_number,
            curriculum_file=curriculum_data.get('filepath', f'wk{week_number}.md'),
            status='generated',
            api_duration_seconds=api_call_duration
        )
        
        logger.info(f"Successfully generated lesson {lesson_id}")
        return lesson_dict, True
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating lesson: {error_msg}", exc_info=True)
        
        if fallback_on_error:
            logger.warning(f"Falling back to curriculum-based lesson. Error was: {error_msg}")
            fallback_lesson = _create_fallback_lesson(
                week_number=week_number,
                day_number=day_number,
                student_level=student_level,
                curriculum_data=curriculum_data if 'curriculum_data' in locals() else None,
                error_message=str(e)
            )
            
            # Store the fallback in database
            try:
                db.store_generated_lesson(
                    user_id=user_id,
                    lesson_id=fallback_lesson['lesson_id'],
                    week=week_number,
                    day=day_number,
                    curriculum_file=curriculum_data.get('filepath', f'wk{week_number}.md') if 'curriculum_data' in locals() else 'unknown',
                    status='fallback',
                    error_message=str(e)
                )
            except Exception as db_error:
                logger.error(f"Failed to store fallback lesson: {db_error}")
            
            return fallback_lesson, False
        else:
            raise LessonGenerationError(
                f"Failed to generate lesson for Week {week_number}, Day {day_number}: {str(e)}"
            )


def _call_gemini_for_lesson(
    system_prompt: str,
    lesson_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    timeout_seconds: int = 30,
    max_retries: int = 2
) -> Tuple[str, float]:
    """
    Call Gemini API to generate a lesson with retry logic.
    
    Args:
        system_prompt: System context prompt
        lesson_prompt: Main lesson generation prompt
        temperature: Sampling temperature (0.0-2.0, default 0.7 for balance)
        max_tokens: Maximum tokens in response
        timeout_seconds: API timeout
        max_retries: Number of retries if response is empty
    
    Returns:
        Tuple of (lesson_json_string, duration_seconds)
    
    Raises:
        Exception: If API call fails
    """
    import time
    
    try:
        # Get API client
        client = _get_genai_client()
        
        for attempt in range(max_retries + 1):
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{lesson_prompt}"
            
            start_time = time.time()
            
            # Make the API call with new SDK
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=64,
                )
            )
            
            duration = time.time() - start_time
            
            # Extract response text
            response_text = response.text if response else ""
            
            # Check if response is empty
            if response_text and response_text.strip():
                logger.info(f"Gemini API call completed in {duration:.2f}s (attempt {attempt + 1})")
                return response_text, duration
            else:
                if attempt < max_retries:
                    logger.warning(f"Empty response from Gemini (attempt {attempt + 1}/{max_retries + 1}), retrying...")
                    time.sleep(1)  # Brief delay before retry
                else:
                    logger.error(f"Gemini returned empty response after {max_retries + 1} attempts")
                    raise Exception("Gemini API returned empty response")
        
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}")
        raise


def _validate_lesson_json(response_text: str) -> Dict[str, Any]:
    """
    Validate and extract JSON from API response.
    
    The API should return pure JSON (no markdown, no extra text).
    If JSON is wrapped in markdown code blocks, extract it.
    
    Args:
        response_text: The API response text
    
    Returns:
        Parsed lesson dictionary
    
    Raises:
        ValueError: If JSON is invalid
    """
    try:
        # If response is wrapped in markdown code block, extract it
        if response_text.strip().startswith('```'):
            # Extract JSON from markdown code block
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end]
        
        # Parse JSON
        lesson_dict = json.loads(response_text)
        
        # Validate required fields
        required_fields = [
            'lesson_id', 'week', 'day', 'level', 'grammar', 'vocabulary', 
            'speaking', 'quiz', 'homework'
        ]
        
        missing_fields = [f for f in required_fields if f not in lesson_dict]
        if missing_fields:
            raise ValueError(f"Missing required lesson fields: {missing_fields}")
        
        # Validate grammar section
        grammar = lesson_dict.get('grammar', {})
        if not isinstance(grammar, dict) or 'target_form' not in grammar:
            raise ValueError("Grammar section missing target_form")
        
        # Validate vocabulary section
        vocab = lesson_dict.get('vocabulary', {})
        if not isinstance(vocab, dict) or 'words' not in vocab:
            raise ValueError("Vocabulary section missing words list")
        
        vocab_words = vocab.get('words', [])
        if len(vocab_words) < 10:
            logger.warning(f"Vocabulary has only {len(vocab_words)} words; expected 15+")
        
        # Validate quiz section
        quiz = lesson_dict.get('quiz', {})
        if not isinstance(quiz, dict) or 'questions' not in quiz:
            raise ValueError("Quiz section missing questions")
        
        questions = quiz.get('questions', [])
        if len(questions) < 3:
            raise ValueError(f"Quiz has only {len(questions)} questions; expected 4-5")

        # Normalize quiz question text and answers
        for question in questions:
            _normalize_quiz_question(question)
            
            # Validate listening questions have audio_text
            if _is_listening_question(question) and not question.get("audio_text"):
                raise ValueError("Listening quiz question missing audio_text")
            
            # Warn about fill-in-the-blank questions without base verb (but don't fail)
            if _is_fill_blank_question(question) and not question.get("base_verb"):
                logger.warning(
                    f"Fill-in-the-blank question missing base verb. "
                    f"Question: {question.get('question', 'N/A')}"
                )
        
        # Validate homework section
        homework = lesson_dict.get('homework', {})
        if not isinstance(homework, dict) or 'prompt' not in homework:
            raise ValueError("Homework section missing prompt")
        
        logger.info(f"Lesson JSON validated successfully")
        return lesson_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in response: {str(e)}")
        raise ValueError(f"Response is not valid JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Lesson validation failed: {str(e)}")
        raise


def _extract_answer_from_question_text(question_text: str) -> Tuple[str, Optional[str]]:
    if not question_text:
        return "", None

    separators = ["→", "->", "=>"]
    for sep in separators:
        if sep in question_text:
            parts = question_text.split(sep)
            clean_text = parts[0].strip()
            extracted = sep.join(parts[1:]).strip()
            return clean_text, extracted if extracted else None

    return question_text.strip(), None


def _normalize_quiz_question(question: Dict[str, Any]) -> None:
    question_text = question.get("question") or question.get("question_text") or ""
    clean_text, extracted_answer = _extract_answer_from_question_text(question_text)

    if clean_text:
        question["question"] = clean_text

    correct_answer = question.get("correct_answer")
    if (correct_answer is None or str(correct_answer).strip() == "") and extracted_answer:
        question["correct_answer"] = extracted_answer

    # For fill-in-the-blank questions: extract and store base verb(s)
    if _is_fill_blank_question(question):
        base_verb = _extract_base_verb_from_question(question_text)
        if base_verb:
            question["base_verb"] = base_verb

    audio_text = question.get("audio_text") or question.get("listen_text") or question.get("tts_text")
    if not audio_text and _is_listening_question(question):
        quoted = re.search(r"[\"“”'‘’]([^\"“”'‘’]+)[\"“”'‘’]", question_text)
        if quoted:
            question["audio_text"] = quoted.group(1).strip()
        else:
            # Fallback: use trailing clause after ':' if present
            if ":" in question_text:
                tail = question_text.split(":", 1)[1].strip()
                if tail:
                    question["audio_text"] = tail

    options = question.get("options")
    correct_answer = question.get("correct_answer")
    if isinstance(options, list) and options and correct_answer is not None:
        try:
            idx = int(correct_answer)
        except (ValueError, TypeError):
            idx = None
        if idx is not None and 0 <= idx < len(options):
            question["correct_answer"] = options[idx]


def _is_listening_question(question: Dict[str, Any]) -> bool:
    question_type = str(question.get("type") or "").lower()
    question_text = str(question.get("question") or question.get("question_text") or "").lower()
    return "listen" in question_type or "audio" in question_type or "listen" in question_text


def _is_fill_blank_question(question: Dict[str, Any]) -> bool:
    question_type = str(question.get("type") or "").lower()
    return "fill" in question_type or "fill_blank" in question_type or "fillblank" in question_type


def _extract_base_verb_from_question(question_text: str) -> Optional[str]:
    """
    Extract base verb(s) from parentheses in fill-in-the-blank question.
    Expected format: "Elle _____ (avoir) un chat." → returns "avoir"
    """
    if not question_text:
        return None
    
    # Look for verb in parentheses
    match = re.search(r'\(([^)]+)\)', question_text)
    if match:
        verb = match.group(1).strip()
        # Clean up common patterns like "avoir, être" → keep as is
        return verb if verb else None
    
    return None


def _create_fallback_lesson(
    week_number: int,
    day_number: int,
    student_level: str,
    curriculum_data: Optional[Dict[str, Any]] = None,
    error_message: str = ""
) -> Dict[str, Any]:
    """
    Create a fallback lesson when API generation fails.
    
    Returns a basic lesson structure that allows students to continue learning,
    though without full AI personalization.
    
    Args:
        week_number: Week number
        day_number: Day number
        student_level: CEFR level
        curriculum_data: Parsed curriculum (optional, use if available)
        error_message: What went wrong
    
    Returns:
        A basic lesson dictionary
    """
    from datetime import datetime, timezone
    
    logger.info(f"Creating fallback lesson for Week {week_number}, Day {day_number}")
    
    timestamp = datetime.now(timezone.utc).isoformat()
    curriculum_file = f'wk{week_number}.md'
    
    # If curriculum is available, use its data
    if curriculum_data:
        grammar = curriculum_data.get('grammar_target', {})
        vocab_items = curriculum_data.get('vocabulary_set', [])
        homework = curriculum_data.get('homework_task', {})
        speaking = curriculum_data.get('speaking_scenario', {})
        assessment = curriculum_data.get('assessment_checkpoint', {})
        theme = curriculum_data.get('theme', 'General')
        level = curriculum_data.get('level', student_level)
    else:
        # Minimal fallback data
        grammar = {'form': 'Basic French', 'complexity': 1}
        vocab_items = []
        homework = {'type': 'text', 'task_description': 'Write about yourself'}
        speaking = {'domain': 'Greetings'}
        assessment = {}
        theme = 'Basic French'
        level = student_level
    
    scaffolding_steps = grammar.get('scaffolding', []) or []
    
    # Build a comprehensive explanation from scaffolding steps
    explanation_parts = []
    
    if scaffolding_steps:
        # Extract meaningful steps to build explanation
        for i, step in enumerate(scaffolding_steps):
            if isinstance(step, dict):
                explanation_parts.append(step.get('explanation', str(step)))
            elif isinstance(step, str):
                # Skip short titles/references (< 50 chars)
                if len(step) > 50:
                    explanation_parts.append(step)
    
    # If we have reasonable explanations, use them; otherwise create a basic one
    if explanation_parts and any(len(p) > 100 for p in explanation_parts):
        # Join explanations with paragraph breaks
        explanation = "\n\n".join([p for p in explanation_parts if len(p) > 100])
    else:
        # Create a fallback explanation from grammar target info
        form = grammar.get('form', 'this grammar structure')
        complexity = grammar.get('complexity', 5)
        explanation = f"""**Grammar Target: {form}** (Complexity: {complexity}/10)

This is an important grammar concept for your current level. To understand {form} better:

1. **Definition & Purpose**: {form} is used toexpress specific ideas in French. Understanding when and how to use it is crucial for effective communication at this level.

2. **Common Patterns**: Look for {form} in the provided examples. Notice how it changes based on the subject, context, and tense.

3. **Practice**: Complete the exercises below to practice using {form}. Pay attention to how natives speakers use this structure.

4. **Real-World Usage**: You'll encounter {form} in everyday conversations, written texts, and media.

5. **Next Steps**: Once you're comfortable with this structure, you'll be able to use it naturally in your own French expression.

For a complete in-depth explanation, please refer to your curriculum file (wk{week_number}.md)."""

    quiz_questions = []
    for idx, q in enumerate(assessment.get('questions', []) or []):
        quiz_questions.append({
            'id': f'q{idx + 1}',
            'type': 'short',
            'question': q.get('question', ''),
            'correct_answer': q.get('expected_answer', '')
        })

    fallback_lesson = {
        'lesson_id': f"week_{week_number}_day_{day_number}_{timestamp}",
        'week': week_number,
        'day': day_number,
        'level': level,
        'theme': theme,
        'estimated_duration_minutes': 45,
        'is_fallback': True,
        'fallback_reason': f"API generation failed: {error_message[:100]}",
        
        'grammar': {
            'target_form': grammar.get('form', 'Review from curriculum'),
            'complexity_rating': grammar.get('complexity', 5),
            'explanation': explanation,
            'key_rules': scaffolding_steps[1:4],
            'examples': grammar.get('examples', [])[:4],
            'common_errors': []
        },
        
        'vocabulary': {
            'semantic_domain': theme,
            'words': vocab_items if vocab_items else [
                {'word': 'bonjour', 'definition': 'hello', 'pronunciation_tip': 'bon-ZHOOR'},
                {'word': 'au revoir', 'definition': 'goodbye', 'pronunciation_tip': 'oh ruh-vwahr'},
            ]
        },
        
        'speaking': {
            'scenario_domain': speaking.get('domain', 'General conversation'),
            'scenario_prompt': speaking.get('example_interaction', ['Practice basic conversation'])[0] if speaking.get('example_interaction') else 'Have a brief conversation with the AI tutor',
            'ai_opening': f"Bonjour! Je suis ton tuteur français. Parlons ensemble.",
            'interaction_tier': speaking.get('interaction_tier', 1),
            'target_phrases': speaking.get('example_interaction', [])[:4] or ['Greetings', 'Basic introductions'],
            'success_criteria': 'Respond naturally to the AI tutor\'s questions'
        },
        
        'quiz': {
            'instruction': 'Answer the following review questions',
            'questions': quiz_questions if quiz_questions else [
                {
                    'id': 'q1',
                    'type': 'fill_blank',
                    'question': 'Je ___ étudiant(e).',
                    'options': ['suis', 'es', 'est', 'sommes'],
                    'correct_answer': 'suis',
                    'explanation': 'Use "suis" with "je" (I am)'
                },
                {
                    'id': 'q2',
                    'type': 'translation',
                    'question': 'What does "Bonjour" mean?',
                    'options': ['Hello', 'Goodbye', 'Thank you', 'Please'],
                    'correct_answer': 'Hello',
                    'explanation': '"Bonjour" is the standard French greeting'
                }
            ]
        },
        
        'homework': {
            'type': homework.get('type', 'text'),
            'prompt': homework.get('task_description', 'Write about yourself in French'),
            'detailed_instructions': 'Review the curriculum file for this week\'s homework assignment',
            'minimum_requirements': {
                'text_length': '6-10 sentences' if homework.get('type') == 'text' else None,
                'vocabulary_words': homework.get('task_description', 'Review curriculum')
            },
            'rubric': homework.get('rubric', ['Complete the assignment', 'Use correct grammar', 'Include vocabulary from the lesson']),
            'pass_threshold': homework.get('pass_threshold', 3),
            'example_response': 'Refer to curriculum file'
        },
        
        'metadata': {
            'generated_at': timestamp,
            'curriculum_file': f'wk{week_number}.md',
            'personalization_applied': {
                'weakness_addressed': False,
                'extra_scaffolding_given': False,
                'extra_examples_given': False,
                'complexity_adjusted': 'none'
            },
            'warning': 'This is a fallback lesson created because the AI lesson generation encountered an error. Please check the curriculum file for complete content.'
        }
    }
    
    return fallback_lesson


# =============================================================================
# NEW CURRICULUM SYSTEM (Research/NEW_CURRICULUM_REDESIGNED/)
# =============================================================================

def generate_lesson_from_redesigned_curriculum(
    week_number: int,
    day_number: int,
    user_id: int = 1
) -> Dict[str, Any]:
    """
    Generate a lesson from the NEW redesigned curriculum format.
    
    This function uses FIXED curriculum content (no AI generation needed).
    The curriculum files already contain:
    - Grammar explanations (5-paragraph format) ✅
    - Vocabulary (5 words with examples) ✅
    - Examples (50 questions with content identifiers) ✅
    
    AI is only used for:
    - Speaking scenario generation
    - Homework evaluation
    - Exam grading
    
    Args:
        week_number: Week number (1-52)
        day_number: Day number (1-7)
        user_id: Student user ID (default 1)
    
    Returns:
        Complete lesson dictionary ready for frontend display
    
    Example output structure:
    {
        'lesson_id': 'week_1_day_1',
        'week': 1,
        'day': 1,
        'cefr_level': 'A1.1',
        'grammar_topic': 'Verb être (I am, You are)',
        'grammar_explanation': '...(5-paragraph HTML)...',
        'vocabulary': [...5 words...],
        'quiz_questions': [...8-10 selected from 50...],
        'speaking_tier': 1,
        'duration': '30 minutes'
    }
    """
    import quiz_parser  # Import here to avoid circular dependency
    
    # Load curriculum day
    try:
        day_data = curriculum_loader.load_redesigned_curriculum_day(week_number, day_number)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to load redesigned curriculum: {e}")
        raise LessonGenerationError(f"Curriculum not found for Week {week_number} Day {day_number}")
    
    # Get quiz questions (8-10 randomly selected from 50)
    quiz_questions = quiz_parser.get_quiz_questions(week_number, day_number, count=8)
    
    # Format quiz questions for display
    formatted_questions = [
        quiz_parser.format_question_for_display(q) for q in quiz_questions
    ]
    
    # Build lesson dictionary
    lesson = {
        'lesson_id': f"week_{week_number}_day_{day_number}",
        'week': week_number,
        'day': day_number,
        'cefr_level': day_data.get('cefr_level', 'A1.1'),
        'grammar_topic': day_data.get('grammar_topic', ''),
        'vocabulary_domain': day_data.get('vocabulary_domain', ''),
        'content_identifiers': day_data.get('content_identifiers', []),
        'speaking_tier': day_data.get('speaking_tier', 1),
        'duration': day_data.get('duration', '30 minutes'),
        
        # FIXED content from curriculum
        'grammar_explanation': _format_grammar_as_html(day_data.get('grammar_explanation', '')),
        'vocabulary': day_data.get('vocabulary', []),
        
        # Quiz (selected randomly)
        'quiz_questions': formatted_questions,
        'total_available_questions': len(day_data.get('examples', [])),  # 50
        
        # Metadata
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'source': 'redesigned_curriculum',
        'curriculum_file': day_data.get('filepath', ''),
        'is_ai_generated': False  # Content is FIXED, not AI-generated
    }
    
    # Store in database
    try:
        db.store_generated_lesson(
            user_id=user_id,
            lesson_id=lesson['lesson_id'],
            week=week_number,
            day=day_number,
            curriculum_file=day_data.get('filepath', ''),
            status='loaded_from_curriculum',
            api_duration_seconds=0  # No API call
        )
    except Exception as e:
        logger.warning(f"Failed to store lesson in database: {e}")
    
    return lesson


def _format_grammar_as_html(grammar_text: str) -> str:
    """
    Convert markdown-style grammar explanation to HTML.
    
    Handles:
    - Bold text: **text** → <strong>text</strong>
    - Tables (markdown) → HTML tables
    - Bullet points → <ul><li>
    - Section headers: #### → <h4>
    """
    if not grammar_text:
        return "<p>Grammar explanation not available.</p>"
    
    html = grammar_text
    
    # Convert markdown headers
    html = re.sub(r'####\s+(.+)', r'<h4>\1</h4>', html)
    html = re.sub(r'###\s+(.+)', r'<h3>\1</h3>', html)
    html = re.sub(r'##\s+(.+)', r'<h2>\1</h2>', html)
    
    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert markdown tables to HTML
    html = _convert_markdown_tables_to_html(html)
    
    # Convert lists (lines starting with -)
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('- ') or stripped.startswith('• '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item_text = stripped[2:].strip() if stripped[0] in ['-', '•'] else stripped
            result_lines.append(f'  <li>{item_text}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            
            # Wrap non-empty lines in <p> if not already HTML
            if stripped and not stripped.startswith('<'):
                result_lines.append(f'<p>{stripped}</p>')
            else:
                result_lines.append(line)
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)


def _convert_markdown_tables_to_html(text: str) -> str:
    """Convert markdown tables to HTML tables."""
    # Pattern: | header | header |
    #          |--------|--------|
    #          | cell   | cell   |
    
    table_pattern = r'(\|.+\|\n\|[-:\s|]+\|\n(?:\|.+\|\n?)+)'
    
    def replace_table(match):
        table_md = match.group(1)
        lines = [line.strip() for line in table_md.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return table_md  # Invalid table
        
        # Parse header
        header_cells = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        
        # Parse rows (skip separator line[1])
        rows = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                rows.append(cells)
        
        # Build HTML
        html = ['<table class="grammar-table">']
        html.append('  <thead>')
        html.append('    <tr>')
        for cell in header_cells:
            html.append(f'      <th>{cell}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
        html.append('  <tbody>')
        for row in rows:
            html.append('    <tr>')
            for cell in row:
                html.append(f'      <td>{cell}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
        html.append('</table>')
        
        return '\n'.join(html)
    
    return re.sub(table_pattern, replace_table, text)
