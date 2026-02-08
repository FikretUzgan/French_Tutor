"""
AI Prompts Module

Contains all prompt templates for lesson generation, grading, feedback, etc.
Each prompt is documented with its purpose, expected inputs, outputs, and token estimates.
"""

# System Prompt - Sets the overall context and role for the AI
SYSTEM_PROMPT = """You are an expert French language tutor with 15+ years of teaching experience. 
Your role is to create personalized, engaging French lessons for learners at CEFR levels A1.1 through B2.2.

Your core responsibilities:
1. **Curriculum Fidelity**: Strictly follow the provided curriculum for the week, ensuring all learning objectives are met.
2. **Personalization**: Adapt explanations and examples based on student weaknesses and learning history.
3. **Scaffolding**: Break complex grammar into step-by-step explanations with progressively difficult examples.
4. **Engagement**: Use context-relevant scenarios (ordering coffee, hotel check-in, etc.) to make lessons practical.
5. **Clear Feedback**: Provide specific, actionable corrections with positive reinforcement.

Teaching Philosophy:
- Start with what students KNOW (review previous weeks if needed)
- Use French as much as possible, but translate key terms for beginners (A1)
- Celebrate effort and progress, even small wins
- Correct errors gently: "Good try! Notice that..."
- Always provide context for grammar rules (When do we use this? Why is this important?)

You have access to:
- The curriculum for this week (grammar target, vocabulary, learning outcomes)
- Student's previous week completions
- Student's documented weaknesses (topics where they struggled)
- Expected homework submission topics

Output Format: You MUST respond with valid JSON (no markdown, no extra text before/after the JSON).

Do NOT hallucinate content. If something is not in the curriculum, do NOT invent it.
Always stay within the specified complexity level for the student's CEFR level."""

# Token estimate: ~450 tokens

