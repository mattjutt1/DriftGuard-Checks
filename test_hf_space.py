#!/usr/bin/env python3
"""Test HuggingFace Space availability and API"""

import requests
import json
import time

SPACE_URL = "https://unfiltrdfreedom-prompt-evolver.hf.space"

def test_space_availability():
    """Check if the HF Space is accessible"""
    print(f"Testing HuggingFace Space: {SPACE_URL}")
    print("-" * 50)
    
    try:
        # Test main page
        print("1. Testing main page...")
        response = requests.get(SPACE_URL, timeout=10)
        if response.status_code == 200:
            print("   ✅ Space is accessible")
            if "gradio" in response.text.lower():
                print("   ✅ Gradio interface detected")
        else:
            print(f"   ❌ Space returned status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("   ⏱️ Space is loading (timeout) - may be starting up")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Space - may be rebuilding")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test API endpoint
    print("2. Testing API endpoint...")
    api_url = f"{SPACE_URL}/api/predict"
    
    try:
        # Simple test payload
        payload = {
            "data": [
                "Write a Python function to calculate factorial",  # prompt
                "Need a clear, efficient implementation",  # task description
                "balanced",  # mode
                0.7  # temperature
            ]
        }
        
        print(f"   Sending test request to {api_url}")
        response = requests.post(
            api_url,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ API responded successfully")
            result = response.json()
            print(f"   Response preview: {json.dumps(result, indent=2)[:200]}...")
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print("   ⏱️ API timeout - model may be loading")
    except Exception as e:
        print(f"   ❌ API Error: {e}")
    
    print()
    print("3. Space Info:")
    print(f"   Public URL: {SPACE_URL}")
    print(f"   API Endpoint: {SPACE_URL}/api/predict")
    print(f"   Files URL: https://huggingface.co/spaces/unfiltrdfreedom/prompt-evolver/tree/main")
    print(f"   Logs URL: https://huggingface.co/spaces/unfiltrdfreedom/prompt-evolver/logs")

if __name__ == "__main__":
    test_space_availability()