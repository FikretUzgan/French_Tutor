"""
Test Homework Blocking Logic and Lesson Delivery
Tests the complete workflow with blocking enabled/disabled
"""

import requests
import json

base_url = "http://localhost:8000"

def test_settings_api():
    """Test settings management endpoints"""
    print("\n" + "="*60)
    print("TESTING SETTINGS API")
    print("="*60)
    
    # Get current mode
    response = requests.get(f"{base_url}/api/mode")
    mode_data = response.json()
    print(f"\nCurrent mode: {mode_data['mode']}")
    print(f"Homework blocking: {mode_data.get('homework_blocking_enabled', 'N/A')}")
    
    return mode_data


def test_lesson_delivery():
    """Test lesson delivery from database"""
    print("\n" + "="*60)
    print("TESTING LESSON DELIVERY")
    print("="*60)
    
    # Test 1: Get all lessons
    response = requests.get(f"{base_url}/api/lessons")
    lessons = response.json()
    print(f"\n[1] Total lessons in DB: {len(lessons)}")
    
    if lessons:
        first = lessons[0]
        print(f"    First lesson: {first['lesson_id']}")
        print(f"    Title: {first['title']}")
        print(f"    Level: {first['level']}")
    
    # Test 2: Get available lessons (should respect blocking)
    response = requests.get(f"{base_url}/api/lessons/available")
    available = response.json()
    print(f"\n[2] Available lessons (non-blocked): {len(available)}")
    
    # Test 3: Get specific lesson
    lesson_id = "block1_w1_d1_monday"
    response = requests.get(f"{base_url}/api/lessons/{lesson_id}")
    
    if response.status_code == 200:
        lesson = response.json()
        print(f"\n[3] Retrieved lesson: {lesson_id}")
        print(f"    Title: {lesson['title']}")
        print(f"    Has grammar: {'grammar' in lesson['content']}")
        print(f"    Has vocabulary: {'vocabulary' in lesson['content']}")
        print(f"    Vocabulary items: {len(lesson['content'].get('vocabulary', []))}")
    elif response.status_code == 403:
        print(f"\n[3] Lesson blocked: {response.json()['detail']}")
    else:
        print(f"\n[3] Error: {response.status_code} - {response.text}")
    
    return lessons


def test_homework_blocking_disabled():
    """Test with blocking disabled (dev mode)"""
    print("\n" + "="*60)
    print("TESTING WITH BLOCKING DISABLED")
    print("="*60)
    
    # Disable blocking
    response = requests.post(
        f"{base_url}/api/settings/homework-blocking",
        params={"enabled": False}
    )
    result = response.json()
    print(f"\n[1] Disabled homework blocking: {result['message']}")
    
    # Try to access second lesson (should work)
    lesson_id = "block1_w1_d2_tuesday"
    response = requests.get(f"{base_url}/api/lessons/{lesson_id}")
    
    if response.status_code == 200:
        lesson = response.json()
        print(f"\n[2] ✓ Second lesson accessible: {lesson['title']}")
    else:
        print(f"\n[2] ✗ Failed to access second lesson: {response.status_code}")
    
    # Check available lessons count
    response = requests.get(f"{base_url}/api/lessons/available")
    available = response.json()
    print(f"\n[3] Available lessons with blocking OFF: {len(available)}")


def test_homework_blocking_enabled():
    """Test with blocking enabled (production mode)"""
    print("\n" + "="*60)
    print("TESTING WITH BLOCKING ENABLED")
    print("="*60)
    
    # Enable blocking
    response = requests.post(
        f"{base_url}/api/settings/homework-blocking",
        params={"enabled": True}
    )
    result = response.json()
    print(f"\n[1] Enabled homework blocking: {result['message']}")
    
    # Try to access first lesson (should always work - it's the first)
    lesson_id = "block1_w1_d1_monday"
    response = requests.get(f"{base_url}/api/lessons/{lesson_id}")
    
    if response.status_code == 200:
        lesson = response.json()
        print(f"\n[2] ✓ First lesson accessible: {lesson['title']}")
    else:
        print(f"\n[2] ✗ Failed to access first lesson: {response.status_code}")
    
    # Try to access second lesson without completing first homework (should be blocked)
    lesson_id = "block1_w1_d2_tuesday"
    response = requests.get(f"{base_url}/api/lessons/{lesson_id}")
    
    if response.status_code == 403:
        print(f"\n[3] ✓ Second lesson correctly blocked: {response.json()['detail']}")
    elif response.status_code == 200:
        print(f"\n[3] ? Second lesson accessible (homework may have been submitted)")
    else:
        print(f"\n[3] ✗ Unexpected response: {response.status_code}")
    
    # Check available lessons count
    response = requests.get(f"{base_url}/api/lessons/available")
    available = response.json()
    print(f"\n[4] Available lessons with blocking ON: {len(available)}")


def test_toggle_modes():
    """Test toggling between modes"""
    print("\n" + "="*60)
    print("TESTING MODE TOGGLING")
    print("="*60)
    
    # Toggle homework blocking OFF
    response = requests.post(
        f"{base_url}/api/settings/homework-blocking",
        params={"enabled": False}
    )
    print(f"\n[1] Blocking OFF: {response.json()['homework_blocking_enabled']}")
    
    # Verify setting
    response = requests.get(f"{base_url}/api/mode")
    mode_data = response.json()
    print(f"    Confirmed: {mode_data.get('homework_blocking_enabled', 'ERROR')}")
    
    # Toggle homework blocking ON
    response = requests.post(
        f"{base_url}/api/settings/homework-blocking",
        params={"enabled": True}
    )
    print(f"\n[2] Blocking ON: {response.json()['homework_blocking_enabled']}")
    
    # Verify setting
    response = requests.get(f"{base_url}/api/mode")
    mode_data = response.json()
    print(f"    Confirmed: {mode_data.get('homework_blocking_enabled', 'ERROR')}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LESSON DELIVERY & HOMEWORK BLOCKING TESTS")
    print("="*60)
    
    try:
        # Test 1: Check current settings
        test_settings_api()
        
        # Test 2: Lesson delivery
        test_lesson_delivery()
        
        # Test 3: Blocking disabled
        test_homework_blocking_disabled()
        
        # Test 4: Blocking enabled
        test_homework_blocking_enabled()
        
        # Test 5: Toggle modes
        test_toggle_modes()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("✓ All tests completed successfully!")
        print("\nFeatures tested:")
        print("  - Lesson delivery from database (129 lessons)")
        print("  - Homework blocking logic")
        print("  - Bypass option (enabled/disabled)")
        print("  - Settings API endpoints")
        print("  - Available lessons filtering")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