# Main Lesson Generation Prompt
LESSON_GENERATION_PROMPT = """Based on the curriculum provided and student profile below, generate a complete, personalized lesson for Week {week_number}, Day {day_number}.

CURRICULUM FOR THIS WEEK:
{curriculum_data}

STUDENT PROFILE:
- Current CEFR Level: {student_level}
- Completed Weeks: {completed_weeks}
- Documented Weaknesses: {weaknesses}
- Struggled Topics: {struggled_topics}

YOUR TASK:
Generate a JSON lesson object with these sections:

{{
  "lesson_id": "week_{week_number}_day_{day_number}_{timestamp}",
  "week": {week_number},
  "day": {day_number},
  "level": "{student_level}",
  "theme": "{curriculum_theme}",
  "estimated_duration_minutes": 45,
  
  "grammar": {{
    "target_form": "the main grammar structure for this week",
    "complexity_rating": 1-10,
    "explanation": "Clear, step-by-step explanation (2-3 paragraphs). For beginners, include English translations. For advanced, think about usage nuances.",
    "conjugation_table": {{
      "headers": ["pronoun", "form", "example"],
      "rows": [
        {{"pronoun": "je", "form": "suis", "example": "Je suis français."}}
      ]
    }},
    "key_rules": [
      "Rule 1 with explanation",
      "Rule 2 with explanation"
    ],
    "examples": [
      {{"french": "Je suis étudiant.", "english": "I am a student.", "usage_context": "Introducing yourself"}},
      // Include 5-6 examples, progressively more complex
    ],
    "common_errors": [
      {{"error": "Je es fatigué", "correction": "Je suis fatigué", "explanation": "Subject-verb agreement"}}
    ]
  }},
  
  "vocabulary": {{
    "semantic_domain": "the word families/theme",
    "words": [
      {{"word": "bonjour", "definition": "hello", "pronunciation_tip": "bon-JOR, emphasis on last syllable", "context_example": "Bonjour, comment ça va?"}},
      // MUST include ALL vocabulary words from the curriculum (15-21 words)
      // Prioritize words from the curriculum vocabulary set
    ]
  }},
  
  "speaking": {{
    "scenario_domain": "the interaction context (e.g., 'First meeting', 'Coffee shop order')",
    "scenario_prompt": "Your interaction prompt that tells the student what to do",
    "ai_opening": "How the AI tutor will start the conversation",
    "interaction_tier": 1-3,
    "target_phrases": ["phrase 1", "phrase 2"],
    "success_criteria": "What counts as a good response"
  }},
  
  "quiz": {{
    "instruction": "Instructions for the quiz",
    "questions": [
      {{
        "id": "q1",
        "type": "conjugation",
        "question": "Conjugate the verb in parentheses: Je (être) heureux.",
        "options": ["suis", "es", "sommes", "êtes"],
        "correct_answer": "suis",
        "explanation": "Use 'suis' with 'je' (I am). The subject is singular first person."
      }},
      // 4-5 questions total, mix of:
      // - conjugation (complete the verb)
      // - translation (French → English or vice versa)
      // - fill_blank (complete the sentence)
      // - multiple_choice (select correct form)
    ]
  }},
  
  "homework": {{
    "type": "text|audio|both",
    "prompt": "Clear prompt explaining what to write or say (1-2 sentences)",
    "detailed_instructions": "Step-by-step instructions with examples",
    "minimum_requirements": {{
      "text_length": "6-10 sentences",
      "vocabulary_words": 5,
      "grammar_structures": ["target verb form", "other grammar"],
      "spoken_duration_seconds": null  // Only if audio
    }},
    "rubric": [
      "Use at least 5 vocabulary words from today's lesson correctly",
      "Conjugate the target verb correctly at least 3 times",
      "Sentences are understandable (grammar errors A1 level or correctable)",
      "Make a genuine effort (minimum 6 sentences for text)"
    ],
    "pass_threshold": 4,
    "example_response": "Bonjour, je m'appelle Fikret. Je suis turc. Je suis étudiant..."
  }},
  
  "metadata": {{
    "generated_at": "{timestamp}",
    "curriculum_file": "{curriculum_file}",
    "personalization_applied": {{
      "weakness_addressed": ["topic 1", "topic 2"],
      "extra_scaffolding_given": true,
      "extra_examples_given": true,
      "complexity_adjusted": "up|down|none"
    }}
  }}
}}

CRITICAL REQUIREMENTS FOR YOUR OUTPUT:
1. VALID JSON ONLY: Your response must be parseable JSON. Test it before submitting.
2. VOCABULARY FIDELITY: Use ALL vocabulary words from the curriculum. Do not skip words.
3. GRAMMAR ACCURACY: Verify all French is correct. No invented words or structures.
4. COMPLEXITY: Match {student_level} level (A1.1 → very simple, B2.2 → advanced nuances).
5. WEAKNESSES: If student has documented weaknesses, add extra examples/scaffolding in that grammar area.
6. EXAMPLES: Include 5-6 realistic, contextual examples for the grammar target.
7. DATETIME: Use ISO format for timestamp (e.g., 2026-02-08T14:30:00Z).

COMMON MISTAKES TO AVOID:
- Do NOT invent curriculum content. Stick to what was provided.
- Do NOT make grammar mistakes (this is especially critical).
- Do NOT give homework that requires vocabulary NOT in the lesson.
- Do NOT make examples too complex for the level.
- Do NOT forget to include pronunciation tips for vocabulary.

If a student has struggled with {struggled_topics}, add an extra section in grammar explaining common mistakes and misconceptions."""

# Token estimate: ~800-1000 tokens (varies with personalization data)

# Weakness Personalization Sub-Prompt
WEAKNESS_PERSONALIZATION_SUBPROMPT = """The student has struggled with these topics in the past:
{weaknesses_list}

ADAPT the LESSON_GENERATION_PROMPT as follows:
1. In the grammar section, add 2-3 extra examples specifically targeting the weakness(es).
2. In common_errors, include the exact type of mistake this student has made before.
3. In the homework rubric, add a specific criterion related to the weakness.
4. Add a "Remediation Notes" section with tips for the AI tutor during speaking practice.

Example addition to grammar section:
"EXTRA SCAFFOLDING FOR PAST STRUGGLES:
Since you had trouble with [topic], pay special attention to:
- [specific rule]
- [common error pattern]
Example that clarifies the confusion: [custom example]"

Make sure the extra scaffolding is encouraging, not discouraging ("Let's strengthen this!" not "You kept getting this wrong")."""

