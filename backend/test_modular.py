#!/usr/bin/env python3
"""
Test script for modular NexusAI
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modular imports work"""
    try:
        print("🧪 Testing modular imports...")
        
        # Test utils import
        from utils.helpers import apply_ai_guardrails, format_model_name
        print("✅ Utils helpers imported successfully")
        
        # Test API routes import
        from api.chat_routes import register_chat_routes
        print("✅ Chat routes imported successfully")
        
        # Test main app import
        from app import app
        print("✅ Main app imported successfully")
        
        # Test that routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        chat_route = '/api/chat' in routes
        models_route = '/api/models' in routes
        
        print(f"✅ Chat route registered: {chat_route}")
        print(f"✅ Models route registered: {models_route}")
        
        if chat_route and models_route:
            print("🎉 All modular components working correctly!")
            return True
        else:
            print("❌ Some routes not registered properly")
            return False
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_helper_functions():
    """Test helper functions"""
    try:
        print("\n🧪 Testing helper functions...")
        
        from utils.helpers import apply_ai_guardrails, format_model_name
        
        # Test guardrails
        safe_result = apply_ai_guardrails("Hello, how are you?")
        print(f"✅ Safe message test: {not safe_result['blocked']}")
        
        # Test model name formatting
        formatted_name = format_model_name("llama-3.1-8b-instant")
        print(f"✅ Model name formatting: {formatted_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Helper function error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing NexusAI Modularization")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_helper_functions()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Modularization successful!")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    sys.exit(0 if success else 1)