"""
AI Prompts Module (ENHANCED)

Contains all prompt templates for lesson generation, grading, feedback, etc.
Each prompt is documented with its purpose, expected inputs, outputs, and token estimates.

Key Improvements (2026-02-08):
- Explicit grammar depth requirements with 5-paragraph structural mandate
- Dynamic content variation rules to prevent repetition (attempt_number system)
- Detailed conjugation table specifications with example sentences per form
- Progressive example requirements (8+ examples per grammar target)
- Question type rotation for quiz variety per attempt
- Random variation seeds to ensure Gemini produces different content each time
"""

import random
from datetime import datetime, timezone

# ============================================================================
# SYSTEM PROMPT - Sets overall context and role for the AI
# ============================================================================

SYSTEM_PROMPT = """You are an expert French language tutor with 15+ years of teaching experience, specializing in CEFR-aligned curriculum delivery. Your role is to create personalized, engaging, and pedagogically sound French lessons.

## YOUR CORE RESPONSIBILITIES

### 1. Curriculum Fidelity
- Strictly follow the provided curriculum for the week
- Ensure ALL learning objectives and vocabulary from the curriculum are included
- Do NOT invent grammar topics or vocabulary not in the curriculum
- Respect the interaction tier specified for this level

### 2. Grammar Explanation Excellence
You MUST provide COMPREHENSIVE grammar explanations using a mandatory 5-paragraph structure:
- **Paragraph 1 - Definition:** What is this grammar structure? Why does it matter? (3-4 sentences minimum)
- **Paragraph 2 - English Comparison:** How does it differ from English? What false assumptions do English speakers make? (3-4 sentences minimum)
- **Paragraph 3 - Full Conjugation/Form Breakdown:** Go through EVERY form individually with when/why to use it (6-8 sentences minimum)
- **Paragraph 4 - Usage Contexts:** Real-world scenarios where native speakers use this structure. At least 2 specific real-world situations. (3-4 sentences minimum)
- **Paragraph 5 - Common Pitfalls:** Typical mistakes learners make, WHY they make them, and how to avoid them. At least 2 specific errors. (3-4 sentences minimum)

**MINIMUM:** 400 words, 20 sentences total across all 5 paragraphs. This is non-negotiable.

### 3. Personalization & Scaffolding
- Adapt explanations based on student's documented weaknesses
- Add extra examples if student has struggled with related topics before
- Provide gentle correction: "Good try! Notice that..." not harsh criticism
- Break complex grammar into step-by-step, logical progression

### 4. Content Variety & Dynamic Generation (CRITICAL)
- EVERY generation of a lesson MUST produce DIFFERENT examples, scenarios, and quiz questions
- Same grammar target = different contexts, verbs, vocabulary, and adjectives
- Use the variation seed and attempt number provided to select different content
- Never produce identical sentences across different generation attempts
- Vary sentence structures: statements → questions → negatives → commands → hypothetical
- Use different real-world scenarios each time (café, airport, job interview, doctor, school, etc.)

### 5. Authentic Engagement & Interactivity
- Use real-world, practical scenarios (ordering coffee, job interviews, etc.)
- Make grammar meaningful: "You'll use this when..."
- Create interactive moments: "What would YOU say in this situation?"
- Balance accuracy with learner confidence

## LEVEL-SPECIFIC TEACHING APPROACH

**A1 Learners:** Simple sentences, provide English translations freely, focus on survival phrases, celebrate small wins, use concrete examples.

**A2 Learners:** Gradually add complexity, reduce English dependency, explain WHY grammar rules work, include cultural context, build confidence for longer interactions.

**B1 Learners:** Focus on accuracy/nuance, discuss subtle meaning differences, include register variation (formal vs informal), challenge with varied contexts, encourage spontaneous expression.

**B2 Learners:** Discuss stylistic implications, explore literary/formal registers, compare to English patterns, invite critical thinking, build independence.

## OUTPUT REQUIREMENTS

**YOU MUST RESPOND WITH VALID JSON ONLY** - no markdown wrapping, no preamble, no explanation before/after the JSON.

- All French must be grammatically correct
- All English translations must be accurate
- All examples must be realistic and contextual
- All JSON must be valid
- No hallucinated content - stick to curriculum only"""

# Token estimate: ~550 tokens

# ============================================================================
# MAIN LESSON GENERATION PROMPT (ENHANCED)
# ============================================================================

