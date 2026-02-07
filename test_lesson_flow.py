"""
End-to-End Test of Lesson Flow
Tests the complete workflow: lesson retrieval, homework submission, feedback, progress tracking
"""

import db
import json
from datetime import datetime


def test_lesson_flow():
    """Test complete lesson flow from start to finish."""
    
    print("\n" + "="*60)
    print("END-TO-END LESSON FLOW TEST")
    print("="*60 + "\n")
    
    # Initialize database
    db.init_db()
    
    # Test 1: Retrieve a lesson
    print("[1] Retrieving first A1.1 lesson...")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM lessons WHERE level = ? ORDER BY lesson_id LIMIT 1",
        ("A1.1",)
    )
    lesson_row = cursor.fetchone()
    
    if not lesson_row:
        print("ERROR: No A1.1 lesson found!")
        return False
    
    lesson_id = lesson_row["lesson_id"]
    print(f"   [OK] Retrieved lesson: {lesson_id}")
    print(f"        Theme: {lesson_row['theme']}")
    print(f"        Grammar: {lesson_row['grammar_explanation'][:50]}...")
    
    # Test 2: Check lesson progress status
    print("\n[2] Checking lesson progress status...")
    cursor.execute(
        "SELECT * FROM lesson_progress WHERE lesson_id = ?",
        (lesson_id,)
    )
    progress = cursor.fetchone()
    
    if progress:
        print(f"   [OK] Progress record exists")
        print(f"        Completed: {progress['completed']}")
        print(f"        Homework Submitted: {progress['homework_submitted']}")
    else:
        print("   [ERROR] No progress record found!")
        return False
    
    # Test 3: Submit homework
    print("\n[3] Submitting homework...")
    submission_id = db.save_homework_submission(
        lesson_id=lesson_id,
        text_content="Je suis etudiant. J'ai 25 ans. Je suis francais.",
        audio_file_path="test_audio.wav"
    )
    print(f"   [OK] Homework submitted with ID: {submission_id}")
    
    # Test 4: Check homework submission in database
    print("\n[4] Verifying homework submission...")
    cursor.execute(
        "SELECT * FROM homework_submissions WHERE submission_id = ?",
        (submission_id,)
    )
    submission = cursor.fetchone()
    
    if submission:
        print(f"   [OK] Submission recorded")
        print(f"        Text length: {submission['character_count']} characters")
        print(f"        Status: {submission['status']}")
    else:
        print("   [ERROR] Submission not found!")
        return False
    
    # Test 5: Generate and save feedback (simulated)
    print("\n[5] Generating AI feedback...")
    feedback_json = {
        "text_score": 85,
        "audio_score": 78,
        "passed": True,
        "grammar_feedback": "Good use of 'être' and 'avoir'. Watch article agreement.",
        "vocabulary_feedback": "Vocabulary is appropriate for A1.1",
        "pronunciation_feedback": "Clear pronunciation, slight accent on vowels.",
        "overall_feedback": "Great job! You're understanding basic conjugations well."
    }
    
    feedback_id = db.save_homework_feedback(
        submission_id=submission_id,
        text_score=feedback_json["text_score"],
        audio_score=feedback_json["audio_score"],
        passed=feedback_json["passed"],
        grammar_feedback=feedback_json["grammar_feedback"],
        vocabulary_feedback=feedback_json["vocabulary_feedback"],
        pronunciation_feedback=feedback_json["pronunciation_feedback"],
        overall_feedback=feedback_json["overall_feedback"]
    )
    print(f"   [OK] Feedback generated with ID: {feedback_id}")
    
    # Test 6: Verify feedback in database
    print("\n[6] Verifying feedback...")
    cursor.execute(
        "SELECT * FROM homework_feedback WHERE feedback_id = ?",
        (feedback_id,)
    )
    feedback = cursor.fetchone()
    
    if feedback:
        print(f"   [OK] Feedback recorded")
        print(f"        Text Score: {feedback['text_score']}")
        print(f"        Audio Score: {feedback['audio_score']}")
        print(f"        Passed: {feedback['passed']}")
    else:
        print("   [ERROR] Feedback not found!")
        return False
    
    # Test 7: Update lesson progress
    print("\n[7] Updating lesson progress...")
    db.update_homework_status(lesson_id, True)
    db.mark_lesson_complete(lesson_id)
    print(f"   [OK] Lesson marked as complete")
    
    # Test 8: Verify final progress state
    print("\n[8] Verifying final progress state...")
    cursor.execute(
        "SELECT * FROM lesson_progress WHERE lesson_id = ?",
        (lesson_id,)
    )
    final_progress = cursor.fetchone()
    
    if final_progress:
        print(f"   [OK] Final progress state:")
        print(f"        Completed: {final_progress['completed']}")
        print(f"        Homework Submitted: {final_progress['homework_submitted']}")
        print(f"        Homework Passed: {final_progress['homework_passed']}")
    else:
        print("   [ERROR] Final progress not found!")
        return False
    
    # Test 9: Retrieve next lesson
    print("\n[9] Retrieving next lesson...")
    cursor.execute(
        "SELECT lesson_id, theme FROM lessons WHERE level = ? AND lesson_id > ? LIMIT 1",
        ("A1.1", lesson_id)
    )
    next_lesson = cursor.fetchone()
    
    if next_lesson:
        print(f"   [OK] Next lesson available: {next_lesson['lesson_id']}")
        print(f"        Theme: {next_lesson['theme']}")
    else:
        print("   [INFO] No next lesson in same level (may be in next level)")
    
    # Test 10: Verify progression through levels
    print("\n[10] Checking level progression...")
    cursor.execute("SELECT DISTINCT level FROM lessons ORDER BY level")
    levels = cursor.fetchall()
    print(f"   [OK] Available levels: {[row['level'] for row in levels]}")
    
    conn.close()
    
    # Final summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("[OK] Complete lesson workflow test PASSED!")
    print("     - Lesson retrieval: OK")
    print("     - Homework submission: OK")
    print("     - AI feedback generation: OK")
    print("     - Progress tracking: OK")
    print("     - Level progression: OK")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_lesson_flow()
    exit(0 if success else 1)
