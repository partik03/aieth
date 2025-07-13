#!/usr/bin/env python3
"""
Development server for Crypto-UPI Backend
Sets default environment variables for testing
"""

import os
import sys
import uvicorn
from pathlib import Path

# Set default environment variables for development
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "crypto_upi_db")
os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# Set dummy API keys for development
os.environ.setdefault("OPENAI_API_KEY", "sk-dummy-key")
os.environ.setdefault("UPI_GATEWAY_API_KEY", "dummy-key")
os.environ.setdefault("UPI_GATEWAY_SECRET", "dummy-secret")
os.environ.setdefault("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/dummy")
os.environ.setdefault("POLYGON_RPC_URL", "https://polygon-rpc.com")
os.environ.setdefault("PRIVATE_KEY", "dummy-private-key")
os.environ.setdefault("CRYPTO_PRICE_API_URL", "https://api.coingecko.com/api/v3")
os.environ.setdefault("TWITTER_API_KEY", "dummy-key")
os.environ.setdefault("TWITTER_API_SECRET", "dummy-secret")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("UPI_MERCHANT_ID", "dummy-merchant-id")
os.environ.setdefault("UPI_APP_ID", "dummy-app-id")
os.environ.setdefault("UPI_CALLBACK_URL", "http://localhost:8000/api/upi/callback")
os.environ.setdefault("DIGILOCKER_CLIENT_ID", "dummy-client-id")
os.environ.setdefault("DIGILOCKER_CLIENT_SECRET", "dummy-client-secret")
os.environ.setdefault("DIGILOCKER_REDIRECT_URI", "http://localhost:8000/api/aadhaar/callback")
os.environ.setdefault("DIGILOCKER_BASE_URL", "https://api.digitallocker.gov.in")
os.environ.setdefault("AI_MODEL", "gpt-4")
os.environ.setdefault("AI_MAX_TOKENS", "1000")
os.environ.setdefault("AI_TEMPERATURE", "0.7")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://jaggery-open-ai.openai.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "5NwK8dktlJQ5ZPNBHjoBDVcgNdLASKJEF3MFCN5MfnUpKe3K2AY8JQQJ99ALACYeBjFXJ3w3AAABACOGc4FA")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-2")
os.environ.setdefault("ESCROW_WALLET_ADDRESS", "0x1234567890123456789012345678901234567890")
os.environ.setdefault("ESCROW_PRIVATE_KEY", "dummy-private-key")
os.environ.setdefault("LOAN_INTEREST_RATE", "0.12")
os.environ.setdefault("MAX_LOAN_AMOUNT", "100000")
os.environ.setdefault("MIN_CREDIT_SCORE", "600")

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    print("🚀 Starting Crypto-UPI Backend Development Server")
    print("📝 Using default environment variables for development")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 