# Token estimate: ~150-200 tokens

# Homework Evaluation Prompt
HOMEWORK_EVALUATION_PROMPT = """You are evaluating a student's homework submission for Week {week_number}, Day {day_number}.

ASSIGNMENT:
{homework_assignment}

STUDENT'S SUBMISSION:
{student_submission}

ORIGINAL LESSON CONTENT (for context):
{lesson_content}

EVALUATE using the rubric above and provide:
{{
  "submission_id": "{submission_id}",
  "week": {week_number},
  "day": {day_number},
  "student_level": "{student_level}",
  "rubric_scores": [
    {{"criterion": "criterion 1", "met": true, "comment": "explanation"}},
    {{"criterion": "criterion 2", "met": false, "comment": "explanation"}}
  ],
  "passed": true,  // true if pass_threshold met
  "total_criteria_met": 4,
  "total_criteria": 4,
  "strengths": [
    "You used the verb perfectly!",
    "Great word choice with..."
  ],
  "improvements": [
    {{"error": "incorrect form", "correction": "correct form", "explanation": "why this is better"}},
  ],
  "overall_feedback": "2-3 sentence summary, encouraging but honest",
  "next_steps": "If passed: Ready for next lesson! | If failed: Try again with ...",
  "topics_for_future_review": ["topic if weak"]
}}

TONE:
- Specific: Not just "Good job!" but "Your use of the passé composé in sentence 3 was perfect!"
- Encouraging: Celebrate what they did right first
- Constructive: Explain WHY corrections matter
- Clear: Use examples, not abstract rules

Only set passed=true if pass_threshold criteria are met. If not, suggest a remedial attempt."""

# Token estimate: ~600-800 tokens

# Speaking Feedback Prompt
SPEAKING_FEEDBACK_PROMPT = """The student just completed a speaking practice interaction:

SCENARIO: {scenario}
TARGET SKILL: {target_skill}
INTERACTION TIER: {interaction_tier}

STUDENT'S RESPONSE(S):
{student_transcription}

ORIGINAL SCENARIO CONTEXT:
{scenario_details}

Provide feedback:
{{
  "interaction_quality": 5,  // 1-5 scale
  "pronunciation_quality": 4,  // 1-5 scale
  "grammar_accuracy": 4,  // 1-5 scale
  "vocabulary_usage": 5,  // 1-5 scale
  "confidence_level": "attempted|secure|fluent",
  
  "strengths": [
    "You used [structure] perfectly!",
  ],
  "pronunciation_notes": [
    {{"word": "bonjour", "your_pronunciation": "bon-JOR", "correct_pronunciation": "bon-ZHOOR", "tip": "The 'j' in French is pronounced like 'zh'"}},
  ],
  "grammar_feedback": [
    {{"phrase": "Je suis étudiant", "grade": "perfect", "note": null}},
    {{"phrase": "Tu aller", "grade": "needs_work", "note": "Should be 'Tu vas' (you go). Remember, 'aller' is a special verb."}}
  ],
  "overall_feedback": "Great effort! You were confident and your pronunciation of [word] was excellent. Next time, watch out for [structure] — let's practice that together.",
  "suggested_next_attempt": "Try the same scenario but focus on using [target_structure]. You've got this!",
  
  "topics_to_reinforce": ["topic"]
}}

FEEDBACK STYLE:
- Specific & actionable: Reference exact words, not vague praise
- Encouraging: Start with 1-2 genuine strengths
- Constructive: Suggest one thing to improve
- Reachable: Make goals attainable (not "speak like a native")"""

# Token estimate: ~400-500 tokens

