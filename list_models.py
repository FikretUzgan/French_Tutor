"""
List available Gemini models from the API
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    exit(1)

try:
    client = genai.Client(api_key=api_key)
    
    print("📋 Available Models:")
    print("=" * 80)
    
    models = client.models.list()
    
    for model in models:
        print(f"\n🔹 {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}..." if len(model.description) > 100 else f"   Description: {model.description}")
        
        # Check supported methods
        if hasattr(model, 'supported_generation_methods'):
            print(f"   Supported Methods: {model.supported_generation_methods}")
        
        # Check input/output token limits
        if hasattr(model, 'input_token_limit'):
            print(f"   Max Input Tokens: {model.input_token_limit}")
        if hasattr(model, 'output_token_limit'):
            print(f"   Max Output Tokens: {model.output_token_limit}")
    
    print("\n" + "=" * 80)
    print("\n✅ Models retrieved successfully!")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
    import traceback
    traceback.print_exc()
