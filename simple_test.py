#!/usr/bin/env python3
"""Simple CometAPI connectivity test"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_comet_simple():
    """Simple sync test for CometAPI"""
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    print("🧪 Simple CometAPI Test")
    print("=" * 30)
    print(f"🔑 Testing Key: {api_key[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 50,
        'messages': [
            {
                'role': 'user',
                'content': 'Hello! Just say "Hi" if this works.'
            }
        ]
    }
    
    try:
        print("📡 Connecting to CometAPI...")
        response = requests.post(
            'https://api.cometapi.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CometAPI Connection Successful!")
            print(f"📝 Response: {data}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_comet_simple()
