#!/usr/bin/env python3
"""Test app imports"""

try:
    import app
    print("✅ App imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
