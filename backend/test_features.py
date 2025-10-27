#!/usr/bin/env python3
"""
Test script for NexusAI new features
====================================

Simple test to verify that all new features are working correctly.
"""

import sys
import os
import json
from datetime import datetime

def test_database():
    """Test database functionality"""
    print("🧪 Testing Database System...")
    
    try:
        from database import NexusAIDatabase
        
        # Create test database
        db = NexusAIDatabase('test_nexusai.db')
        
        # Test user creation
        user_data = {
            'name': 'Test User',
            'email': 'test@nexusai.com',
            'bio': 'Test user for NexusAI',
            'preferences': {'theme': 'dark', 'language': 'en'}
        }
        
        user_id = db.create_user(user_data)
        print(f"✅ User created with ID: {user_id}")
        
        # Test user retrieval
        retrieved_user = db.get_user(user_id)
        if retrieved_user:
            print(f"✅ User retrieved: {retrieved_user['name']}")
        
        # Test conversation saving
        conversation_data = {
            'user_id': user_id,
            'title': 'Test Conversation',
            'model': 'llama-3.1-8b-instant',
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a test message'},
                {'role': 'assistant', 'content': 'Hello! This is a test response.'}
            ]
        }
        
        conv_id = db.save_conversation(conversation_data)
        print(f"✅ Conversation saved with ID: {conv_id}")
        
        # Test analytics logging
        db.log_analytics({
            'user_id': user_id,
            'event_type': 'test_event',
            'model_used': 'test-model',
            'response_time': 1.5,
            'data': {'test': True}
        })
        print("✅ Analytics logged successfully")
        
        # Get database stats
        stats = db.get_database_stats()
        print(f"✅ Database stats: {stats}")
        
        # Clean up test database
        os.remove('test_nexusai.db')
        print("✅ Database test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Module Imports...")
    
    modules_to_test = [
        'app',
        'database',
        'simple_rag_system',
        'lora_system'
    ]
    
    success_count = 0
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"⚠️ {module} import failed: {e}")
        except Exception as e:
            print(f"❌ {module} error: {e}")
    
    print(f"📊 Import test: {success_count}/{len(modules_to_test)} modules imported successfully")
    return success_count == len(modules_to_test)

def test_file_structure():
    """Test that all required files exist"""
    print("🧪 Testing File Structure...")
    
    required_files = [
        'app.py',
        'database.py',
        'simple_rag_system.py',
        'lora_system.py',
        'index.html',
        'manifest.json',
        'sw.js',
        'static/js/user-management.js',
        'static/js/global-search.js',
        'static/js/pwa-support.js',
        'static/css/new-features.css',
        'requirements-minimal.txt',
        'requirements-full.txt',
        'INSTALLATION.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_json_files():
    """Test that JSON files are valid"""
    print("🧪 Testing JSON Files...")
    
    json_files = ['manifest.json']
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
            print(f"✅ {json_file} is valid JSON")
        except FileNotFoundError:
            print(f"❌ {json_file} not found")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ {json_file} invalid JSON: {e}")
            return False
    
    return True

def test_css_syntax():
    """Basic CSS syntax test"""
    print("🧪 Testing CSS Files...")
    
    css_files = [
        'static/css/new-features.css',
        'static/css/nexusai-theme.css',
        'static/css/z-index-fix.css'
    ]
    
    for css_file in css_files:
        if os.path.exists(css_file):
            try:
                with open(css_file, 'r') as f:
                    content = f.read()
                    # Basic syntax check - count braces
                    open_braces = content.count('{')
                    close_braces = content.count('}')
                    
                    if open_braces == close_braces:
                        print(f"✅ {css_file} - braces balanced")
                    else:
                        print(f"⚠️ {css_file} - unbalanced braces ({open_braces} open, {close_braces} close)")
            except Exception as e:
                print(f"❌ {css_file} error: {e}")
        else:
            print(f"⚠️ {css_file} not found")
    
    return True

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("🚀 NEXUSAI NEW FEATURES TEST REPORT")
    print("="*60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("-"*60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("JSON Validation", test_json_files),
        ("CSS Syntax", test_css_syntax),
        ("Database System", test_database)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("-"*60)
    print(f"📈 Overall Result: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! NexusAI new features are ready!")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = generate_test_report()
    sys.exit(0 if success else 1)