"""
WebSocket chat API for AI-powered wallet assistant
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

from src.services.nlp_service import nlp_service


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"🔌 User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: str):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"🔌 User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


# Global connection manager
manager = ConnectionManager()


async def format_chat_message(message: str, sender: str = "user", timestamp: str = None) -> str:
    """Format chat message as JSON"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    return json.dumps({
        "message": message,
        "sender": sender,
        "timestamp": timestamp,
        "type": "chat"
    })


async def format_system_message(message: str, message_type: str = "info") -> str:
    """Format system message as JSON"""
    return json.dumps({
        "message": message,
        "sender": "system",
        "timestamp": datetime.now().isoformat(),
        "type": message_type
    })


async def handle_websocket_chat(websocket: WebSocket, user_id: str):
    """Handle WebSocket chat connection"""
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        welcome_msg = await format_system_message(
            f"🤖 Welcome to AI Wallet Assistant! I can help you with transfers, balance checks, and investment strategies. Type 'help' to see what I can do.",
            "welcome"
        )
        await websocket.send_text(welcome_msg)
        
        # Handle incoming messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                
                # Parse message
                try:
                    message_data = json.loads(data)
                    user_message = message_data.get("message", "").strip()
                except json.JSONDecodeError:
                    # Handle plain text messages
                    user_message = data.strip()
                
                if not user_message:
                    continue
                
                # Log incoming message
                print(f"📨 User {user_id}: {user_message}")
                
                # Send user message back (echo)
                user_msg = await format_chat_message(user_message, "user")
                await websocket.send_text(user_msg)
                
                # Process message with NLP service
                ai_response = await nlp_service.process_nlp_message(user_message, user_id)
                
                # Send AI response
                ai_msg = await format_chat_message(ai_response, "assistant")
                await websocket.send_text(ai_msg)
                
                # Log AI response
                print(f"🤖 AI Assistant: {ai_response}")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                # Send error message
                error_msg = await format_system_message(
                    f"❌ Error processing message: {str(e)}",
                    "error"
                )
                await websocket.send_text(error_msg)
                print(f"Error in WebSocket chat: {e}")
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(user_id)


# WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for chat"""
    await handle_websocket_chat(websocket, user_id) 