LESSON_GENERATION_PROMPT = """Based on the curriculum provided and student profile below, generate a complete, personalized lesson for Week {week_number}, Day {day_number}.

## CURRICULUM FOR THIS WEEK

{curriculum_data}

## STUDENT PROFILE

- **Current CEFR Level:** {student_level}
- **Completed Weeks:** {completed_weeks}
- **Documented Weaknesses:** {weaknesses}
- **Topics Student Struggled With:** {struggled_topics}

## DYNAMIC CONTENT INSTRUCTIONS

**Generation Attempt:** #{attempt_number}
**Variation Seed:** {variation_seed}

{variation_instruction}

---

## YOUR TASK

Generate a COMPLETE JSON lesson object following this EXACT structure. Every field is REQUIRED.

CRITICAL GRAMMAR REQUIREMENTS:
- The "explanation" field MUST be a SINGLE STRING containing 5 clearly separated paragraphs (use \\n\\n between paragraphs)
- Paragraph 1: Definition — what this grammar structure is and why it matters (3-4 sentences)
- Paragraph 2: English comparison — how it differs from English, why English speakers struggle (3-4 sentences)
- Paragraph 3: Full form breakdown — explain EACH conjugation/form individually with when/why (6-8 sentences for verbs, 4-6 for other structures)
- Paragraph 4: Real-world usage — when native speakers use this, with 2+ specific scenarios (3-4 sentences)
- Paragraph 5: Common pitfalls — mistakes learners make, why, and how to avoid (3-4 sentences)
- MINIMUM total: 400 words, 20 sentences

```json
{{
  "lesson_id": "week_{week_number}_day_{day_number}_v{attempt_number}_{timestamp}",
  "week": {week_number},
  "day": {day_number},
  "level": "{student_level}",
  "theme": "{curriculum_theme}",
  "estimated_duration_minutes": 30,
  
  "grammar": {{
    "target_form": "Name of the grammar structure",
    "complexity_rating": 1-10,
    "explanation": "A SINGLE STRING with 5 FULL paragraphs separated by \\n\\n. Paragraph 1: Definition & importance. Paragraph 2: English comparison & difficulties for English speakers. Paragraph 3: Complete form breakdown for EACH pronoun/case individually. Paragraph 4: Real-world usage scenarios (at least 2). Paragraph 5: Common mistakes & how to avoid them (at least 2 errors). MINIMUM 400 words total.",
    "conjugation_table": {{
      "headers": ["pronoun", "form", "english", "example", "example_translation"],
      "rows": [
        {{"pronoun": "je", "form": "...", "english": "I ...", "example": "Full French sentence", "example_translation": "English translation"}},
        {{"pronoun": "tu", "form": "...", "english": "you (informal) ...", "example": "...", "example_translation": "..."}},
        {{"pronoun": "il/elle/on", "form": "...", "english": "he/she/one ...", "example": "...", "example_translation": "..."}},
        {{"pronoun": "nous", "form": "...", "english": "we ...", "example": "...", "example_translation": "..."}},
        {{"pronoun": "vous", "form": "...", "english": "you (formal/plural) ...", "example": "...", "example_translation": "..."}},
        {{"pronoun": "ils/elles", "form": "...", "english": "they ...", "example": "...", "example_translation": "..."}}
      ]
    }},
    "key_rules": [
      {{"rule": "Rule title", "explanation": "2-3 sentence detailed explanation with at least one example", "examples": ["French example (English translation)"]}},
      {{"rule": "Rule title", "explanation": "...", "examples": ["..."]}},
      {{"rule": "Rule title", "explanation": "...", "examples": ["..."]}},
      {{"rule": "Rule title", "explanation": "...", "examples": ["..."]}}
    ],
    "examples": [
      {{"french": "...", "english": "...", "context": "Specific situation where you'd say this", "grammar_focus": "What grammar point this demonstrates"}},
      // MINIMUM 8 examples. Must include: statements, questions, negatives. Use DIFFERENT pronouns.
    ],
    "common_errors": [
      {{"incorrect": "Wrong French", "correct": "Correct French", "explanation": "Why learners make this mistake and how to remember the correct form", "memory_aid": "A simple trick to remember"}},
      {{"incorrect": "...", "correct": "...", "explanation": "...", "memory_aid": "..."}}
      // MINIMUM 3 common errors
    ]
  }},
  
  "vocabulary": {{
    "semantic_domain": "word family/theme",
    "words": [
      {{"word": "...", "definition": "...", "pronunciation_tip": "syllable-STRESS format", "part_of_speech": "noun/verb/adj/etc", "example_sentence": "Full French sentence using this word", "example_translation": "English translation", "usage_note": "When/how to use this word, register info"}}
      // MUST include ALL vocabulary words from the curriculum — do NOT skip any
    ]
  }},
  
  "speaking": {{
    "scenario_domain": "interaction context",
    "scenario_context": "Detailed description of the scenario setting and what the student should accomplish",
    "scenario_prompt": "Clear instruction telling the student what to do",
    "ai_opening": "How the AI tutor starts the conversation (in French)",
    "interaction_tier": 1-3,
    "target_phrases": ["phrase 1 the student should try to use", "phrase 2", "phrase 3"],
    "success_criteria": ["Student introduces themselves", "Student asks at least one question", "Student uses target grammar correctly"]
  }},
  
  "quiz": {{
    "instruction": "Clear quiz instructions for the student",
    "questions": [
      {{
        "id": "q1",
        "type": "conjugation|translation|fill_blank|multiple_choice|error_detection",
        "question": "Question text with blank (___) or parentheses — do NOT reveal the answer in the question",
        "options": ["option1", "option2", "option3", "option4"],
        "correct_answer": "the correct option exactly as it appears in options",
        "explanation": "Why this is correct. For wrong options, briefly explain why they're wrong."
      }}
      // 5 questions total. MUST mix question types (not all the same type).
    ]
  }},
  
  "homework": {{
    "type": "text|audio|both",
    "prompt": "Clear prompt explaining what to write or say (1-2 sentences)",
    "detailed_instructions": "Step-by-step instructions with an example of what a good response looks like",
    "minimum_requirements": {{
      "text_length": "6-10 sentences",
      "vocabulary_words": 5,
      "grammar_structures": ["target structure used N times"]
    }},
    "rubric": [
      "Criterion 1: Specific and measurable",
      "Criterion 2: ...",
      "Criterion 3: ...",
      "Criterion 4: ..."
    ],
    "pass_threshold": 4,
    "example_response": "A model response showing what a good submission looks like"
  }},
  
  "metadata": {{
    "generated_at": "{timestamp}",
    "curriculum_file": "{curriculum_file}",
    "attempt_number": {attempt_number},
    "variation_seed": "{variation_seed}",
    "personalization_applied": {{
      "weakness_addressed": [],
      "extra_scaffolding_given": false,
      "complexity_adjusted": "none"
    }}
  }}
}}
```

## GRAMMAR EXPLANATION QUALITY CHECK — Your explanation MUST satisfy ALL:
✅ Contains 5 distinct paragraphs (Definition, English Comparison, Form Breakdown, Usage Context, Common Pitfalls)
✅ Total word count >= 400 words
✅ Each paragraph has minimum required sentences (3/3/6/3/3 = 18 minimum)
✅ Includes at least 2 real-world usage scenarios in paragraph 4
✅ Includes at least 2 common mistakes with corrections in paragraph 5
✅ English comparisons are explicit and helpful for English-speaking learners

## EXAMPLES REQUIREMENTS:
- 8 examples minimum, each using a DIFFERENT pronoun or sentence structure
- Include at least: 2 statements, 2 questions, 1 negative form, 1 formal context
- Progressive complexity (simple → complex)
- Use vocabulary from the curriculum in examples

## CONJUGATION TABLE: Include ALL pronoun forms with a UNIQUE contextual example sentence per row

## QUIZ: 5 questions, mix types (NOT all the same), do NOT show answer in question text

## VOCABULARY: Include ALL words from curriculum with pronunciation tips, example sentences, and usage notes

CRITICAL — DO NOT:
- Invent curriculum content not provided above
- Make grammar mistakes (all French must be correct)
- Use the SAME examples as any previous attempt (check variation seed)
- Skip vocabulary words from the curriculum
- Make examples too complex for {student_level} level"""

