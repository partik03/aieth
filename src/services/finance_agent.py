"""
Finance Agent service using Azure OpenAI for UPI transaction analysis
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from src.config.settings import get_settings


class FinanceAgentService:
    """Finance Agent for UPI transaction analysis and financial insights"""
    
    def __init__(self):
        self.settings = get_settings()
        self.endpoint = self.settings.azure_openai_endpoint
        self.api_key = self.settings.azure_openai_api_key
        self.deployment = self.settings.azure_openai_deployment
        
    async def _call_azure_openai(self, messages: List[Dict[str, str]]) -> str:
        """Call Azure OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Azure OpenAI API error: {response.status} - {error_text}")
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response when Azure OpenAI is unavailable"""
        return "I'm currently experiencing technical difficulties. Here's a general financial insight: Consider reviewing your spending patterns and setting up automatic savings transfers to build your emergency fund."
    
    async def analyze_transactions(self, user_id: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze UPI transactions and provide insights"""
        try:
            # Prepare transaction data for analysis
            transaction_summary = self._prepare_transaction_summary(transactions)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(transaction_summary)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a professional financial advisor specializing in UPI transaction analysis. 
                    Provide clear, actionable insights and recommendations based on transaction patterns. 
                    Focus on spending habits, savings opportunities, and financial health indicators."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Get AI analysis
            ai_response = await self._call_azure_openai(messages)
            
            # Parse and structure the response
            analysis = self._parse_ai_response(ai_response, transaction_summary)
            
            return {
                "success": True,
                "analysis": analysis,
                "transaction_summary": transaction_summary,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Transaction analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": self._get_basic_analysis(transactions)
            }
    
    def _prepare_transaction_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare transaction data for analysis"""
        if not transactions:
            return {"error": "No transactions found"}
        
        # Calculate basic statistics
        total_amount = sum(t.get('amount', 0) for t in transactions)
        total_count = len(transactions)
        
        # Categorize transactions
        categories = {}
        merchants = {}
        monthly_totals = {}
        
        for transaction in transactions:
            amount = transaction.get('amount', 0)
            category = transaction.get('category', 'Other')
            merchant = transaction.get('merchant', 'Unknown')
            date = transaction.get('date', datetime.now())
            
            # Category totals
            if category not in categories:
                categories[category] = 0
            categories[category] += amount
            
            # Merchant totals
            if merchant not in merchants:
                merchants[merchant] = 0
            merchants[merchant] += amount
            
            # Monthly totals
            month_key = date.strftime('%Y-%m') if isinstance(date, datetime) else str(date)[:7]
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += amount
        
        # Top categories and merchants
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "average_amount": total_amount / total_count if total_count > 0 else 0,
            "categories": categories,
            "top_categories": top_categories,
            "merchants": merchants,
            "top_merchants": top_merchants,
            "monthly_totals": monthly_totals,
            "date_range": {
                "start": min(t.get('date', datetime.now()) for t in transactions),
                "end": max(t.get('date', datetime.now()) for t in transactions)
            }
        }
    
    def _create_analysis_prompt(self, summary: Dict[str, Any]) -> str:
        """Create prompt for transaction analysis"""
        prompt = f"""
Analyze the following UPI transaction data and provide financial insights:

TRANSACTION SUMMARY:
- Total Amount: ₹{summary.get('total_amount', 0):,.2f}
- Total Transactions: {summary.get('total_count', 0)}
- Average Transaction: ₹{summary.get('average_amount', 0):,.2f}

TOP SPENDING CATEGORIES:
{chr(10).join([f"- {cat}: ₹{amt:,.2f}" for cat, amt in summary.get('top_categories', [])])}

TOP MERCHANTS:
{chr(10).join([f"- {merchant}: ₹{amt:,.2f}" for merchant, amt in summary.get('top_merchants', [])])}

MONTHLY TRENDS:
{chr(10).join([f"- {month}: ₹{amt:,.2f}" for month, amt in summary.get('monthly_totals', {}).items()])}

Please provide:
1. Spending Pattern Analysis
2. Financial Health Assessment
3. Savings Opportunities
4. Budgeting Recommendations
5. Risk Assessment
6. Actionable Next Steps

Format your response as a structured analysis with clear sections and actionable insights.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Try to extract structured sections
            sections = {
                "spending_analysis": "",
                "financial_health": "",
                "savings_opportunities": "",
                "budgeting_recommendations": "",
                "risk_assessment": "",
                "next_steps": ""
            }
            
            # Simple parsing - look for section headers
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if any(keyword in line.lower() for keyword in ['spending', 'pattern', 'analysis']):
                    current_section = "spending_analysis"
                elif any(keyword in line.lower() for keyword in ['health', 'financial']):
                    current_section = "financial_health"
                elif any(keyword in line.lower() for keyword in ['savings', 'opportunity']):
                    current_section = "savings_opportunities"
                elif any(keyword in line.lower() for keyword in ['budget', 'recommendation']):
                    current_section = "budgeting_recommendations"
                elif any(keyword in line.lower() for keyword in ['risk', 'assessment']):
                    current_section = "risk_assessment"
                elif any(keyword in line.lower() for keyword in ['next', 'step', 'action']):
                    current_section = "next_steps"
                elif current_section and line:
                    sections[current_section] += line + " "
            
            return {
                "raw_response": response,
                "structured_analysis": sections,
                "key_metrics": {
                    "total_spent": summary.get('total_amount', 0),
                    "transaction_count": summary.get('total_count', 0),
                    "avg_transaction": summary.get('average_amount', 0),
                    "top_category": summary.get('top_categories', [{}])[0][0] if summary.get('top_categories') else "N/A"
                }
            }
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return {
                "raw_response": response,
                "structured_analysis": {"general_insights": response},
                "key_metrics": summary
            }
    
    def _get_basic_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide basic analysis when AI is unavailable"""
        if not transactions:
            return {"error": "No transactions to analyze"}
        
        total = sum(t.get('amount', 0) for t in transactions)
        avg = total / len(transactions) if transactions else 0
        
        return {
            "raw_response": f"Basic analysis: You've spent ₹{total:,.2f} across {len(transactions)} transactions with an average of ₹{avg:,.2f} per transaction.",
            "structured_analysis": {
                "general_insights": f"Total spending: ₹{total:,.2f}, Average transaction: ₹{avg:,.2f}"
            },
            "key_metrics": {
                "total_spent": total,
                "transaction_count": len(transactions),
                "avg_transaction": avg
            }
        }
    
    async def get_financial_recommendations(self, user_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized financial recommendations"""
        try:
            prompt = f"""
Based on the following financial analysis, provide specific, actionable recommendations:

ANALYSIS SUMMARY:
{json.dumps(analysis.get('key_metrics', {}), indent=2)}

STRUCTURED ANALYSIS:
{json.dumps(analysis.get('structured_analysis', {}), indent=2)}

Provide recommendations in these categories:
1. Immediate Actions (next 7 days)
2. Short-term Goals (next 30 days)
3. Medium-term Planning (next 3 months)
4. Long-term Strategy (next 6-12 months)
5. Investment Opportunities
6. Risk Mitigation

Make recommendations specific, measurable, and achievable.
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a certified financial planner. Provide practical, actionable recommendations based on transaction analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            ai_response = await self._call_azure_openai(messages)
            
            return {
                "success": True,
                "recommendations": ai_response,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": "Consider reviewing your spending patterns and setting up automatic savings."
            }


# Global instance
finance_agent_service = FinanceAgentService() 