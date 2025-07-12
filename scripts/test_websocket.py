"""
Test script for WebSocket chat functionality
"""

import asyncio
import websockets
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


async def test_websocket_chat():
    """Test WebSocket chat functionality"""
    uri = "ws://localhost:8000/ws/chat/test_user"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔌 Connected to WebSocket chat!")
            
            # Test messages
            test_messages = [
                "help",
                "What's my balance?",
                "Send 50 USDT to Alice",
                "Invest my ₹2000 salary this month"
            ]
            
            for message in test_messages:
                print(f"\n📤 Sending: {message}")
                
                # Send message
                await websocket.send(json.dumps({"message": message}))
                
                # Receive response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                print(f"📥 Received: {response_data['message']}")
                print(f"   From: {response_data['sender']}")
                print(f"   Type: {response_data['type']}")
                
                # Wait a bit between messages
                await asyncio.sleep(1)
            
            print("\n✅ WebSocket chat test completed!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing WebSocket Chat Functionality")
    print("Make sure the FastAPI server is running on localhost:8000")
    print("=" * 50)
    
    asyncio.run(test_websocket_chat()) 