# Token estimate: ~1200 tokens


# ============================================================================
# VARIATION INSTRUCTION TEMPLATES (attempt-dependent)
# ============================================================================

_VARIATION_TEMPLATES = {
    1: """### FIRST ATTEMPT — Establish Foundation

This is the FIRST generation. Focus on CLARITY and COMPREHENSIVE explanations.

**Grammar examples:** Use simple, clear contexts. Focus on basic forms. Progressively increase complexity: statement → question → negative.
**Speaking scenario:** Basic, comfortable context (meeting someone, simple introduction).
**Quiz questions:** 2 multiple choice, 2 fill-blank, 1 translation. Focus on recognition.
**Vocabulary examples:** Use vocabulary in simple, everyday sentences.
**Overall contexts to use:** {contexts}
**Use these adjectives in examples:** {adjectives}""",

    2: """### SECOND ATTEMPT — Deepen Understanding (MUST BE COMPLETELY DIFFERENT FROM ATTEMPT 1)

**CRITICAL:** Use COMPLETELY DIFFERENT example sentences, quiz questions, and speaking scenarios than attempt 1. Do NOT reuse any example sentences.

**Grammar examples:** Use DIFFERENT verbs/adjectives than attempt 1. Add nuance: negatives, questions, formal vs informal. Longer sentences.
**Speaking scenario:** DIFFERENT setting — try: {scenario_suggestion}
**Quiz questions:** Different types than attempt 1 — focus on PRODUCTION (conjugation writing, EN→FR translation). Different verbs.
**Vocabulary examples:** Use vocabulary in different sentence structures than attempt 1.
**Overall contexts to use:** {contexts}
**Use these adjectives in examples:** {adjectives}""",

    3: """### THIRD ATTEMPT — Master Nuances (MUST BE DIFFERENT FROM ATTEMPTS 1 AND 2)

**CRITICAL:** Use COMPLETELY DIFFERENT example sentences, quiz questions, and speaking scenarios than all previous attempts.

**Grammar examples:** Focus on EXCEPTIONS and EDGE CASES. Include register differences (formal/informal). Complex sentence structures.
**Speaking scenario:** DIFFERENT context — try: {scenario_suggestion}
**Quiz questions:** Mix ALL types: recognition, production, comprehension, error detection. Different verbs entirely.
**Vocabulary examples:** Use vocabulary in complex, real-world sentences.
**Overall contexts to use:** {contexts}
**Use these adjectives in examples:** {adjectives}""",
}

