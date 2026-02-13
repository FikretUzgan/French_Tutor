import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Testing imports...")
    from main import app
    print("[OK] main.py imported successfully")
    
    from services import ai_service
    print("[OK] services.ai_service imported successfully")
    
    from services import audio_service
    print("[OK] services.audio_service imported successfully")
    
    from core import prompts
    print("[OK] core.prompts imported successfully")
    
    from core import schemas
    print("[OK] core.schemas imported successfully")
    
    print("\nChecking AI Service functions...")
    assert hasattr(ai_service, 'generate_lesson_from_curriculum'), "ai_service missing generate_lesson_from_curriculum"
    assert hasattr(ai_service, 'get_speaking_roleplay_response'), "ai_service missing get_speaking_roleplay_response"
    print("[OK] AI Service functions found")
    
    print("\nChecking Audio Service functions...")
    assert hasattr(audio_service, 'transcribe_audio'), "audio_service missing transcribe_audio"
    print("[OK] Audio Service functions found")

    print("\n[SUCCESS] PHASE 2 VERIFICATION SUCCESSFUL")

except Exception as e:
    print(f"\n[FAILED] PHASE 2 VERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
