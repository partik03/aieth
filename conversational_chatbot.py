#!/usr/bin/env python3
"""
Conversational Chatbot for UPI Data Analysis (ChatGPT-like experience)
"""

import os
import asyncio
import random
import time

# Set up test environment variables (reuse from test_finance_agent.py)
os.environ.update({
    "MONGO_URI": "mongodb://localhost:27017/test",
    "DB_NAME": "test_db",
    "SECRET_KEY": "test_secret_key_12345",
    "OPENAI_API_KEY": "test_openai_key",
    "UPI_GATEWAY_API_KEY": "test_upi_key",
    "UPI_GATEWAY_SECRET": "test_upi_secret",
    "ETHEREUM_RPC_URL": "https://eth-mainnet.alchemyapi.io/v2/test",
    "POLYGON_RPC_URL": "https://polygon-mainnet.alchemyapi.io/v2/test",
    "PRIVATE_KEY": "test_private_key",
    "TWITTER_API_KEY": "test_twitter_key",
    "TWITTER_API_SECRET": "test_twitter_secret",
    "UPI_MERCHANT_ID": "test_merchant",
    "UPI_APP_ID": "test_app_id",
    "UPI_CALLBACK_URL": "http://localhost:8000/callback",
    "DIGILOCKER_CLIENT_ID": "test_digilocker_id",
    "DIGILOCKER_CLIENT_SECRET": "test_digilocker_secret",
    "DIGILOCKER_REDIRECT_URI": "http://localhost:8000/digilocker/callback",
    "DIGILOCKER_BASE_URL": "https://api.digitallocker.gov.in",
    "ESCROW_WALLET_ADDRESS": "0x1234567890123456789012345678901234567890",
    "ESCROW_PRIVATE_KEY": "test_escrow_key",
    "AZURE_OPENAI_ENDPOINT": "https://jaggery-open-ai.openai.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview",
    "AZURE_OPENAI_API_KEY": "5NwK8dktlJQ5ZPNBHjoBDVcgNdLASKJEF3MFCN5MfnUpKe3K2AY8JQQJ99ALACYeBjFXJ3w3AAABACOGc4FA",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4.1-2"
})

from src.services.conversational_agent import conversational_agent

# Typing indicator animation using synchronous code
def typing_animation(duration=1.0):
    """Show a typing animation"""
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        print(f"\rAI is thinking {animation[i % len(animation)]}", end="", flush=True)
        i += 1
        time.sleep(0.1)
    
    print("\r" + " " * 20 + "\r", end="", flush=True)

async def chatbot():
    """Run the conversational chatbot"""
    print("\n🤖 Welcome to FinChat - Your Personal Financial Assistant")
    print("=" * 60)
    print("I can analyze your UPI transactions and provide personalized insights.")
    print("I work just like ChatGPT, so you can have natural conversations about your finances.")
    print("=" * 60)
    print("\n💡 Try saying:")
    print("  • \"My UPI ID is username@provider\"")
    print("  • \"Analyze my recent transactions\"")
    print("  • \"What are my top spending categories?\"")
    print("  • \"Give me financial advice based on my spending\"")
    print("  • \"How much did I spend on food last month?\"")
    print("\nType 'exit' to quit\n")
    
    # Use a default user ID
    user_id = "default_user"
    
    # Initial greeting
    print("AI: Hello! I'm your AI financial assistant. How can I help you with your finances today?")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("\nAI: Thank you for using FinChat! Have a great day!")
            break
        if not user_input:
            continue
        
        # Show typing animation with random duration for more natural feel
        typing_duration = random.uniform(0.5, 2.0)
        typing_animation(typing_duration)
        
        try:
            # Process message through conversational agent
            response = await conversational_agent.process_message(user_input, user_id)
            print(f"AI: {response}")
        except Exception as e:
            print(f"AI: I'm sorry, I encountered an error: {str(e)}. Could you try again?")

if __name__ == "__main__":
    asyncio.run(chatbot()) 