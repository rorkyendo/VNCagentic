"""
Test script to verify CometAPI (Anthropic Compatible) functionality
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def test_comet_api():
    """Test if the CometAPI key works with Anthropic Compatible endpoint"""
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')  # Can reuse same env var
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("💡 Add your CometAPI key as ANTHROPIC_API_KEY in .env")
        return False
    
    print(f"🔑 Testing CometAPI Key: {api_key[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 100,
        'messages': [
            {
                'role': 'user',
                'content': 'Say hello in Indonesian and tell me if this CometAPI connection is working!'
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.cometapi.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    # CometAPI may return different response format
                    if 'choices' in data and len(data['choices']) > 0:
                        message = data['choices'][0].get('message', {}).get('content', 'No response')
                    elif 'content' in data:
                        message = data.get('content', [{}])[0].get('text', 'No response')
                    else:
                        message = str(data)
                    
                    print(f"✅ CometAPI Working!")
                    print(f"📝 Response: {message}")
                    return True
                
                elif response.status == 401:
                    print("❌ API Key Invalid or Expired")
                    print("💡 Check your CometAPI key configuration")
                    return False
                
                elif response.status == 402:
                    print("⚠️  API Key Valid but No Credits/Billing")
                    print("💳 Check your CometAPI billing status")
                    print("🆓 You might have a free tier available")
                    return False
                
                elif response.status == 429:
                    print("⏱️  Rate Limited - API Key Valid")
                    print("🔄 Try again in a few minutes")
                    return True
                
                else:
                    error_text = await response.text()
                    print(f"❌ CometAPI Error {response.status}: {error_text}")
                    # Try alternative endpoint if main one fails
                    print("🔄 Trying alternative endpoint...")
                    return await test_comet_messages_endpoint(session, headers, payload)
                    
    except Exception as e:
        print(f"❌ Network Error: {str(e)}")
        return False

async def test_comet_messages_endpoint(session, headers, payload):
    """Test alternative CometAPI messages endpoint"""
    try:
        async with session.post(
            'https://api.cometapi.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            
            if response.status == 200:
                data = await response.json()
                message = data.get('content', [{}])[0].get('text', 'No response from messages endpoint')
                print(f"✅ CometAPI Messages Endpoint Working!")
                print(f"📝 Response: {message}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Messages Endpoint Error {response.status}: {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ Messages Endpoint Error: {str(e)}")
        return False

async def main():
    print("🧪 VNCagentic - CometAPI Test")
    print("=" * 40)
    
    success = await test_comet_api()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Ready to run VNCagentic with CometAPI!")
        print("🚀 Next: Run 'docker-compose up -d'")
    else:
        print("❌ Fix CometAPI configuration first")
        print("📖 Check documentation for setup help")

if __name__ == "__main__":
    try:
        import aiohttp
        from dotenv import load_dotenv
        asyncio.run(main())
    except ImportError as e:
        print("❌ Missing dependencies. Install with:")
        print("pip install aiohttp python-dotenv")