# Quiz Evaluation Prompt
QUIZ_EVALUATION_PROMPT = """Evaluate the student's quiz responses. Quiz info:

QUIZ: Week {week_number}, Day {day_number}
STUDENT_LEVEL: {student_level}
CURRICULUM_TARGET: {grammar_target}

QUIZ QUESTIONS:
{quiz_questions}

STUDENT ANSWERS:
{student_answers}

{{
  "quiz_id": "{quiz_id}",
  "questions_total": 5,
  "questions_correct": 4,
  "percentage_correct": 80,
  "passed": true,  // true if >= 70%
  "question_details": [
    {{
      "question_id": "q1",
      "question": "Conjugate: Je (être) heureux",
      "student_answer": "suis",
      "correct_answer": "suis",
      "is_correct": true,
      "feedback": "Perfect!"
    }},
  ],
  "overall_assessment": "You mastered the target conjugation! Your success on questions 1,2,4 shows solid understanding. Question 3 stumped you - let's revisit [structure].",
  "weak_areas": [],
  "strong_areas": ["être conjugation"],
  "recommendation": "Move to speaking practice" | "Review the grammar section again"
}}

Be fair but honest. A correct answer is correct. A near-miss is still incorrect (but comment on it)."""

# Token estimate: ~300-400 tokens

def get_system_prompt() -> str:
    """Return the system prompt."""
    return SYSTEM_PROMPT


def get_lesson_generation_prompt(
    week_number: int,
    day_number: int,
    student_level: str,
    completed_weeks: list,
    weaknesses: list,
    struggled_topics: list,
    curriculum_data: dict,
    curriculum_theme: str,
    timestamp: str
) -> str:
    """
    Build the main lesson generation prompt with student context.
    
    Args:
        week_number: Week (1-52)
        day_number: Day (1-7)
        student_level: CEFR level (e.g., 'A1.1')
        completed_weeks: List of completed week numbers
        weaknesses: List of weakness descriptions
        struggled_topics: List of topics student struggled with
        curriculum_data: Parsed curriculum data
        curriculum_theme: Week theme
        timestamp: ISO format timestamp
    
    Returns:
        Formatted prompt string
    """
    # Format completed weeks nicely
    completed_weeks_str = ', '.join(map(str, completed_weeks)) if completed_weeks else "None yet"
    
    # Format weaknesses
    weaknesses_str = '\n'.join([f"- {w}" for w in weaknesses]) if weaknesses else "No documented weaknesses yet"
    
    # Format struggled topics
    struggled_str = ', '.join(struggled_topics) if struggled_topics else "None identified"
    
    # Format curriculum data for inclusion
    curriculum_str = _format_curriculum_for_display(curriculum_data)
    
    prompt = LESSON_GENERATION_PROMPT.format(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        completed_weeks=completed_weeks_str,
        weaknesses=weaknesses_str,
        struggled_topics=struggled_str,
        curriculum_data=curriculum_str,
        curriculum_theme=curriculum_theme,
        timestamp=timestamp
    )
    
    return prompt


def _format_curriculum_for_display(curriculum_data: dict) -> str:
    """Format curriculum data as a readable string for prompt inclusion."""
    parts = []
    
    parts.append(f"**Theme**: {curriculum_data.get('theme', 'N/A')}")
    parts.append(f"**Level**: {curriculum_data.get('level', 'N/A')}")
    
    parts.append("\n**Learning Outcomes:**")
    for outcome in curriculum_data.get('learning_outcomes', []):
        parts.append(f"- {outcome}")
    
    grammar = curriculum_data.get('grammar_target', {})
    parts.append(f"\n**Grammar Target**: {grammar.get('form', 'N/A')}")
    parts.append(f"**Complexity**: {grammar.get('complexity', 5)}/10")
    if grammar.get('examples'):
        parts.append("**Examples:**")
        for ex in grammar.get('examples', [])[:5]:
            parts.append(f"- {ex}")
    
    vocab = curriculum_data.get('vocabulary_set', [])
    parts.append(f"\n**Vocabulary** ({len(vocab)} words):")
    for item in vocab:
        parts.append(f"- {item['word']} – {item['definition']}")
    
    speaking = curriculum_data.get('speaking_scenario', {})
    parts.append(f"\n**Speaking Scenario**: {speaking.get('domain', 'N/A')}")
    
    homework = curriculum_data.get('homework_task', {})
    parts.append(f"\n**Homework Type**: {homework.get('type', 'N/A')}")
    
    return '\n'.join(parts)


