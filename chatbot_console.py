#!/usr/bin/env python3
"""
Console Chatbot for Finance Agent (Mock UPI Data + Azure OpenAI)
"""

import os
import asyncio

# Set up test environment variables (reuse from test_finance_agent.py)
os.environ.update({
    "MONGO_URI": "mongodb+srv://hs05june:1234567890@cluster0.xpqjxvh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
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
    "ESCROW_PRIVATE_KEY": "test_escrow_key"
})

from src.services.nlp_service import nlp_service

async def chatbot():
    print("\n🚀 Welcome to the AI-Powered Finance Agent!")
    print("=" * 50)
    print("💰 Your personal financial assistant for UPI transactions and crypto")
    print("=" * 50)
    print("\n📱 GETTING STARTED:")
    print("1️⃣ Register your UPI ID with: \"My UPI ID is username@provider\"")
    print("2️⃣ Get financial insights with: \"Analyze my transactions\"")
    print("3️⃣ View a summary with: \"Show me transaction summary\"")
    print("4️⃣ Get investment advice with: \"Invest 5000 rupees\"")
    print("\nType 'help' to see all available commands")
    print("Type 'exit' to quit\n")
    
    # Use a default user ID without prompting
    user_id = "default_user"
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
        if not user_input:
            continue
        print("AI is thinking...", end="\r")
        try:
            response = await nlp_service.process_nlp_message(user_input, user_id)
            print(" " * 40, end="\r")  # Clear the 'AI is thinking...' line
            print(f"AI: {response}\n")
        except Exception as e:
            print(f"[Error] {e}\n")

if __name__ == "__main__":
    asyncio.run(chatbot()) 