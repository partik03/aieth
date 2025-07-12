"""
NLP service for processing natural language wallet commands
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from src.services.ai_agent import ai_agent_service
from src.services.wallet_service import wallet_service
from src.services.salary_service import salary_service
from src.services.twitter_service import twitter_service
from src.services.finance_agent import finance_agent_service
from src.services.mock_upi_data import mock_upi_data_service
from src.services.upi_data_service import upi_data_service


class NLPService:
    """Service for processing natural language wallet commands"""
    
    def __init__(self):
        # Mock recipient database (in real app, this would be in MongoDB)
        self.recipient_db = {
            "alice": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "bob": "0x1234567890123456789012345678901234567890",
            "charlie": "0xabcdef1234567890abcdef1234567890abcdef12",
            "david": "0x9876543210987654321098765432109876543210",
            "emma": "0xfedcba0987654321fedcba0987654321fedcba09"
        }
        
        # Supported tokens and their symbols
        self.supported_tokens = {
            "bitcoin": "BTC", "btc": "BTC",
            "ethereum": "ETH", "eth": "ETH",
            "polygon": "MATIC", "matic": "MATIC",
            "solana": "SOL", "sol": "SOL",
            "dogecoin": "DOGE", "doge": "DOGE",
            "usdt": "USDT", "tether": "USDT",
            "usdc": "USDC", "usd coin": "USDC"
        }
    
    async def process_nlp_message(self, message: str, user_id: str) -> str:
        """Process natural language message and return response"""
        try:
            # Convert to lowercase for easier processing
            message_lower = message.lower().strip()
            
            # Detect intent
            intent = self._detect_intent(message_lower)
            
            if intent == "transfer":
                return await self._handle_transfer(message_lower, user_id)
            elif intent == "check_balance":
                return await self._handle_check_balance(user_id)
            elif intent == "invest_salary":
                return await self._handle_invest_salary(message_lower, user_id)
            elif intent == "analyze_transactions":
                return await self._handle_analyze_transactions(user_id)
            elif intent == "financial_insights":
                return await self._handle_financial_insights(user_id)
            elif intent == "transaction_summary":
                return await self._handle_transaction_summary(user_id)
            elif intent == "register_upi":
                return await self._handle_register_upi(message_lower, user_id)
            elif intent == "help":
                return self._get_help_message()
            else:
                return "🤖 I'm not sure what you want to do. Try saying 'help' to see what I can do!"
                
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the message"""
        # Transfer patterns
        transfer_patterns = [
            r"send\s+\d+",
            r"transfer\s+\d+",
            r"pay\s+\d+",
            r"give\s+\d+"
        ]
        
        # Balance patterns
        balance_patterns = [
            r"balance",
            r"how much",
            r"what.*balance",
            r"check.*balance"
        ]
        
        # Investment patterns
        invest_patterns = [
            r"invest",
            r"buy.*crypto",
            r"purchase.*crypto",
            r"salary.*invest"
        ]
        
        # Help patterns
        help_patterns = [
            r"help",
            r"what.*can.*do",
            r"commands",
            r"options"
        ]
        
        # Transaction analysis patterns
        transaction_patterns = [
            r"analyze.*transaction",
            r"transaction.*analysis",
            r"spending.*analysis",
            r"analyze.*spending"
        ]
        
        # Financial insights patterns
        insights_patterns = [
            r"financial.*insight",
            r"money.*insight",
            r"spending.*insight",
            r"financial.*advice",
            r"money.*advice"
        ]
        
        # Transaction summary patterns
        summary_patterns = [
            r"transaction.*summary",
            r"spending.*summary",
            r"summary.*transaction",
            r"monthly.*summary"
        ]
        
        # UPI registration patterns
        upi_patterns = [
            r"register.*upi",
            r"add.*upi",
            r"connect.*upi",
            r"set.*upi",
            r"my upi.*is",
            r"upi.*id.*is",
            r"use.*upi.*id"
        ]
        
        # Check patterns
        for pattern in transfer_patterns:
            if re.search(pattern, message):
                return "transfer"
        
        for pattern in balance_patterns:
            if re.search(pattern, message):
                return "check_balance"
        
        for pattern in invest_patterns:
            if re.search(pattern, message):
                return "invest_salary"
        
        for pattern in transaction_patterns:
            if re.search(pattern, message):
                return "analyze_transactions"
        
        for pattern in insights_patterns:
            if re.search(pattern, message):
                return "financial_insights"
        
        for pattern in summary_patterns:
            if re.search(pattern, message):
                return "transaction_summary"
        
        for pattern in upi_patterns:
            if re.search(pattern, message):
                return "register_upi"
        
        for pattern in help_patterns:
            if re.search(pattern, message):
                return "help"
        
        return "unknown"
    
    async def _handle_transfer(self, message: str, user_id: str) -> str:
        """Handle transfer intent"""
        try:
            # Extract amount and token
            amount_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if not amount_match:
                return "❌ Please specify an amount to transfer."
            
            amount = float(amount_match.group(1))
            
            # Extract token
            token = "INR"  # Default to INR
            for token_name, token_symbol in self.supported_tokens.items():
                if token_name in message:
                    token = token_symbol
                    break
            
            # Extract recipient
            recipient = None
            for name in self.recipient_db.keys():
                if name in message:
                    recipient = name
                    break
            
            if not recipient:
                return "❌ Please specify a recipient (Alice, Bob, Charlie, David, or Emma)."
            
            # Get recipient wallet address
            recipient_address = self.recipient_db[recipient]
            
            # Check if user has sufficient balance
            wallet = await wallet_service.get_wallet_by_user_id(user_id)
            if not wallet:
                return "❌ Wallet not found. Please create a wallet first."
            
            if token == "INR":
                if wallet.fiat_balance < amount:
                    return f"❌ Insufficient INR balance. You have ₹{wallet.fiat_balance:.2f}"
            else:
                if wallet.crypto_balance.get(token, 0) < amount:
                    return f"❌ Insufficient {token} balance. You have {wallet.crypto_balance.get(token, 0)} {token}"
            
            # Perform transfer (mock for now)
            # In real implementation, you would call wallet_service.transfer()
            
            return f"💸 Successfully sent {amount} {token} to {recipient.capitalize()}!"
            
        except Exception as e:
            return f"❌ Transfer failed: {str(e)}"
    
    async def _handle_check_balance(self, user_id: str) -> str:
        """Handle check balance intent"""
        try:
            wallet = await wallet_service.get_wallet_by_user_id(user_id)
            if not wallet:
                return "❌ Wallet not found. Please create a wallet first."
            
            # Format crypto balances
            crypto_balances = []
            for token, balance in wallet.crypto_balance.items():
                if balance > 0:
                    crypto_balances.append(f"{balance} {token}")
            
            crypto_text = ", ".join(crypto_balances) if crypto_balances else "0"
            
            return f"💼 Your wallet balance:\n💰 INR: ₹{wallet.fiat_balance:.2f}\n🪙 Crypto: {crypto_text}"
            
        except Exception as e:
            return f"❌ Failed to check balance: {str(e)}"
    
    async def _handle_analyze_transactions(self, user_id: str) -> str:
        """Handle transaction analysis intent"""
        try:
            # Try to get transactions from UPI data service first
            transactions = await upi_data_service.get_transactions(user_id, days=90)
            
            if not transactions:
                # Fall back to mock data if no real transactions
                transactions = mock_upi_data_service.get_user_transactions(user_id, days=90)
            
            if not transactions:
                return "❌ No transaction data found for analysis."
            
            # Analyze transactions using finance agent
            analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
            
            if not analysis_result.get("success"):
                return f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}"
            
            analysis = analysis_result.get("analysis", {})
            structured_analysis = analysis.get("structured_analysis", {})
            
            # Format response
            response = "📊 **Transaction Analysis Results**\n\n"
            
            # Add spending analysis
            if structured_analysis.get("spending_analysis"):
                response += "🔍 **Spending Analysis:**\n"
                response += structured_analysis["spending_analysis"][:300] + "...\n\n"
            
            # Add financial health
            if structured_analysis.get("financial_health"):
                response += "💹 **Financial Health:**\n"
                response += structured_analysis["financial_health"][:300] + "...\n\n"
            
            # Add key metrics
            key_metrics = analysis.get("key_metrics", {})
            if key_metrics:
                response += "📈 **Key Metrics:**\n"
                response += f"- Total Spent: ₹{key_metrics.get('total_spent', 0):,.2f}\n"
                response += f"- Transactions: {key_metrics.get('transaction_count', 0)}\n"
                response += f"- Average: ₹{key_metrics.get('avg_transaction', 0):,.2f}\n"
                response += f"- Top Category: {key_metrics.get('top_category', 'N/A')}\n\n"
            
            # Add next steps
            if structured_analysis.get("next_steps"):
                response += "👣 **Recommended Next Steps:**\n"
                response += structured_analysis["next_steps"][:300] + "...\n"
            
            return response
            
        except Exception as e:
            return f"❌ Analysis failed: {str(e)}"
    
    async def _handle_financial_insights(self, user_id: str) -> str:
        """Handle financial insights intent"""
        try:
            # Try to get transactions from UPI data service first
            transactions = await upi_data_service.get_transactions(user_id, days=90)
            
            if not transactions:
                # Fall back to mock data if no real transactions
                transactions = mock_upi_data_service.get_user_transactions(user_id, days=90)
            
            if not transactions:
                return "❌ No transaction data found for insights."
            
            # Get transaction summary
            summary = upi_data_service.get_transaction_summary(transactions)
            
            # Analyze transactions
            analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
            
            if not analysis_result.get("success"):
                return f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}"
            
            # Get recommendations
            recommendations_result = await finance_agent_service.get_financial_recommendations(
                user_id, analysis_result.get("analysis", {})
            )
            
            if not recommendations_result.get("success"):
                return f"❌ Recommendations failed: {recommendations_result.get('error', 'Unknown error')}"
            
            # Format response
            response = "🧠 **Financial Insights & Recommendations**\n\n"
            
            # Add summary
            response += "📊 **Quick Summary:**\n"
            response += f"• Total Transactions: {summary.get('total_transactions', 0)}\n"
            response += f"• Net Amount: ₹{summary.get('net_amount', 0):,.2f}\n"
            response += f"• Average Transaction: ₹{summary.get('average_transaction', 0):,.2f}\n\n"
            
            # Add recommendations
            recommendations = recommendations_result.get("recommendations", "")
            if recommendations:
                # Extract just the first part of recommendations (they can be lengthy)
                response += "💡 **Key Recommendations:**\n"
                
                # Try to extract bullet points
                bullet_points = re.findall(r'[•\-\*]\s+([^\n]+)', recommendations)
                if bullet_points:
                    # Take first 5 bullet points
                    for i, point in enumerate(bullet_points[:5]):
                        response += f"• {point}\n"
                    
                    if len(bullet_points) > 5:
                        response += "• ...\n"
                else:
                    # Just take first 300 chars
                    response += recommendations[:300] + "...\n"
            
            return response
            
        except Exception as e:
            return f"❌ Insights failed: {str(e)}"
    
    async def _handle_transaction_summary(self, user_id: str) -> str:
        """Handle transaction summary intent"""
        try:
            # Try to get transactions from UPI data service first
            transactions = await upi_data_service.get_transactions(user_id, days=30)
            
            if not transactions:
                # Fall back to mock data if no real transactions
                transactions = mock_upi_data_service.get_user_transactions(user_id, days=30)
            
            if not transactions:
                return "❌ No transaction data found for summary."
            
            # Get summary
            summary = upi_data_service.get_transaction_summary(transactions)
            
            # Format response
            response = "📋 **Transaction Summary (Last 30 Days)**\n\n"
            
            # Financial overview
            response += "💰 **Financial Overview:**\n"
            response += f"• Total Amount: ₹{summary.get('total_amount', 0):,.2f}\n"
            response += f"• Total Transactions: {summary.get('total_transactions', 0)}\n"
            response += f"• Average Transaction: ₹{summary.get('average_transaction', 0):,.2f}\n\n"
            
            # Category breakdown
            response += "📊 **Top Spending Categories:**\n"
            top_categories = summary.get('top_categories', [])
            for category, amount in top_categories[:5]:
                percentage = (amount / summary.get('total_amount', 1)) * 100
                response += f"• {category}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
            
            # Transaction types
            response += f"\n💸 **Transaction Types:**\n"
            response += f"• Debits: {summary.get('debit_transactions', 0)} (₹{summary.get('debit_amount', 0):,.2f})\n"
            response += f"• Credits: {summary.get('credit_transactions', 0)} (₹{summary.get('credit_amount', 0):,.2f})\n"
            response += f"• Net Amount: ₹{summary.get('net_amount', 0):,.2f}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Summary failed: {str(e)}"
    
    async def _handle_register_upi(self, message: str, user_id: str) -> str:
        """Handle UPI registration intent"""
        try:
            # Extract UPI ID from message
            upi_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)', message)
            
            if not upi_match:
                return "❌ Please provide a valid UPI ID in the format username@provider (e.g., johndoe@okicici)"
            
            upi_id = upi_match.group(1)
            
            # Register UPI ID
            result = await upi_data_service.collect_upi_data(user_id, upi_id)
            
            if result.get("success"):
                return f"✅ Successfully registered UPI ID: {upi_id}\n\nYou can now use commands like 'analyze my transactions' or 'show me financial insights' to get personalized financial analysis based on your UPI transactions!"
            else:
                return f"❌ Failed to register UPI ID: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ UPI registration failed: {str(e)}"
    
    async def _handle_invest_salary(self, message: str, user_id: str) -> str:
        """Handle invest salary intent"""
        try:
            # Extract amount
            amount_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if not amount_match:
                return "❌ Please specify an amount to invest."
            
            amount = float(amount_match.group(1))
            
            # Call salary service to invest
            investment_result = await salary_service.invest_salary(user_id, amount)
            
            if investment_result.get("success"):
                strategy = investment_result.get("strategy", "")
                return f"📈 Investment Strategy Generated!   \n\n💰 Salary: ₹{amount}\n🎯 Allocation: {strategy}\n\n💡 Reasoning: {investment_result.get('reasoning', 'Strategy based on market analysis')}"
            else:
                return f"❌ Investment failed: {investment_result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Investment failed: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        help_message = "🤖 **AI Wallet Assistant - Available Commands**\n\n"
        
        help_message += "💸 **Transfer Money:**\n"
        help_message += "- \"Send 50 USDT to Alice\"\n"
        help_message += "- \"Transfer 1000 INR to Bob\"\n"
        help_message += "- \"Pay 25 ETH to Charlie\"\n\n"
        
        help_message += "💼 **Check Balance:**\n"
        help_message += "- \"What's my balance?\"\n"
        help_message += "- \"Check my wallet balance\"\n"
        help_message += "- \"How much do I have?\"\n\n"
        
        help_message += "📈 **Invest Salary:**\n"
        help_message += "- \"Invest my ₹2000 salary this month\"\n"
        help_message += "- \"Buy crypto with ₹5000\"\n"
        help_message += "- \"Purchase crypto for ₹1000\"\n\n"
        
        help_message += "📊 **Financial Analysis:**\n"
        help_message += "- \"Analyze transactions\" - Deep transaction analysis with AI insights\n"
        help_message += "- \"Financial insights\" - Get personalized financial advice\n"
        help_message += "- \"Transaction summary\" - Monthly spending summary\n"
        help_message += "- \"Spending analysis\" - Detailed spending pattern analysis\n\n"
        
        help_message += "🔗 **Connect UPI:**\n"
        help_message += "- \"Register my UPI ID username@provider\"\n"
        help_message += "- \"Connect my UPI ID username@provider\"\n"
        help_message += "- \"My UPI ID is username@provider\"\n\n"
        
        help_message += "❓ **Help:**\n"
        help_message += "- \"Help\" or \"What can you do?\"\n\n"
        
        help_message += "**Supported Recipients:** Alice, Bob, Charlie, David, Emma\n"
        help_message += "**Supported Tokens:** BTC, ETH, MATIC, SOL, DOGE, USDT, USDC, INR"
        
        return help_message
    
    def get_recipient_address(self, name: str) -> Optional[str]:
        """Get recipient wallet address by name"""
        return self.recipient_db.get(name.lower())


# Create singleton instance
nlp_service = NLPService() 