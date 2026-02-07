"""
Test script for database functionality.
"""

from db import (
    init_db,
    save_homework_submission,
    get_homework_submission,
    save_homework_feedback,
    get_homework_feedback,
    update_homework_status,
)

def test_homework_flow():
    """Test the complete homework submission flow."""
    print("Testing homework submission flow...")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Save a sample homework submission
    submission_id = save_homework_submission(
        lesson_id="a2_imparfait_001",
        text_content="Quand j'etais enfant, je jouais au parc chaque jour. Un jour, j'ai retrouve un vieux cahier. Il pleuvait beaucoup ce jour-la. Je me souvenais de mes amis qui habitaient pres du parc. Nous allions souvent ensemble apres l'ecole.",
        audio_file_path="submissions/audio/a2_imparfait_001_20260207_120000.wav",
        character_count=268,
        audio_size_kb=450.5
    )
    print(f"✓ Homework submission saved: submission_id={submission_id}")
    
    # Retrieve the submission
    submission = get_homework_submission(submission_id)
    if submission:
        print(f"✓ Submission retrieved")
        print(f"  - Text length: {submission['character_count']} chars")
        print(f"  - Audio size: {submission['audio_size_kb']} KB")
        print(f"  - Status: {submission['status']}")
    
    # Save AI feedback
    feedback_id = save_homework_feedback(
        submission_id=submission_id,
        text_score=82.5,
        audio_score=75.0,
        passed=True,
        grammar_feedback="Good use of imparfait and passe compose. Minor: 'pres du parc' -> 'pres de notre parc'",
        vocabulary_feedback="Excellent vocabulary. You used 'cahier', 'souvenirl', 'autrefois' correctly.",
        pronunciation_feedback="Clear pronunciation. Good pacing. Accent on some words could be improved.",
        overall_feedback="Excellent work! You demonstrated good command of past tenses and showed progress."
    )
    print(f"✓ Feedback saved: feedback_id={feedback_id}")
    
    # Retrieve feedback
    feedback = get_homework_feedback(submission_id)
    if feedback:
        print(f"✓ Feedback retrieved")
        print(f"  - Text Score: {feedback['text_score']}/100")
        print(f"  - Audio Score: {feedback['audio_score']}/100")
        print(f"  - Passed: {feedback['passed']}")
    
    # Update status
    update_homework_status(submission_id, "graded")
    submission_updated = get_homework_submission(submission_id)
    print(f"✓ Status updated: {submission_updated['status']}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_homework_flow()
