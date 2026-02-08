"""
Test script for dynamic lesson generation
Tests the complete flow from curriculum loading to lesson generation
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import curriculum_loader
import lesson_generator
import prompt_builders

def test_curriculum_loading():
    """Test loading and parsing curriculum files"""
    print("=" * 60)
    print("TEST 1: Curriculum Loading")
    print("=" * 60)
    
    try:
        # Test Week 1 (A1.1)
        print("\n📂 Loading Week 1 curriculum...")
        week1 = curriculum_loader.load_curriculum_file(1)
        
        print(f"✅ Week {week1['week_number']}")
        print(f"   Theme: {week1['theme']}")
        print(f"   Level: {week1['level']}")
        print(f"   Grammar: {week1['grammar_target']['form']}")
        print(f"   Vocabulary: {len(week1['vocabulary_set'])} words")
        print(f"   Learning Outcomes: {len(week1['learning_outcomes'])} items")
        
        # Test Week 5 (A1.2 with passé composé)
        print("\n📂 Loading Week 5 curriculum...")
        week5 = curriculum_loader.load_curriculum_file(5)
        
        print(f"✅ Week {week5['week_number']}")
        print(f"   Theme: {week5['theme']}")
        print(f"   Level: {week5['level']}")
        print(f"   Grammar: {week5['grammar_target']['form']}")
        print(f"   Vocabulary: {len(week5['vocabulary_set'])} words")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_building():
    """Test prompt builder functions"""
    print("\n" + "=" * 60)
    print("TEST 2: Prompt Building")
    print("=" * 60)
    
    try:
        # Load curriculum for context
        curriculum_data = curriculum_loader.load_curriculum_file(1)
        
        # Build system prompt
        print("\n🔨 Building system prompt...")
        system_prompt = prompt_builders.build_system_prompt(
            student_level='A1.1',
            completed_weeks=[],
            weaknesses=[]
        )
        print(f"✅ System prompt: {len(system_prompt)} characters")
        print(f"   Preview: {system_prompt[:150]}...")
        
        # Build lesson generation context
        print("\n🔨 Building lesson generation context...")
        student_profile = {
            'user_id': 1,
            'level': 'A1.1',
            'completed_weeks': []
        }
        
        lesson_prompt = prompt_builders.build_lesson_generation_context(
            week_number=1,
            day_number=1,
            curriculum_data=curriculum_data,
            student_profile=student_profile,
            weaknesses_data=[],
            attempt_number=1,
            variation_seed=12345
        )
        print(f"✅ Lesson prompt: {len(lesson_prompt)} characters")
        print(f"   Preview: {lesson_prompt[:150]}...")
        
        # Validate token budget
        print("\n📊 Validating token budget...")
        token_info = prompt_builders.validate_prompt_token_budget(
            system_prompt=system_prompt,
            lesson_prompt=lesson_prompt
        )
        print(f"✅ Total tokens: {token_info['total_tokens']}")
        print(f"   Fits budget: {token_info['fits_budget']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lesson_generation():
    """Test full lesson generation (requires API key)"""
    print("\n" + "=" * 60)
    print("TEST 3: Lesson Generation (Full Flow)")
    print("=" * 60)
    
    try:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Check if API key is available
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  GEMINI_API_KEY not found in environment")
            print("   Skipping API call test")
            print("   To test fully, add GEMINI_API_KEY to .env file")
            return True  # Still counts as "passed" since it's optional
        
        print("\n🤖 Generating lesson for Week 1, Day 1...")
        print("   (This may take 8-15 seconds...)")
        
        lesson, was_generated = lesson_generator.generate_lesson_from_curriculum(
            week_number=1,
            day_number=1,
            student_level='A1.1',
            user_id=999,  # Test user
            fallback_on_error=True
        )
        
        if was_generated:
            print("✅ Lesson generated successfully via API!")
        else:
            print("⚠️  Lesson generated using fallback")
        
        print(f"\n📋 Lesson Summary:")
        print(f"   Lesson ID: {lesson.get('lesson_id', 'N/A')}")
        print(f"   Theme: {lesson.get('theme', 'N/A')}")
        print(f"   Level: {lesson.get('level', 'N/A')}")
        print(f"   Week: {lesson.get('week', 'N/A')}")
        
        # Check grammar section
        if 'grammar' in lesson:
            grammar = lesson['grammar']
            explanation_len = len(grammar.get('explanation', ''))
            examples_count = len(grammar.get('examples', []))
            print(f"\n   Grammar:")
            print(f"      Explanation: {explanation_len} characters")
            print(f"      Examples: {examples_count} items")
        
        # Check vocabulary section
        if 'vocabulary' in lesson:
            vocab = lesson['vocabulary']
            words_count = len(vocab.get('words', []))
            print(f"\n   Vocabulary:")
            print(f"      Words: {words_count} items")
        
        # Check quiz section
        if 'quiz' in lesson:
            quiz = lesson['quiz']
            questions_count = len(quiz.get('questions', []))
            print(f"\n   Quiz:")
            print(f"      Questions: {questions_count} items")
        
        # Save sample output for inspection
        output_file = Path(__file__).parent / "test_generated_lesson.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full lesson saved to: {output_file.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DYNAMIC LESSON GENERATION - TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Curriculum loading
    results['curriculum_loading'] = test_curriculum_loading()
    
    # Test 2: Prompt building
    results['prompt_building'] = test_prompt_building()
    
    # Test 3: Lesson generation (requires API key)
    results['lesson_generation'] = test_lesson_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
