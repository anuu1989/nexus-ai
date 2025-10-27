#!/usr/bin/env python3
"""
Test script for the Enhanced LoRA System
"""

import requests
import json
import time

def test_lora_endpoints():
    """Test the LoRA API endpoints"""
    base_url = "http://localhost:5002"
    
    print("🧪 Testing Enhanced LoRA System...")
    
    # Test 1: Get adapters
    print("\n1. Testing GET /api/lora/adapters")
    try:
        response = requests.get(f"{base_url}/api/lora/adapters")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data.get('adapters', []))} adapters")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Create adapter
    print("\n2. Testing POST /api/lora/create")
    try:
        payload = {
            "name": "Test Adapter",
            "type": "General",
            "rank": 16,
            "alpha": 32
        }
        response = requests.post(f"{base_url}/api/lora/create", json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Created adapter: {data.get('adapter', {}).get('name')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 3: Analyze performance
    print("\n3. Testing GET /api/lora/analyze")
    try:
        response = requests.get(f"{base_url}/api/lora/analyze")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            print(f"   ✅ Analysis complete - {analysis.get('total_adapters', 0)} adapters analyzed")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 4: Optimize hyperparameters
    print("\n4. Testing POST /api/lora/optimize")
    try:
        payload = {
            "dataset_size": 1000,
            "task_type": "general"
        }
        response = requests.post(f"{base_url}/api/lora/optimize", json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            optimization = data.get('optimization', {})
            optimal_params = optimization.get('optimal_parameters', {})
            print(f"   ✅ Optimization complete - Recommended rank: {optimal_params.get('rank')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n🎉 LoRA System Test Complete!")
    print("\nTo run this test:")
    print("1. Start the Flask server: python app.py")
    print("2. Run this test: python test_lora_system.py")

if __name__ == "__main__":
    test_lora_endpoints()