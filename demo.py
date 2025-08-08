#!/usr/bin/env python3
"""
Demo script to test the VNCagentic system according to requirements.

This script tests the two specific use cases mentioned in the requirements:
1. "Search the weather in Dubai"
2. "Search the weather in San Francisco"

And verifies that both sessions are properly stored in history.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class VNCagenticDemo:
    def __init__(self):
        self.api_url = "http://localhost:8000/api/v1"
        self.session_1 = None
        self.session_2 = None
    
    async def create_session(self, title: str) -> Dict[str, Any]:
        """Create a new agent session"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/sessions",
                json={
                    "title": title,
                    "model": "claude-sonnet-4-20250514",
                    "api_provider": "anthropic",
                    "user_id": 1
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to create session: {response.status}")
    
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message to an agent session"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages/{session_id}/messages",
                json={
                    "content": message,
                    "role": "user",
                    "session_id": session_id
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to send message: {response.status}")
    
    async def get_session_history(self) -> Dict[str, Any]:
        """Get all session history"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/sessions") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get sessions: {response.status}")
    
    async def get_messages(self, session_id: str) -> Dict[str, Any]:
        """Get messages for a session"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/messages/{session_id}/messages"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get messages: {response.status}")
    
    async def run_demo(self):
        """Run the complete demo according to requirements"""
        print("🚀 Starting VNCagentic Demo")
        print("=" * 50)
        
        # Usage Case 1: Search weather in Dubai
        print("\n📍 Usage Case 1: Search weather in Dubai")
        print("-" * 40)
        
        try:
            self.session_1 = await self.create_session("Weather in Dubai")
            print(f"✅ Created session 1: {self.session_1['id'][:8]}...")
            
            # Send the weather query
            message_response = await self.send_message(
                self.session_1['id'],
                "Search the weather in Dubai"
            )
            print(f"✅ Sent message: {message_response['content']}")
            
            # Wait for processing (in real scenario, this would be handled via WebSocket)
            print("⏳ Processing... (waiting for agent to respond)")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Error in Usage Case 1: {e}")
        
        # Usage Case 2: Search weather in San Francisco
        print("\n📍 Usage Case 2: Search weather in San Francisco")
        print("-" * 40)
        
        try:
            self.session_2 = await self.create_session("Weather in San Francisco")
            print(f"✅ Created session 2: {self.session_2['id'][:8]}...")
            
            # Send the weather query
            message_response = await self.send_message(
                self.session_2['id'],
                "Search the weather in San Francisco"
            )
            print(f"✅ Sent message: {message_response['content']}")
            
            # Wait for processing
            print("⏳ Processing... (waiting for agent to respond)")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Error in Usage Case 2: {e}")
        
        # Verify session history
        print("\n📚 Verifying Session History")
        print("-" * 40)
        
        try:
            history = await self.get_session_history()
            print(f"✅ Total sessions found: {history['total']}")
            
            for session in history['sessions']:
                print(f"  - {session['title']}: {session['status']} ({session['id'][:8]}...)")
            
            # Verify both sessions exist
            session_ids = [s['id'] for s in history['sessions']]
            if self.session_1 and self.session_1['id'] in session_ids:
                print("✅ Session 1 (Dubai) found in history")
            else:
                print("❌ Session 1 (Dubai) NOT found in history")
            
            if self.session_2 and self.session_2['id'] in session_ids:
                print("✅ Session 2 (San Francisco) found in history")
            else:
                print("❌ Session 2 (San Francisco) NOT found in history")
                
        except Exception as e:
            print(f"❌ Error verifying history: {e}")
        
        # Show message history for both sessions
        print("\n💬 Message History")
        print("-" * 40)
        
        for i, session in enumerate([self.session_1, self.session_2], 1):
            if session:
                try:
                    messages = await self.get_messages(session['id'])
                    print(f"\nSession {i} ({session['title']}):")
                    for msg in messages['messages']:
                        print(f"  {msg['role']}: {msg['content'][:50]}...")
                except Exception as e:
                    print(f"❌ Error getting messages for session {i}: {e}")
        
        print("\n🎉 Demo completed!")
        print("\nNext steps:")
        print("- Open http://localhost:3000 to see the web interface")
        print("- Open http://localhost:6080/vnc.html to see the VNC interface")
        print("- Check http://localhost:8000/docs for API documentation")


async def main():
    """Main entry point"""
    demo = VNCagenticDemo()
    
    print("Testing connection to VNCagentic API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ API is responsive")
                else:
                    print(f"❌ API returned status {response.status}")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend is running with: docker-compose up -d")
        return
    
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
