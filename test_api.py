"""
Test script to verify Anthropic API key functionality
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

async def test_anthropic_api():
    """Test if the Anthropic API key works"""
    load_dotenv()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        return False
    
    print(f"🔑 Testing API Key: {api_key[:20]}...")
    
    headers = {
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    
    payload = {
        'model': 'claude-3-5-sonnet-20241022',
        'max_tokens': 100,
        'messages': [
            {
                'role': 'user',
                'content': 'Say hello in Indonesian and tell me if this API key is working!'
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get('content', [{}])[0].get('text', 'No response')
                    print(f"✅ API Key Working!")
                    print(f"📝 Claude Response: {message}")
                    return True
                
                elif response.status == 401:
                    print("❌ API Key Invalid or Expired")
                    print("💡 Check your API key at https://console.anthropic.com")
                    return False
                
                elif response.status == 402:
                    print("⚠️  API Key Valid but No Credits/Billing")
                    print("💳 Add billing info at https://console.anthropic.com")
                    print("🆓 You might have a small free tier available")
                    return False
                
                elif response.status == 429:
                    print("⏱️  Rate Limited - API Key Valid")
                    print("🔄 Try again in a few minutes")
                    return True
                
                else:
                    error_text = await response.text()
                    print(f"❌ API Error {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Network Error: {str(e)}")
        return False

async def main():
    print("🧪 VNCagentic - API Key Test")
    print("=" * 40)
    
    success = await test_anthropic_api()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Ready to run VNCagentic!")
        print("🚀 Next: Run 'docker-compose up -d'")
    else:
        print("❌ Fix API key issues first")
        print("📖 Check documentation for setup help")

if __name__ == "__main__":
    try:
        import aiohttp
        from dotenv import load_dotenv
        asyncio.run(main())
    except ImportError as e:
        print("❌ Missing dependencies. Install with:")
        print("pip install aiohttp python-dotenv")
