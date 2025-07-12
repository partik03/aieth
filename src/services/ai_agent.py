"""
AI Agent service for crypto investment strategy generation
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from openai import AsyncOpenAI

from src.config.settings import get_settings


class AIAgentService:
    """AI Agent for crypto investment strategy generation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.ai_model
        self.max_tokens = self.settings.ai_max_tokens
        self.temperature = self.settings.ai_temperature
    
    def _create_investment_prompt(self, salary_info: Dict[str, Any], trending_tokens: List[str]) -> str:
        """Create the investment strategy prompt"""
        prompt = f"""
You are a crypto investment advisor. Given the following information, suggest how to allocate the salary into 3-5 crypto tokens.

SALARY INFORMATION:
- Amount: ₹{salary_info.get('amount', 0)}
- Employer: {salary_info.get('employer', 'Unknown')}
- Date: {salary_info.get('date', 'Unknown')}

TRENDING TOKENS: {', '.join(trending_tokens)}

INSTRUCTIONS:
1. Analyze the salary amount and trending tokens
2. Consider risk tolerance based on salary amount
3. Suggest allocation percentages for 3-5 tokens
4. Ensure total allocation equals 100%
5. Focus on trending tokens but consider established ones like BTC/ETH for stability

RESPONSE FORMAT:
Return ONLY a valid JSON object with this structure:
{{
    "strategy": {{
        "BTC": 30,
        "ETH": 25,
        "MATIC": 20,
        "SOL": 15,
        "DOGE": 10
    }},
    "reasoning": "Brief explanation of the allocation strategy",
    "risk_level": "low|medium|high",
    "expected_return": "conservative|moderate|aggressive"
}}

IMPORTANT: Return ONLY the JSON object, no additional text.
"""
        return prompt.strip()
    
    async def generate_investment_strategy(
        self, 
        salary_info: Dict[str, Any], 
        trending_tokens: List[str]
    ) -> Dict[str, Any]:
        """Generate investment strategy using AI"""
        try:
            # Create the prompt
            prompt = self._create_investment_prompt(salary_info, trending_tokens)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional crypto investment advisor. Provide clear, actionable investment strategies."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                strategy_data = json.loads(content.strip())
                
                # Validate the response structure
                if "strategy" not in strategy_data:
                    raise ValueError("Invalid response structure: missing 'strategy'")
                
                # Ensure strategy percentages sum to 100
                total_percentage = sum(strategy_data["strategy"].values())
                if abs(total_percentage - 100) > 1:  # Allow 1% tolerance
                    # Normalize percentages
                    for token in strategy_data["strategy"]:
                        strategy_data["strategy"][token] = round(
                            (strategy_data["strategy"][token] / total_percentage) * 100, 2
                        )
                
                return {
                    "success": True,
                    "strategy": strategy_data["strategy"],
                    "reasoning": strategy_data.get("reasoning", ""),
                    "risk_level": strategy_data.get("risk_level", "medium"),
                    "expected_return": strategy_data.get("expected_return", "moderate"),
                    "trending_tokens": trending_tokens,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
            except json.JSONDecodeError as e:
                # Fallback to mock strategy if JSON parsing fails
                print(f"JSON parsing failed: {e}")
                return self._generate_mock_strategy(salary_info, trending_tokens)
                
        except Exception as e:
            print(f"AI strategy generation failed: {e}")
            # Return mock strategy as fallback
            return self._generate_mock_strategy(salary_info, trending_tokens)
    
    def _generate_mock_strategy(self, salary_info: Dict[str, Any], trending_tokens: List[str]) -> Dict[str, Any]:
        """Generate a mock investment strategy as fallback"""
        amount = salary_info.get('amount', 0)
        
        # Simple mock logic based on salary amount
        if amount > 50000:
            # High salary - more aggressive
            strategy = {
                "BTC": 25,
                "ETH": 20,
                "MATIC": 25,
                "SOL": 20,
                "DOGE": 10
            }
            risk_level = "medium"
            expected_return = "moderate"
        elif amount > 25000:
            # Medium salary - balanced
            strategy = {
                "BTC": 35,
                "ETH": 25,
                "MATIC": 20,
                "SOL": 15,
                "DOGE": 5
            }
            risk_level = "low"
            expected_return = "conservative"
        else:
            # Low salary - conservative
            strategy = {
                "BTC": 50,
                "ETH": 30,
                "MATIC": 15,
                "SOL": 5
            }
            risk_level = "low"
            expected_return = "conservative"
        
        return {
            "success": True,
            "strategy": strategy,
            "reasoning": f"Mock strategy generated for ₹{amount} salary",
            "risk_level": risk_level,
            "expected_return": expected_return,
            "trending_tokens": trending_tokens,
            "generated_at": datetime.utcnow().isoformat(),
            "is_mock": True
        }
    
    async def analyze_market_sentiment(self, tokens: List[str]) -> Dict[str, str]:
        """Analyze market sentiment for given tokens"""
        try:
            prompt = f"""
Analyze the current market sentiment for these crypto tokens: {', '.join(tokens)}

For each token, provide a sentiment score (bullish, bearish, neutral) and brief reasoning.

Return as JSON:
{{
    "BTC": {{"sentiment": "bullish", "reason": "..."}},
    "ETH": {{"sentiment": "neutral", "reason": "..."}}
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            # Return mock sentiment
            return {token: {"sentiment": "neutral", "reason": "Mock analysis"} for token in tokens}


# Global AI agent service instance
ai_agent_service = AIAgentService() 