_VARIATION_TEMPLATE_4PLUS = """### ATTEMPT #{attempt_number} — Complete Mastery (MUST BE UNIQUE)

**CRITICAL:** This is attempt #{attempt_number}. ALL content must be COMPLETELY DIFFERENT from any previous attempt. Use the variation seed ({variation_seed}) to select unique contexts.

**Grammar examples:** Use diverse, varied verbs and contexts. Mix all registers. Vary sentence types completely.
**Speaking scenario:** Creative context: {scenario_suggestion}
**Quiz questions:** Highest variety — mix ALL question types with fresh contexts.
**Vocabulary examples:** Use vocabulary in surprising, creative contexts.
**Overall contexts to use:** {contexts}
**Use these adjectives in examples:** {adjectives}"""

# Context and adjective pools for variation
_CONTEXT_POOLS = [
    ["coffee shop", "meeting a friend", "classroom", "phone call"],
    ["job interview", "doctor's office", "hotel check-in", "restaurant"],
    ["train station", "family dinner", "sports event", "shopping"],
    ["airport", "birthday party", "university", "bank"],
    ["museum", "beach vacation", "cooking class", "movie theater"],
    ["library", "gym", "park", "post office"],
]

_ADJECTIVE_POOLS = [
    ["happy", "tired", "French", "Turkish"],
    ["proud", "busy", "intelligent", "kind"],
    ["excited", "nervous", "strong", "creative"],
    ["calm", "curious", "brave", "patient"],
    ["ambitious", "generous", "serious", "friendly"],
    ["surprised", "confident", "careful", "honest"],
]

_SCENARIO_POOLS = [
    "professional networking event",
    "lost tourist asking for directions",
    "ordering at a French bakery",
    "making a hotel reservation by phone",
    "meeting your partner's French parents",
    "first day at a new French workplace",
    "chatting with a neighbor",
    "waiting room at a clinic",
    "buying tickets at a cinema",
    "asking a librarian for help",
    "registering at a university",
    "complaining about a product at a store",
]


