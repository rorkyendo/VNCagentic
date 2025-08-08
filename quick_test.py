#!/usr/bin/env python3
"""
Quick CometAPI Anthropic Compatible Test
"""
import os
import requests
from dotenv import load_dotenv

def test_comet_anthropic():
    """Test CometAPI with Anthropic Compatible format"""
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    print("🧪 CometAPI Anthropic Compatible Test")
    print("=" * 40)
    print(f"🔑 Testing Key: {api_key[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    
    # Format sesuai dokumentasi Anthropic Compatible
    payload = {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 100,
        'messages': [
            {
                'role': 'user',
                'content': 'Hello! Just say "Hi from CometAPI" if this works.'
            }
        ]
    }
    
    try:
        print("📡 Connecting to CometAPI /v1/messages...")
        response = requests.post(
            'https://api.cometapi.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CometAPI Anthropic Compatible Working!")
            
            # Parse response format
            if 'content' in data and isinstance(data['content'], list):
                # Anthropic format
                message = data['content'][0].get('text', 'No text content')
                print(f"📝 Response: {message}")
            elif 'choices' in data:
                # OpenAI format (fallback)
                message = data['choices'][0].get('message', {}).get('content', 'No content')
                print(f"📝 Response: {message}")
            else:
                print(f"📝 Raw Response: {data}")
            
            return True
            
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Error Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_comet_anthropic()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ CometAPI Anthropic Compatible is working!")
        print("🚀 Ready to integrate with VNCagentic backend")
    else:
        print("❌ Fix CometAPI configuration first")
        print("📖 Check your API key and endpoint")
