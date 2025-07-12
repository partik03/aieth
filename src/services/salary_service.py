"""
Salary service for processing salary data and generating investment strategies
"""

from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from src.models.salary import Salary, SalaryCreate, InvestmentStrategy, InvestmentStrategyCreate
from src.services.db import get_collection
from src.services.ai_agent import ai_agent_service
from src.services.twitter_service import twitter_service


class SalaryService:
    """Service for salary processing and investment strategy generation"""
    
    def __init__(self):
        self.salary_collection = "salaries"
        self.strategy_collection = "investment_strategies"
    
    async def create_salary_record(self, salary_data: Dict[str, Any]) -> Optional[str]:
        """Create a new salary record"""
        try:
            collection = await get_collection(self.salary_collection)
            
            # Create salary document
            salary_doc = SalaryCreate(**salary_data).dict()
            salary_doc["created_at"] = datetime.utcnow()
            
            # Insert into database
            result = await collection.insert_one(salary_doc)
            
            if result.inserted_id:
                return str(result.inserted_id)
            return None
            
        except Exception as e:
            print(f"Error creating salary record: {e}")
            return None
    
    async def create_investment_strategy(
        self, 
        user_id: str, 
        salary_id: str, 
        strategy_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create a new investment strategy record"""
        try:
            collection = await get_collection(self.strategy_collection)
            
            # Create strategy document
            strategy_doc = {
                "user_id": user_id,
                "salary_id": salary_id,
                "strategy": strategy_data.get("strategy", {}),
                "reasoning": strategy_data.get("reasoning", ""),
                "risk_level": strategy_data.get("risk_level", "medium"),
                "expected_return": strategy_data.get("expected_return", "moderate"),
                "trending_tokens": strategy_data.get("trending_tokens", []),
                "generated_at": datetime.utcnow(),
                "is_mock": strategy_data.get("is_mock", False)
            }
            
            # Insert into database
            result = await collection.insert_one(strategy_doc)
            
            if result.inserted_id:
                return str(result.inserted_id)
            return None
            
        except Exception as e:
            print(f"Error creating investment strategy: {e}")
            return None
    
    async def process_salary_and_generate_strategy(self, salary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process salary data and generate investment strategy"""
        try:
            # Step 1: Save salary record
            salary_id = await self.create_salary_record(salary_data)
            if not salary_id:
                return {
                    "success": False,
                    "message": "Failed to create salary record"
                }
            
            # Step 2: Get trending tokens
            trending_tokens = await twitter_service.get_trending_tokens()
            
            # Step 3: Generate investment strategy
            strategy_result = await ai_agent_service.generate_investment_strategy(
                salary_data, 
                trending_tokens
            )
            
            if not strategy_result.get("success"):
                return {
                    "success": False,
                    "message": "Failed to generate investment strategy",
                    "salary_id": salary_id
                }
            
            # Step 4: Save investment strategy
            strategy_id = await self.create_investment_strategy(
                salary_data["user_id"],
                salary_id,
                strategy_result
            )
            
            if not strategy_id:
                return {
                    "success": False,
                    "message": "Failed to save investment strategy",
                    "salary_id": salary_id
                }
            
            return {
                "success": True,
                "salary_id": salary_id,
                "strategy_id": strategy_id,
                "message": "Salary processed and investment strategy generated successfully",
                "strategy": strategy_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing salary: {str(e)}"
            }
    
    async def get_salary_by_id(self, salary_id: str) -> Optional[Salary]:
        """Get salary record by ID"""
        try:
            collection = await get_collection(self.salary_collection)
            salary_doc = await collection.find_one({"_id": ObjectId(salary_id)})
            
            if salary_doc:
                return Salary(**salary_doc)
            return None
            
        except Exception as e:
            print(f"Error getting salary: {e}")
            return None
    
    async def get_strategy_by_id(self, strategy_id: str) -> Optional[InvestmentStrategy]:
        """Get investment strategy by ID"""
        try:
            collection = await get_collection(self.strategy_collection)
            strategy_doc = await collection.find_one({"_id": ObjectId(strategy_id)})
            
            if strategy_doc:
                return InvestmentStrategy(**strategy_doc)
            return None
            
        except Exception as e:
            print(f"Error getting strategy: {e}")
            return None
    
    async def get_user_salaries(self, user_id: str, limit: int = 10) -> list:
        """Get recent salaries for a user"""
        try:
            collection = await get_collection(self.salary_collection)
            cursor = collection.find(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            ).limit(limit)
            
            salaries = []
            async for doc in cursor:
                salaries.append(Salary(**doc))
            
            return salaries
            
        except Exception as e:
            print(f"Error getting user salaries: {e}")
            return []
    
    async def get_user_strategies(self, user_id: str, limit: int = 10) -> list:
        """Get recent investment strategies for a user"""
        try:
            collection = await get_collection(self.strategy_collection)
            cursor = collection.find(
                {"user_id": user_id},
                sort=[("generated_at", -1)]
            ).limit(limit)
            
            strategies = []
            async for doc in cursor:
                strategies.append(InvestmentStrategy(**doc))
            
            return strategies
            
        except Exception as e:
            print(f"Error getting user strategies: {e}")
            return []


# Global salary service instance
salary_service = SalaryService() 