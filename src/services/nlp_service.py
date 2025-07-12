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
            # Generate mock transactions for the user
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
            
            if structured_analysis.get("spending_analysis"):
                response += f"🔍 **Spending Analysis:**\n{structured_analysis['spending_analysis']}\n\n"
            
            if structured_analysis.get("financial_health"):
                response += f"💚 **Financial Health:**\n{structured_analysis['financial_health']}\n\n"
            
            if structured_analysis.get("savings_opportunities"):
                response += f"💰 **Savings Opportunities:**\n{structured_analysis['savings_opportunities']}\n\n"
            
            if structured_analysis.get("next_steps"):
                response += f"🎯 **Next Steps:**\n{structured_analysis['next_steps']}\n\n"
            
            response += f"📈 **Key Metrics:**\n"
            key_metrics = analysis.get("key_metrics", {})
            response += f"• Total Spent: ₹{key_metrics.get('total_spent', 0):,.2f}\n"
            response += f"• Transactions: {key_metrics.get('transaction_count', 0)}\n"
            response += f"• Average Transaction: ₹{key_metrics.get('avg_transaction', 0):,.2f}\n"
            response += f"• Top Category: {key_metrics.get('top_category', 'N/A')}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Transaction analysis failed: {str(e)}"
    
    async def _handle_financial_insights(self, user_id: str) -> str:
        """Handle financial insights intent"""
        try:
            # Generate mock transactions
            transactions = mock_upi_data_service.get_user_transactions(user_id, days=60)
            
            if not transactions:
                return "❌ No transaction data available for insights."
            
            # Get transaction summary
            summary = mock_upi_data_service.get_transaction_summary(transactions)
            
            # Get AI-powered recommendations
            analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
            
            if not analysis_result.get("success"):
                return f"❌ Insights generation failed: {analysis_result.get('error', 'Unknown error')}"
            
            # Get detailed recommendations
            recommendations_result = await finance_agent_service.get_financial_recommendations(
                user_id, analysis_result.get("analysis", {})
            )
            
            # Format response
            response = "🧠 **Financial Insights & Recommendations**\n\n"
            
            # Add summary statistics
            response += f"📊 **Quick Summary:**\n"
            response += f"• Total Transactions: {summary.get('total_transactions', 0)}\n"
            response += f"• Net Amount: ₹{summary.get('net_amount', 0):,.2f}\n"
            response += f"• Average Transaction: ₹{summary.get('average_transaction', 0):,.2f}\n\n"
            
            # Add AI recommendations
            if recommendations_result.get("success"):
                response += f"💡 **AI Recommendations:**\n{recommendations_result.get('recommendations', 'No recommendations available.')}\n\n"
            else:
                response += f"💡 **General Advice:**\nConsider reviewing your spending patterns and setting up automatic savings transfers.\n\n"
            
            # Add top spending categories
            categories = summary.get('categories', {})
            if categories:
                response += f"🏷️ **Top Spending Categories:**\n"
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
                for category, amount in sorted_categories:
                    response += f"• {category}: ₹{amount:,.2f}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Financial insights failed: {str(e)}"
    
    async def _handle_transaction_summary(self, user_id: str) -> str:
        """Handle transaction summary intent"""
        try:
            # Generate mock transactions
            transactions = mock_upi_data_service.get_user_transactions(user_id, days=30)
            
            if not transactions:
                return "❌ No transaction data available for summary."
            
            # Get detailed summary
            summary = mock_upi_data_service.get_transaction_summary(transactions)
            
            # Format response
            response = "📋 **Transaction Summary (Last 30 Days)**\n\n"
            
            response += f"💰 **Financial Overview:**\n"
            response += f"• Total Amount: ₹{summary.get('total_amount', 0):,.2f}\n"
            response += f"• Total Transactions: {summary.get('total_transactions', 0)}\n"
            response += f"• Average Transaction: ₹{summary.get('average_transaction', 0):,.2f}\n"
            response += f"• Net Amount: ₹{summary.get('net_amount', 0):,.2f}\n\n"
            
            response += f"📊 **Transaction Breakdown:**\n"
            response += f"• Debit Transactions: {summary.get('debit_transactions', 0)} (₹{summary.get('debit_amount', 0):,.2f})\n"
            response += f"• Credit Transactions: {summary.get('credit_transactions', 0)} (₹{summary.get('credit_amount', 0):,.2f})\n\n"
            
            # Add category breakdown
            categories = summary.get('categories', {})
            if categories:
                response += f"🏷️ **Category Breakdown:**\n"
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                for category, amount in sorted_categories[:5]:  # Top 5 categories
                    percentage = (amount / summary.get('total_amount', 1)) * 100
                    response += f"• {category}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
            
            return response
            
        except Exception as e:
            return f"❌ Transaction summary failed: {str(e)}"
    
    async def _handle_invest_salary(self, message: str, user_id: str) -> str:
        """Handle invest salary intent"""
        try:
            # Extract salary amount
            amount_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if not amount_match:
                return "❌ Please specify a salary amount to invest."
            
            amount = float(amount_match.group(1))
            
            # Create mock salary data
            salary_data = {
                "user_id": user_id,
                "amount": amount,
                "employer": "User Input",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Get trending tokens
            trending_tokens = await twitter_service.get_trending_tokens()
            
            # Generate investment strategy
            strategy_result = await ai_agent_service.generate_investment_strategy(
                salary_data, 
                trending_tokens
            )
            
            if not strategy_result.get("success"):
                return "❌ Failed to generate investment strategy."
            
            strategy = strategy_result.get("strategy", {})
            
            # Format strategy response
            strategy_text = []
            for token, percentage in strategy.items():
                strategy_text.append(f"{percentage}% {token}")
            
            strategy_summary = ", ".join(strategy_text)
            
            return f"📈 Investment Strategy Generated!\n\n💰 Salary: ₹{amount}\n🎯 Allocation: {strategy_summary}\n\n💡 Reasoning: {strategy_result.get('reasoning', 'AI-generated strategy')}"
            
        except Exception as e:
            return f"❌ Investment strategy generation failed: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        return """🤖 **AI Wallet Assistant - Available Commands**

💸 **Transfer Money:**
- "Send 50 USDT to Alice"
- "Transfer 1000 INR to Bob"
- "Pay 25 ETH to Charlie"

💼 **Check Balance:**
- "What's my balance?"
- "Check my wallet balance"
- "How much do I have?"

📈 **Invest Salary:**
- "Invest my ₹2000 salary this month"
- "Buy crypto with ₹5000"
- "Purchase crypto for ₹1000"

📊 **Financial Analysis:**
- "Analyze transactions" - Deep transaction analysis with AI insights
- "Financial insights" - Get personalized financial advice
- "Transaction summary" - Monthly spending summary
- "Spending analysis" - Detailed spending pattern analysis

❓ **Help:**
- "Help" or "What can you do?"

**Supported Recipients:** Alice, Bob, Charlie, David, Emma
**Supported Tokens:** BTC, ETH, MATIC, SOL, DOGE, USDT, USDC, INR"""
    
    def get_recipient_address(self, name: str) -> Optional[str]:
        """Get wallet address for a recipient name"""
        return self.recipient_db.get(name.lower())


# Global NLP service instance
nlp_service = NLPService() 