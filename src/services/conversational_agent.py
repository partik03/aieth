"""
Conversational AI agent for more natural interactions with UPI transaction data
"""

import json
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from src.services.finance_agent import finance_agent_service
from src.services.upi_data_service import upi_data_service
from src.services.mock_upi_data import mock_upi_data_service
from src.config.settings import get_settings

class ConversationalAgent:
    """
    A more conversational AI agent that can handle natural language queries
    about UPI transaction data and provide insights and recommendations
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.user_context = {}  # Store conversation context for each user
        
    async def process_message(self, message: str, user_id: str) -> str:
        """
        Process a natural language message and return a conversational response
        with insights and recommendations based on the user's UPI data
        """
        try:
            # Initialize user context if not exists
            if user_id not in self.user_context:
                self.user_context[user_id] = {
                    "last_query_type": None,
                    "last_transactions": None,
                    "upi_id": None,
                    "conversation_history": []
                }
            
            # Add message to conversation history
            self.user_context[user_id]["conversation_history"].append({
                "role": "user",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Lowercase message for easier processing
            message_lower = message.lower().strip()
            
            # Check for UPI ID registration
            upi_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)', message_lower)
            if upi_match and any(keyword in message_lower for keyword in ["upi", "register", "connect"]):
                return await self._handle_upi_registration(upi_match.group(1), user_id)
            
            # Check for transaction analysis request
            if any(keyword in message_lower for keyword in ["analyze", "analysis", "transactions", "spending"]):
                return await self._handle_transaction_analysis(user_id)
            
            # Check for financial insights request
            if any(keyword in message_lower for keyword in ["insight", "advice", "recommend", "suggestion"]):
                return await self._handle_financial_insights(user_id)
            
            # Check for transaction summary request
            if any(keyword in message_lower for keyword in ["summary", "overview", "report"]):
                return await self._handle_transaction_summary(user_id)
                
            # Check for category-specific queries
            category_match = self._extract_category(message_lower)
            if category_match:
                return await self._handle_category_analysis(user_id, category_match)
                
            # Check for time period queries
            time_period = self._extract_time_period(message_lower)
            if time_period:
                return await self._handle_time_period_analysis(user_id, time_period)
                
            # Check for comparison queries
            if any(keyword in message_lower for keyword in ["compare", "comparison", "versus", "vs"]):
                return await self._handle_comparison_analysis(user_id, message_lower)
                
            # Handle general conversation
            return await self._handle_general_conversation(message, user_id)
            
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Could you try rephrasing or ask something else?"
    
    async def _handle_upi_registration(self, upi_id: str, user_id: str) -> str:
        """Handle UPI ID registration"""
        result = await upi_data_service.collect_upi_data(user_id, upi_id)
        
        if result.get("success"):
            self.user_context[user_id]["upi_id"] = upi_id
            return f"Great! I've connected your UPI ID: {upi_id}. Now I can provide personalized insights based on your transaction data. Would you like me to analyze your recent transactions?"
        else:
            return f"I couldn't register your UPI ID. Please make sure it's in the correct format (username@provider). Error: {result.get('error', 'Unknown error')}"
    
    async def _handle_transaction_analysis(self, user_id: str) -> str:
        """Handle transaction analysis request"""
        # Get transactions
        transactions = await self._get_user_transactions(user_id)
        if not transactions:
            return "I don't see any transaction data to analyze. Would you like me to generate some mock data for demonstration purposes?"
        
        # Store transactions in context
        self.user_context[user_id]["last_transactions"] = transactions
        self.user_context[user_id]["last_query_type"] = "analysis"
        
        # Analyze transactions
        analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
        
        if not analysis_result.get("success"):
            return f"I had trouble analyzing your transactions. {analysis_result.get('error', 'Please try again later.')}"
        
        analysis = analysis_result.get("analysis", {})
        structured_analysis = analysis.get("structured_analysis", {})
        
        # Create a conversational response
        response = "I've analyzed your transactions and here's what I found:\n\n"
        
        # Add spending analysis
        if structured_analysis.get("spending_analysis"):
            response += structured_analysis["spending_analysis"] + "\n\n"
        
        # Add financial health
        if structured_analysis.get("financial_health"):
            response += structured_analysis["financial_health"] + "\n\n"
        
        # Add next steps
        if structured_analysis.get("next_steps"):
            response += "Here are some recommended next steps:\n" + structured_analysis["next_steps"] + "\n\n"
        
        response += "Would you like more specific insights about a particular category or time period?"
        
        return response
    
    async def _handle_financial_insights(self, user_id: str) -> str:
        """Handle financial insights request"""
        # Get transactions
        transactions = await self._get_user_transactions(user_id)
        if not transactions:
            return "I don't have any transaction data to provide insights. Would you like me to generate some mock data for demonstration purposes?"
        
        # Store in context
        self.user_context[user_id]["last_transactions"] = transactions
        self.user_context[user_id]["last_query_type"] = "insights"
        
        # Get transaction analysis
        analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
        
        if not analysis_result.get("success"):
            return f"I had trouble generating insights from your transactions. {analysis_result.get('error', 'Please try again later.')}"
        
        # Get recommendations
        recommendations_result = await finance_agent_service.get_financial_recommendations(
            user_id, analysis_result.get("analysis", {})
        )
        
        if not recommendations_result.get("success"):
            return f"I analyzed your transactions but couldn't generate specific recommendations. {recommendations_result.get('error', 'Please try again later.')}"
        
        # Create conversational response
        recommendations = recommendations_result.get("recommendations", "")
        
        response = "Based on your transaction history, here are my financial insights and recommendations:\n\n"
        response += recommendations
        
        response += "\n\nIs there a specific area you'd like more detailed advice on?"
        
        return response
    
    async def _handle_transaction_summary(self, user_id: str) -> str:
        """Handle transaction summary request"""
        # Get transactions
        transactions = await self._get_user_transactions(user_id)
        if not transactions:
            return "I don't have any transaction data to summarize. Would you like me to generate some mock data for demonstration purposes?"
        
        # Store in context
        self.user_context[user_id]["last_transactions"] = transactions
        self.user_context[user_id]["last_query_type"] = "summary"
        
        # Get summary
        summary = upi_data_service.get_transaction_summary(transactions)
        
        # Create conversational response
        response = "Here's a summary of your recent transactions:\n\n"
        
        response += f"You've made {summary.get('total_transactions', 0)} transactions "
        response += f"totaling ₹{summary.get('total_amount', 0):,.2f}. "
        
        if summary.get('debit_transactions', 0) > 0:
            response += f"You spent ₹{summary.get('debit_amount', 0):,.2f} "
            response += f"across {summary.get('debit_transactions', 0)} payments. "
        
        if summary.get('credit_transactions', 0) > 0:
            response += f"You received ₹{summary.get('credit_amount', 0):,.2f} "
            response += f"across {summary.get('credit_transactions', 0)} incoming transactions. "
        
        response += f"Your net cash flow is ₹{summary.get('net_amount', 0):,.2f}.\n\n"
        
        # Add top categories
        top_categories = summary.get('top_categories', [])
        if top_categories:
            response += "Your top spending categories are:\n"
            for category, amount in top_categories[:3]:
                percentage = (amount / summary.get('total_amount', 1)) * 100
                response += f"- {category}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
        
        response += "\nWould you like to see a detailed analysis of your spending patterns?"
        
        return response
    
    async def _handle_category_analysis(self, user_id: str, category: str) -> str:
        """Handle category-specific analysis"""
        # Get transactions
        transactions = await self._get_user_transactions(user_id)
        if not transactions:
            return f"I don't have any transaction data to analyze for {category}. Would you like me to generate some mock data for demonstration purposes?"
        
        # Filter by category
        category_transactions = upi_data_service.get_transactions_by_category(transactions, category)
        
        if not category_transactions:
            return f"I couldn't find any transactions in the '{category}' category. The available categories are: {', '.join(set(t.get('category', 'Other') for t in transactions))}."
        
        # Get summary for this category
        summary = upi_data_service.get_transaction_summary(category_transactions)
        
        # Create conversational response
        response = f"Here's an analysis of your '{category}' transactions:\n\n"
        
        response += f"You've made {summary.get('total_transactions', 0)} transactions "
        response += f"in this category, totaling ₹{summary.get('total_amount', 0):,.2f}. "
        response += f"The average transaction was ₹{summary.get('average_transaction', 0):,.2f}.\n\n"
        
        # Add merchants
        merchants = {}
        for transaction in category_transactions:
            merchant = transaction.get('merchant', 'Unknown')
            amount = transaction.get('amount', 0)
            if merchant not in merchants:
                merchants[merchant] = 0
            merchants[merchant] += amount
        
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if top_merchants:
            response += f"Your top merchants in {category} are:\n"
            for merchant, amount in top_merchants:
                percentage = (amount / summary.get('total_amount', 1)) * 100
                response += f"- {merchant}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
        
        response += "\nWould you like to see how this category compares to your overall spending?"
        
        return response
    
    async def _handle_time_period_analysis(self, user_id: str, days: int) -> str:
        """Handle time period specific analysis"""
        # Get transactions for the specific time period
        transactions = await upi_data_service.get_transactions(user_id, days=days)
        if not transactions:
            return f"I don't have any transaction data for the last {days} days. Would you like me to generate some mock data for demonstration purposes?"
        
        # Store in context
        self.user_context[user_id]["last_transactions"] = transactions
        self.user_context[user_id]["last_query_type"] = "time_period"
        
        # Get summary
        summary = upi_data_service.get_transaction_summary(transactions)
        
        # Create conversational response
        response = f"Here's an analysis of your transactions for the last {days} days:\n\n"
        
        response += f"You've made {summary.get('total_transactions', 0)} transactions "
        response += f"totaling ₹{summary.get('total_amount', 0):,.2f}. "
        
        if summary.get('debit_transactions', 0) > 0:
            response += f"You spent ₹{summary.get('debit_amount', 0):,.2f} "
            response += f"across {summary.get('debit_transactions', 0)} payments. "
        
        if summary.get('credit_transactions', 0) > 0:
            response += f"You received ₹{summary.get('credit_amount', 0):,.2f} "
            response += f"across {summary.get('credit_transactions', 0)} incoming transactions. "
        
        response += f"Your net cash flow is ₹{summary.get('net_amount', 0):,.2f}.\n\n"
        
        # Add top categories
        top_categories = summary.get('top_categories', [])
        if top_categories:
            response += "Your top spending categories are:\n"
            for category, amount in top_categories[:3]:
                percentage = (amount / summary.get('total_amount', 1)) * 100
                response += f"- {category}: ₹{amount:,.2f} ({percentage:.1f}%)\n"
        
        response += "\nWould you like to compare this to a different time period or see more detailed insights?"
        
        return response
    
    async def _handle_comparison_analysis(self, user_id: str, message: str) -> str:
        """Handle comparison analysis between categories, time periods, etc."""
        # This is a simplified implementation - in a real system, this would be more sophisticated
        response = "I understand you want to compare different aspects of your financial data. "
        response += "Here's what I can compare for you:\n\n"
        
        response += "1. Different time periods (e.g., this month vs. last month)\n"
        response += "2. Different spending categories\n"
        response += "3. Different merchants\n\n"
        
        response += "Please let me know which comparison you're interested in, and I'll provide a detailed analysis."
        
        return response
    
    async def _handle_general_conversation(self, message: str, user_id: str) -> str:
        """Handle general conversation that doesn't fit specific intents"""
        # Check if this is a greeting
        greeting_patterns = ["hello", "hi", "hey", "greetings", "howdy"]
        if any(pattern in message.lower() for pattern in greeting_patterns):
            return self._get_greeting(user_id)
        
        # Check if asking about capabilities
        capability_patterns = ["what can you do", "how can you help", "what are you capable of"]
        if any(pattern in message.lower() for pattern in capability_patterns):
            return self._get_capabilities()
        
        # Default response with suggestions
        return ("I'm your financial assistant focused on analyzing your UPI transactions. "
                "You can ask me to:\n\n"
                "- Register your UPI ID\n"
                "- Analyze your transactions\n"
                "- Provide financial insights and recommendations\n"
                "- Show a summary of your spending\n"
                "- Analyze specific spending categories\n"
                "- Compare different time periods\n\n"
                "What would you like to know about your finances?")
    
    def _get_greeting(self, user_id: str) -> str:
        """Return a personalized greeting"""
        upi_id = self.user_context.get(user_id, {}).get("upi_id")
        
        if upi_id:
            return f"Hello! I'm your financial assistant. I'm currently connected to your UPI ID ({upi_id}). How can I help you with your finances today?"
        else:
            return ("Hello! I'm your financial assistant. To get personalized insights, "
                   "you can register your UPI ID by saying something like 'My UPI ID is username@provider'. "
                   "What would you like to do today?")
    
    def _get_capabilities(self) -> str:
        """Return information about the agent's capabilities"""
        return ("I'm your AI-powered financial assistant. Here's what I can do for you:\n\n"
                "📊 **Transaction Analysis**\n"
                "- Analyze your spending patterns\n"
                "- Identify trends and anomalies\n"
                "- Categorize your transactions\n\n"
                
                "💡 **Financial Insights**\n"
                "- Provide personalized recommendations\n"
                "- Suggest savings opportunities\n"
                "- Offer budgeting advice\n\n"
                
                "📈 **Financial Reports**\n"
                "- Generate transaction summaries\n"
                "- Create category-specific reports\n"
                "- Compare different time periods\n\n"
                
                "To get started, you can register your UPI ID or ask me to analyze your transactions.")
    
    async def _get_user_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user transactions, either real or mock"""
        # Try to get real transactions first
        transactions = await upi_data_service.get_transactions(user_id)
        
        # If no transactions, generate mock data
        if not transactions:
            transactions = mock_upi_data_service.generate_mock_transactions(user_id)
        
        return transactions
    
    def _extract_category(self, message: str) -> Optional[str]:
        """Extract category from message"""
        # Common spending categories
        categories = [
            "Food & Dining", "Shopping", "Transportation", "Entertainment",
            "Utilities", "Healthcare", "Education", "Finance", "Travel", "Other"
        ]
        
        # Lowercase categories for matching
        categories_lower = [category.lower() for category in categories]
        
        # Check for category mentions
        for i, category_lower in enumerate(categories_lower):
            if category_lower in message:
                return categories[i]
            
        # Check for specific keywords
        if any(word in message for word in ["food", "restaurant", "dining", "eat"]):
            return "Food & Dining"
        elif any(word in message for word in ["shop", "buy", "purchase"]):
            return "Shopping"
        elif any(word in message for word in ["transport", "travel", "uber", "ola", "taxi"]):
            return "Transportation"
        elif any(word in message for word in ["movie", "entertainment", "netflix"]):
            return "Entertainment"
        
        return None
    
    def _extract_time_period(self, message: str) -> Optional[int]:
        """Extract time period from message (in days)"""
        # Check for specific time periods
        if "last week" in message or "past week" in message:
            return 7
        elif "last month" in message or "past month" in message:
            return 30
        elif "last 3 months" in message or "past 3 months" in message:
            return 90
        elif "last 6 months" in message or "past 6 months" in message:
            return 180
        elif "last year" in message or "past year" in message:
            return 365
        
        # Check for specific day mentions
        day_match = re.search(r'last (\d+) days', message)
        if day_match:
            return int(day_match.group(1))
        
        return None

# Create singleton instance
conversational_agent = ConversationalAgent() 