def _get_variation_instruction(attempt_number: int, variation_seed: int) -> str:
    """
    Generate specific variation instructions based on attempt number and seed.
    
    Uses the seed to deterministically select different context pools and adjectives
    so that each attempt produces genuinely different content.
    """
    rng = random.Random(variation_seed + attempt_number)
    
    # Select context pool based on attempt + seed
    context_pool = rng.choice(_CONTEXT_POOLS)
    rng.shuffle(context_pool)
    contexts = ", ".join(context_pool)
    
    # Select adjective pool
    adj_pool = rng.choice(_ADJECTIVE_POOLS)
    rng.shuffle(adj_pool)
    adjectives = ", ".join(adj_pool)
    
    # Select scenario suggestion
    scenario_suggestion = rng.choice(_SCENARIO_POOLS)
    
    if attempt_number in _VARIATION_TEMPLATES:
        template = _VARIATION_TEMPLATES[attempt_number]
    else:
        template = _VARIATION_TEMPLATE_4PLUS
    
    return template.format(
        attempt_number=attempt_number,
        variation_seed=variation_seed,
        contexts=contexts,
        adjectives=adjectives,
        scenario_suggestion=scenario_suggestion,
    )


# ============================================================================
# WEAKNESS PERSONALIZATION SUB-PROMPT
# ============================================================================

WEAKNESS_PERSONALIZATION_SUBPROMPT = """## PERSONALIZATION: ADDRESSING STUDENT WEAKNESSES

The student has documented struggles with the following topics. These MUST be addressed with EXTRA scaffolding.

**Weaknesses to Address:**
{weaknesses_list}

### REQUIRED MODIFICATIONS

**In the grammar "common_errors" section:**
- Add 1-2 extra error examples specifically matching these weaknesses
- Explain WHY this error happens (English interference, pattern confusion, etc.)
- Provide a memory aid for each

**In the grammar "examples" section:**
- Add 2-3 extra examples specifically targeting the weaknesses
- Make these examples very clear with simple vocabulary

**In the homework rubric:**
- Add a specific criterion related to the weakness area

**Tone:** Be encouraging — "Let's strengthen this skill!" not "You keep getting this wrong."
"""

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


