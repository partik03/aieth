"""
REST API for AI-powered wallet assistant chat
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from src.models.user import User
from src.api.dependencies import get_current_user
from src.services.nlp_service import nlp_service


class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User's message to the AI assistant")


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="AI assistant's response")
    timestamp: str = Field(..., description="Timestamp of the response")
    user_id: str = Field(..., description="User ID who sent the message")


router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

# Hardcoded test user for hackathon/demo
TEST_USER = User(
    id="test_user_111111111111",
    aadhaar_number="111111111111",
    full_name="Test User",
    aadhaar_verified=True,
    created_at=datetime.now()
)


@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a message to the AI wallet assistant (no auth, hardcoded user)
    
    - **message**: Your message to the AI assistant
    - Returns AI assistant's response
    
    The AI can help with:
    - Checking wallet balances
    - Transferring funds
    - Investment strategies
    - Transaction analysis
    - Financial insights
    - UPI registration
    """
    try:
        # Process the message with NLP service using hardcoded user
        ai_response = await nlp_service.process_nlp_message(request.message, TEST_USER.id)
        
        # Log the interaction
        print(f"📨 User {TEST_USER.id}: {request.message}")
        print(f"🤖 AI Assistant: {ai_response}")
        
        return ChatResponse(
            success=True,
            message=ai_response,
            timestamp=datetime.now().isoformat(),
            user_id=TEST_USER.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to process message: {str(e)}",
                "error_code": "CHAT_ERROR"
            }
        )


@router.get("/help")
async def get_chat_help():
    """
    Get help information about the AI chatbot capabilities
    """
    help_message = """
🤖 **AI Wallet Assistant - Available Commands**

**💰 Balance & Transactions:**
- "Check my balance" - View wallet balances
- "What's my balance?" - Check INR and crypto balances
- "Analyze my transactions" - Get transaction analysis
- "Show transaction summary" - Monthly spending summary

**💸 Transfers:**
- "Send 100 INR to Alice" - Transfer INR to a contact
- "Transfer 0.5 ETH to Bob" - Transfer crypto to a contact
- "Pay 50 USDT to Charlie" - Transfer USDT

**📈 Investment & Salary:**
- "Invest my salary" - Get investment strategy for salary
- "Buy crypto with 10000 INR" - Purchase crypto
- "Investment advice" - Get financial insights

**🏦 UPI & Banking:**
- "Register my UPI ID" - Add UPI ID to your account
- "My UPI ID is user@upi" - Set your UPI ID

**💡 Financial Insights:**
- "Financial insights" - Get spending analysis
- "Money advice" - Receive financial recommendations
- "Spending analysis" - Analyze your spending patterns

**❓ Help:**
- "Help" - Show this help message
- "What can you do?" - List available features

**📞 Available Contacts:**
- Alice, Bob, Charlie, David, Emma

**🪙 Supported Tokens:**
- INR, BTC, ETH, MATIC, SOL, DOGE, USDT, USDC
    """
    
    return {
        "success": True,
        "help": help_message.strip(),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/status")
async def get_chat_status():
    """
    Get chat system status and user information (no auth, hardcoded user)
    """
    try:
        # Get user's wallet info
        from src.services.wallet_service import wallet_service
        wallet = await wallet_service.get_wallet_by_user_id(TEST_USER.id)
        
        status = {
            "user_id": TEST_USER.id,
            "user_name": TEST_USER.full_name,
            "aadhaar_verified": TEST_USER.aadhaar_verified,
            "chat_status": "active",
            "ai_model": "GPT-4",
            "available_features": [
                "balance_check",
                "fund_transfer", 
                "investment_advice",
                "transaction_analysis",
                "upi_registration",
                "financial_insights"
            ],
            "wallet_connected": wallet is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get chat status: {str(e)}",
                "error_code": "STATUS_ERROR"
            }
        ) 