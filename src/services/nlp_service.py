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
from src.services.investment_strategy_service import investment_strategy_service
from src.models.investment_strategy import StrategyCreateRequest, StrategyType, TriggerType
from src.services.dashboard_service import dashboard_service


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
            elif intent == "create_strategy":
                return await self._handle_create_strategy(message_lower, user_id)
            elif intent == "check_strategies":
                return await self._handle_check_strategies(user_id)
            elif intent == "check_triggers":
                return await self._handle_check_triggers(user_id)
            elif intent == "check_invoices":
                return await self._handle_check_invoices(user_id)
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
        
        # Investment strategy patterns
        strategy_patterns = [
            r"create.*strategy",
            r"add.*strategy",
            r"set.*strategy",
            r"investment.*strategy",
            r"automated.*investment",
            r"ai.*investment"
        ]
        
        # Check strategies patterns
        check_strategy_patterns = [
            r"my.*strategies",
            r"show.*strategies",
            r"list.*strategies",
            r"check.*strategies",
            r"view.*strategies"
        ]
        
        # Check triggers patterns
        trigger_patterns = [
            r"check.*triggers",
            r"any.*triggers",
            r"investment.*triggers",
            r"should.*invest",
            r"ready.*invest"
        ]
        
        # Check invoices patterns
        invoice_patterns = [
            r"check.*invoices",
            r"show.*invoices",
            r"my.*invoices",
            r"investment.*invoices",
            r"pending.*payments",
            r"payment.*requests"
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
        
        for pattern in strategy_patterns:
            if re.search(pattern, message):
                return "create_strategy"
        
        for pattern in check_strategy_patterns:
            if re.search(pattern, message):
                return "check_strategies"
        
        for pattern in trigger_patterns:
            if re.search(pattern, message):
                return "check_triggers"
        
        for pattern in invoice_patterns:
            if re.search(pattern, message):
                return "check_invoices"
        
        for pattern in help_patterns:
            if re.search(pattern, message):
                return "help"
        
        return "unknown"
    
    async def _handle_check_balance(self, user_id: str) -> str:
        """Handle check balance intent"""
        try:
            # Ensure wallet exists
            wallet = await wallet_service.ensure_wallet_exists(user_id)
            
            # Get wallet balances
            balances = await dashboard_service.get_wallet_balances(user_id)
            
            if not balances:
                return "❌ Unable to fetch wallet balances."
            
            response = "💰 **Your Wallet Balance**\n\n"
            
            # Show INR balance first
            inr_balance = balances.get("INR", 0)
            response += f"💵 **INR:** ₹{inr_balance:,.2f}\n\n"
            
            # Show crypto balances
            crypto_balances = {k: v for k, v in balances.items() if k != "INR" and v > 0}
            
            if crypto_balances:
                response += "🪙 **Crypto Holdings:**\n"
                for token, balance in crypto_balances.items():
                    response += f"• {token}: {balance:,.6f}\n"
            else:
                response += "🪙 **Crypto Holdings:** No crypto tokens\n"
            
            response += f"\n📍 **Wallet Address:** `{wallet.wallet_address}`"
            
            return response
            
        except Exception as e:
            return f"❌ Failed to check balance: {str(e)}"
    
    async def _handle_transfer(self, message: str, user_id: str) -> str:
        """Handle transfer intent"""
        try:
            # Ensure wallet exists
            wallet = await wallet_service.ensure_wallet_exists(user_id)
            
            # Extract amount and recipient from message
            amount_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if not amount_match:
                return "❌ Please specify an amount to transfer."
            
            amount = float(amount_match.group(1))
            
            # Extract recipient
            recipient = None
            for name in self.recipient_db.keys():
                if name.lower() in message.lower():
                    recipient = name
                    break
            
            if not recipient:
                return "❌ Please specify a recipient (Alice, Bob, Charlie, David, or Emma)."
            
            # Extract token type
            token = "INR"  # Default to INR
            for token_name, symbol in self.supported_tokens.items():
                if token_name.lower() in message.lower() or symbol.lower() in message.lower():
                    token = symbol
                    break
            
            # Check if user has sufficient balance
            balances = await dashboard_service.get_wallet_balances(user_id)
            current_balance = balances.get(token, 0)
            
            if current_balance < amount:
                return f"❌ Insufficient {token} balance. You have {current_balance} {token}, need {amount} {token}."
            
            # Perform transfer (mock for now, but updates database)
            if token == "INR":
                await wallet_service.update_fiat_balance(user_id, -amount)
            else:
                await wallet_service.update_crypto_balance(user_id, token, -amount)
            
            recipient_address = self.recipient_db[recipient]
            
            return f"✅ **Transfer Successful!**\n\n" \
                   f"💰 **Amount:** {amount} {token}\n" \
                   f"👤 **Recipient:** {recipient}\n" \
                   f"📍 **Address:** `{recipient_address}`\n" \
                   f"📊 **New Balance:** {current_balance - amount} {token}"
            
        except Exception as e:
            return f"❌ Transfer failed: {str(e)}"
    
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
    
    async def _handle_create_strategy(self, message: str, user_id: str) -> str:
        """Handle create investment strategy intent - AI automatically creates optimal strategy"""
        try:
            from src.models.investment_strategy import StrategyCreateRequest, StrategyType, TriggerType
            
            # AI analyzes user message to determine optimal strategy
            strategy_config = await self._analyze_and_create_optimal_strategy(message, user_id)
            
            # Create the strategy automatically
            strategy = await investment_strategy_service.create_strategy(user_id, strategy_config)
            
            # Auto-approve the strategy for immediate activation
            await investment_strategy_service.approve_strategy(strategy.id)
            
            return f"🤖 **AI Investment Strategy Created & Activated!**\n\n" \
                   f"🎯 **Strategy:** {strategy.name}\n" \
                   f"💰 **Amount:** ₹{strategy.amount:,.2f}\n" \
                   f"🔄 **Trigger:** {strategy.trigger_type}\n" \
                   f"🪙 **Tokens:** {', '.join(strategy.crypto_tokens)}\n" \
                   f"📊 **Allocation:** {strategy.allocation}\n" \
                   f"⚠️ **Risk Level:** {strategy.risk_level}\n\n" \
                   f"✅ **Status:** Strategy is now active and monitoring for triggers!\n\n" \
                   f"💡 **What happens next:**\n" \
                   f"• AI will automatically check for investment opportunities\n" \
                   f"• When triggered, you'll receive a UPI payment request\n" \
                   f"• After payment, AI will automatically invest in crypto\n\n" \
                   f"🔍 **Monitor your strategy:**\n" \
                   f"• 'Check triggers' - See if strategy should execute\n" \
                   f"• 'Show my strategies' - View all your strategies\n" \
                   f"• 'Check investment invoices' - View pending payments"
            
        except Exception as e:
            return f"❌ Strategy creation failed: {str(e)}"
    
    async def _analyze_and_create_optimal_strategy(self, message: str, user_id: str) -> StrategyCreateRequest:
        """AI analyzes user message and creates optimal investment strategy"""
        
        # Extract amount from message
        amount_match = re.search(r'(\d+(?:\.\d+)?)', message)
        amount = float(amount_match.group(1)) if amount_match else 5000.0
        
        # Analyze user preferences from message
        message_lower = message.lower()
        
        # Determine strategy type based on user's message
        if any(word in message_lower for word in ['salary', 'monthly', 'regular']):
            strategy_type = StrategyType.SALARY_PERCENTAGE
            trigger_type = TriggerType.SALARY_RECEIVED
            name = "AI Salary Investment Strategy"
            description = "Automated investment strategy that invests a percentage of your salary"
        elif any(word in message_lower for word in ['dip', 'market', 'buy low']):
            strategy_type = StrategyType.MARKET_DIP
            trigger_type = TriggerType.MARKET_DIP
            name = "AI Market Dip Strategy"
            description = "Smart strategy that buys crypto during market dips"
        elif any(word in message_lower for word in ['trending', 'hot', 'popular']):
            strategy_type = StrategyType.TRENDING
            trigger_type = TriggerType.TRENDING_ALERT
            name = "AI Trending Tokens Strategy"
            description = "Invests in trending and popular cryptocurrencies"
        elif any(word in message_lower for word in ['weekly', 'every week']):
            strategy_type = StrategyType.DCA
            trigger_type = TriggerType.WEEKLY
            name = "AI Weekly DCA Strategy"
            description = "Dollar Cost Averaging strategy for weekly investments"
        elif any(word in message_lower for word in ['monthly', 'every month']):
            strategy_type = StrategyType.DCA
            trigger_type = TriggerType.MONTHLY
            name = "AI Monthly DCA Strategy"
            description = "Dollar Cost Averaging strategy for monthly investments"
        else:
            # Default to DCA with weekly trigger
            strategy_type = StrategyType.DCA
            trigger_type = TriggerType.WEEKLY
            name = "AI Automated DCA Strategy"
            description = "Automated Dollar Cost Averaging strategy for regular crypto investments"
        
        # Determine risk level based on amount and keywords
        if amount > 10000 or any(word in message_lower for word in ['aggressive', 'high risk']):
            risk_level = "high"
            crypto_tokens = ["BTC", "ETH", "SOL", "MATIC", "DOGE"]
            allocation = {"BTC": 30, "ETH": 30, "SOL": 20, "MATIC": 15, "DOGE": 5}
        elif amount < 2000 or any(word in message_lower for word in ['safe', 'conservative', 'low risk']):
            risk_level = "low"
            crypto_tokens = ["BTC", "ETH", "USDT"]
            allocation = {"BTC": 50, "ETH": 30, "USDT": 20}
        else:
            risk_level = "medium"
            crypto_tokens = ["BTC", "ETH", "MATIC", "USDT"]
            allocation = {"BTC": 40, "ETH": 35, "MATIC": 15, "USDT": 10}
        
        # Calculate percentage if salary-related
        percentage = None
        if strategy_type == StrategyType.SALARY_PERCENTAGE:
            if amount > 50000:
                percentage = 10  # 10% of salary
            elif amount > 20000:
                percentage = 15  # 15% of salary
            else:
                percentage = 20  # 20% of salary
        
        # Set investment limits
        max_investment = amount * 2
        min_investment = amount * 0.5
        
        return StrategyCreateRequest(
            name=name,
            description=description,
            strategy_type=strategy_type,
            trigger_type=trigger_type,
            amount=amount,
            percentage=percentage,
            crypto_tokens=crypto_tokens,
            allocation=allocation,
            risk_level=risk_level,
            max_investment=max_investment,
            min_investment=min_investment
        )
    
    async def _handle_check_strategies(self, user_id: str) -> str:
        """Handle check strategies intent"""
        try:
            strategies = await investment_strategy_service.get_user_strategies(user_id)
            
            if not strategies:
                return "📋 **No Investment Strategies Found**\n\n" \
                       "You don't have any investment strategies set up yet.\n" \
                       "Try saying: 'Create an investment strategy' to get started!"
            
            response = f"📋 **Your Investment Strategies ({len(strategies)})**\n\n"
            
            for i, strategy in enumerate(strategies, 1):
                status = "✅ Active" if strategy.is_active and strategy.is_approved else "⏸️ Pending Approval"
                response += f"{i}. **{strategy.name}** - {status}\n"
                response += f"   💰 Amount: ₹{strategy.amount:,.2f}\n"
                response += f"   🔄 Trigger: {strategy.trigger_type}\n"
                response += f"   🪙 Tokens: {', '.join(strategy.crypto_tokens)}\n"
                response += f"   📊 Allocation: {strategy.allocation}\n\n"
            
            response += "💡 **Commands:**\n" \
                       "• 'Check triggers' - See if any strategies should execute\n" \
                       "• 'Approve strategy [ID]' - Approve a pending strategy\n" \
                       "• 'Create strategy' - Create a new strategy"
            
            return response
            
        except Exception as e:
            return f"❌ Failed to get strategies: {str(e)}"
    
    async def _handle_check_triggers(self, user_id: str) -> str:
        """Handle check triggers intent - AI automatically generates invoices"""
        try:
            triggered_strategies = await investment_strategy_service.check_triggers(user_id)
            
            if not triggered_strategies:
                return "🔍 **No Investment Triggers Found**\n\n" \
                       "None of your investment strategies are ready to execute at this time.\n" \
                       "The AI will automatically check for triggers and notify you when it's time to invest!"
            
            # AI automatically generates invoices for triggered strategies
            invoices = []
            for strategy in triggered_strategies:
                reason = f"Strategy '{strategy.name}' triggered by {strategy.trigger_type}"
                invoice = await investment_strategy_service.generate_investment_invoice(strategy, reason)
                invoices.append(invoice)
            
            response = f"🚀 **Investment Triggers Found & Invoices Generated! ({len(triggered_strategies)})**\n\n"
            
            for i, (strategy, invoice) in enumerate(zip(triggered_strategies, invoices), 1):
                response += f"{i}. **{strategy.name}**\n"
                response += f"   💰 Amount: ₹{strategy.amount:,.2f}\n"
                response += f"   🔄 Trigger: {strategy.trigger_type}\n"
                response += f"   🪙 Tokens: {', '.join(strategy.crypto_tokens)}\n"
                response += f"   📄 Invoice: {invoice.id}\n\n"
            
            response += "💳 **Payment Required:**\n" \
                       "AI has generated UPI payment invoices for these investments.\n" \
                       "Please pay via UPI to execute the investments.\n\n" \
                       "🔍 **Check your invoices:**\n" \
                       "• 'Show my investment invoices' - View all pending payments\n" \
                       "• 'Check invoice status' - Check payment status\n" \
                       "• 'Execute investment [invoice_id]' - Execute after payment"
            
            return response
            
        except Exception as e:
            return f"❌ Failed to check triggers: {str(e)}"
    
    async def _handle_check_invoices(self, user_id: str) -> str:
        """Handle check investment invoices intent"""
        try:
            invoices = await investment_strategy_service.get_user_invoices(user_id)
            
            if not invoices:
                return "📄 **No Investment Invoices Found**\n\n" \
                       "You don't have any pending investment invoices.\n" \
                       "Invoices are generated when your investment strategies are triggered."
            
            # Filter by status
            pending_invoices = [i for i in invoices if i.status == "pending"]
            paid_invoices = [i for i in invoices if i.status == "paid"]
            executed_invoices = [i for i in invoices if i.status == "executed"]
            
            response = f"📄 **Investment Invoices ({len(invoices)})**\n\n"
            
            if pending_invoices:
                response += f"⏳ **Pending Payments ({len(pending_invoices)})**\n"
                for i, invoice in enumerate(pending_invoices[:3], 1):  # Show first 3
                    response += f"{i}. **Invoice {invoice.id[:8]}...**\n"
                    response += f"   💰 Amount: ₹{invoice.amount:,.2f}\n"
                    response += f"   🪙 Tokens: {', '.join(invoice.crypto_tokens)}\n"
                    response += f"   📅 Expires: {invoice.expires_at.strftime('%Y-%m-%d %H:%M')}\n"
                    response += f"   💳 UPI: {invoice.upi_string}\n\n"
                
                if len(pending_invoices) > 3:
                    response += f"   ... and {len(pending_invoices) - 3} more pending invoices\n\n"
            
            if paid_invoices:
                response += f"✅ **Paid & Ready to Execute ({len(paid_invoices)})**\n"
                for i, invoice in enumerate(paid_invoices[:2], 1):
                    response += f"{i}. **Invoice {invoice.id[:8]}...**\n"
                    response += f"   💰 Amount: ₹{invoice.amount:,.2f}\n"
                    response += f"   🪙 Tokens: {', '.join(invoice.crypto_tokens)}\n"
                    response += f"   ⏰ Paid: {invoice.paid_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            if executed_invoices:
                response += f"🎯 **Executed Investments ({len(executed_invoices)})**\n"
                for i, invoice in enumerate(executed_invoices[:2], 1):
                    response += f"{i}. **Invoice {invoice.id[:8]}...**\n"
                    response += f"   💰 Amount: ₹{invoice.amount:,.2f}\n"
                    response += f"   🪙 Tokens: {', '.join(invoice.crypto_tokens)}\n"
                    response += f"   ⏰ Executed: {invoice.executed_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            response += "💡 **Actions:**\n" \
                       "• Pay pending invoices via UPI\n" \
                       "• 'Execute investment [invoice_id]' - Execute paid invoices\n" \
                       "• 'Check triggers' - Check for new investment opportunities"
            
            return response
            
        except Exception as e:
            return f"❌ Failed to get invoices: {str(e)}"
    
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
        
        help_message += "🤖 **AI Investment Strategies:**\n"
        help_message += "- \"Create an investment strategy\" - Set up automated AI-driven investments\n"
        help_message += "- \"Show my strategies\" - View your investment strategies\n"
        help_message += "- \"Check triggers\" - See if any strategies should execute\n"
        help_message += "- \"Check investment invoices\" - View pending investment payments\n\n"
        
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