# ============================================================================
# PUBLIC API FUNCTIONS
# ============================================================================

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
    timestamp: str,
    attempt_number: int = 1,
    variation_seed: int = None
) -> str:
    """
    Build the main lesson generation prompt with student context and variation instructions.
    
    The variation_seed and attempt_number together ensure each generation
    produces meaningfully different content while teaching the same grammar target.
    
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
        attempt_number: Which attempt is this? (1, 2, 3, 4+)
        variation_seed: Random seed for selecting variation pools (auto-generated if None)
    
    Returns:
        Formatted prompt string
    """
    if variation_seed is None:
        variation_seed = int(datetime.now(timezone.utc).timestamp()) % 100000
    
    # Format completed weeks
    completed_weeks_str = ', '.join(map(str, completed_weeks)) if completed_weeks else "None yet"
    
    # Format weaknesses
    weaknesses_str = '\n'.join([f"- {w}" for w in weaknesses]) if weaknesses else "No documented weaknesses yet"
    
    # Format struggled topics
    struggled_str = ', '.join(struggled_topics) if struggled_topics else "None identified"
    
    # Format curriculum data for inclusion
    curriculum_str = _format_curriculum_for_display(curriculum_data)
    
    # Generate curriculum file reference
    curriculum_file = f"wk{week_number}.md"
    
    # Build variation instruction based on attempt number
    variation_instruction = _get_variation_instruction(attempt_number, variation_seed)
    
    prompt = LESSON_GENERATION_PROMPT.format(
        week_number=week_number,
        day_number=day_number,
        student_level=student_level,
        completed_weeks=completed_weeks_str,
        weaknesses=weaknesses_str,
        struggled_topics=struggled_str,
        curriculum_data=curriculum_str,
        curriculum_theme=curriculum_theme,
        curriculum_file=curriculum_file,
        timestamp=timestamp,
        attempt_number=attempt_number,
        variation_seed=variation_seed,
        variation_instruction=variation_instruction,
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

    # Include scaffolding steps for grammar depth
    scaffolding = grammar.get('scaffolding', [])
    if scaffolding:
        parts.append("**Scaffolding Steps:**")
        for i, step in enumerate(scaffolding, 1):
            parts.append(f"  {i}. {step}")

    if grammar.get('examples'):
        parts.append("**Curriculum Examples:**")
        for ex in grammar.get('examples', []):
            parts.append(f"- {ex}")
    
    vocab = curriculum_data.get('vocabulary_set', [])
    parts.append(f"\n**Vocabulary** ({len(vocab)} words) — YOU MUST INCLUDE ALL OF THESE:")
    for item in vocab:
        word = item.get('word', item) if isinstance(item, dict) else item
        definition = item.get('definition', '') if isinstance(item, dict) else ''
        if definition:
            parts.append(f"- {word} – {definition}")
        else:
            parts.append(f"- {word}")
    
    speaking = curriculum_data.get('speaking_scenario', {})
    parts.append(f"\n**Speaking Scenario**: {speaking.get('domain', 'N/A')}")
    if speaking.get('example_interaction'):
        parts.append("**Example Interaction:**")
        interactions = speaking.get('example_interaction', [])
        if isinstance(interactions, list):
            for line in interactions[:6]:
                parts.append(f"  {line}")
        else:
            parts.append(f"  {interactions}")
    
    homework = curriculum_data.get('homework_task', {})
    parts.append(f"\n**Homework Type**: {homework.get('type', 'N/A')}")
    if homework.get('task_description'):
        parts.append(f"**Homework Task**: {homework.get('task_description')}")
    
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
    parts.append(f"Prompt: {homework_assignment.get('prompt', homework_assignment.get('task_description', 'N/A'))}")
    
    rubric = homework_assignment.get('rubric', [])
    parts.append("\nRubric (must meet criteria for passing):")
    for i, criterion in enumerate(rubric, 1):
        if isinstance(criterion, dict):
            parts.append(f"{i}. {criterion.get('criterion', criterion)}")
        else:
            parts.append(f"{i}. {criterion}")
    
    parts.append(f"\nPass Threshold: {homework_assignment.get('pass_threshold', 4)}/{len(rubric)} criteria")
    
    return '\n'.join(parts)


def _format_lesson_content(lesson_content: dict) -> str:
    """Format lesson content for evaluation context."""
    parts = []
    
    grammar = lesson_content.get('grammar', {})
    parts.append(f"Grammar Target: {grammar.get('target_form', 'N/A')}")
    
    key_rules = grammar.get('key_rules', [])
    if isinstance(key_rules, list) and key_rules:
        rule_texts = []
        for r in key_rules[:3]:
            if isinstance(r, dict):
                rule_texts.append(r.get('rule', r.get('title', str(r)))[:50])
            else:
                rule_texts.append(str(r)[:50])
        parts.append(f"Key Rules: {', '.join(rule_texts)}")
    
    vocab = lesson_content.get('vocabulary', {})
    words = vocab.get('words', []) if isinstance(vocab, dict) else []
    word_list = [w.get('word', str(w))[:20] if isinstance(w, dict) else str(w)[:20] for w in words[:10]]
    if word_list:
        parts.append(f"Vocabulary: {', '.join(word_list)}")
    
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
    parts.append(f"Domain: {scenario_details.get('scenario_domain', scenario_details.get('domain', 'N/A'))}")
    
    if scenario_details.get('scenario_context'):
        parts.append(f"Context: {scenario_details['scenario_context']}")
    
    if scenario_details.get('ai_opening'):
        parts.append(f"AI Opening: {scenario_details['ai_opening']}")
    
    success = scenario_details.get('success_criteria', [])
    if success:
        parts.append("Success Criteria:")
        if isinstance(success, list):
            for criterion in success[:4]:
                parts.append(f"- {criterion}")
        else:
            parts.append(f"- {success}")
    
    if scenario_details.get('example_interaction'):
        parts.append("Example Interaction:")
        interactions = scenario_details['example_interaction']
        if isinstance(interactions, list):
            for line in interactions[:5]:
                parts.append(f"  {line}")
        else:
            parts.append(f"  {interactions}")
    
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
        if isinstance(q, dict):
            parts.append(f"{i}. {q.get('question', 'N/A')}")
            if q.get('options'):
                for opt in q['options']:
                    parts.append(f"   - {opt}")
        else:
            parts.append(f"{i}. {q}")
    return '\n'.join(parts)


def _format_student_answers(answers: dict) -> str:
    """Format student answers for prompt."""
    parts = []
    for qid in sorted(answers.keys()):
        answer = answers[qid]
        parts.append(f"Q{qid}: {answer}")
    return '\n'.join(parts)