def get_homework_evaluation_prompt(
    week_number: int,
    day_number: int,
    student_level: str,
    homework_assignment: dict,
    student_submission: str,
    lesson_content: dict,
    submission_id: str
) -> str:
    """Build homework evaluation prompt."""
    homework_str = _format_homework_rubric(homework_assignment)
    lesson_str = _format_lesson_content(lesson_content)
    
    prompt = HOMEWORK_EVALUATION_PROMPT.format(
        week_number=week_number,
        day_number=day_number,
        homework_assignment=homework_str,
        student_submission=student_submission,
        lesson_content=lesson_str,
        submission_id=submission_id,
        student_level=student_level
    )
    
    return prompt


def _format_homework_rubric(homework_assignment: dict) -> str:
    """Format homework assignment for prompt inclusion."""
    parts = []
    parts.append(f"Type: {homework_assignment.get('type', 'N/A')}")
    parts.append(f"Prompt: {homework_assignment.get('task_description', 'N/A')}")
    
    rubric = homework_assignment.get('rubric', [])
    parts.append("\nRubric (must meet all for passing):")
    for i, criterion in enumerate(rubric, 1):
        parts.append(f"{i}. {criterion}")
    
    parts.append(f"\nPass Threshold: {homework_assignment.get('pass_threshold', 4)}/{len(rubric)} criteria")
    
    return '\n'.join(parts)


def _format_lesson_content(lesson_content: dict) -> str:
    """Format lesson content for evaluation context."""
    parts = []
    
    grammar = lesson_content.get('grammar', {})
    parts.append(f"Grammar Target: {grammar.get('target_form', 'N/A')}")
    parts.append(f"Key Rules: {', '.join(grammar.get('key_rules', []))}")
    
    vocab = lesson_content.get('vocabulary', {})
    words = [w['word'] for w in vocab.get('words', [])[:10]]
    parts.append(f"Vocabulary: {', '.join(words)}...")
    
    return '\n'.join(parts)


def get_speaking_feedback_prompt(
    scenario: str,
    target_skill: str,
    interaction_tier: int,
    student_transcription: str,
    scenario_details: dict
) -> str:
    """Build speaking feedback prompt."""
    details_str = _format_scenario_details(scenario_details)
    
    prompt = SPEAKING_FEEDBACK_PROMPT.format(
        scenario=scenario,
        target_skill=target_skill,
        interaction_tier=interaction_tier,
        student_transcription=student_transcription,
        scenario_details=details_str
    )
    
    return prompt


def _format_scenario_details(scenario_details: dict) -> str:
    """Format scenario details for prompt."""
    parts = []
    parts.append(f"Domain: {scenario_details.get('domain', 'N/A')}")
    
    if scenario_details.get('example_interaction'):
        parts.append("Example Interaction:")
        for line in scenario_details['example_interaction'][:5]:
            parts.append(f"  {line}")
    
    return '\n'.join(parts)


def get_quiz_evaluation_prompt(
    week_number: int,
    day_number: int,
    student_level: str,
    grammar_target: str,
    quiz_questions: list,
    student_answers: dict,
    quiz_id: str
) -> str:
    """Build quiz evaluation prompt."""
    questions_str = _format_quiz_questions(quiz_questions)
    answers_str = _format_student_answers(student_answers)
    
    prompt = QUIZ_EVALUATION_PROMPT.format(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        grammar_target=grammar_target,
        quiz_questions=questions_str,
        student_answers=answers_str,
        quiz_id=quiz_id
    )
    
    return prompt


def _format_quiz_questions(questions: list) -> str:
    """Format quiz questions for prompt."""
    parts = []
    for i, q in enumerate(questions, 1):
        parts.append(f"{i}. {q.get('question', 'N/A')}")
        if q.get('options'):
            for opt in q['options']:
                parts.append(f"   - {opt}")
    return '\n'.join(parts)


def _format_student_answers(answers: dict) -> str:
    """Format student answers for prompt."""
    parts = []
    for qid, answer in answers.items():
        parts.append(f"Q{qid}: {answer}")
    return '\n'.join(parts)
