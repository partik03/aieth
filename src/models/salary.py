"""
Salary and investment strategy models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SalaryBase(BaseModel):
    """Base salary model"""
    user_id: str = Field(..., description="User ID who received salary")
    amount: float = Field(..., gt=0, description="Salary amount in INR")
    employer: str = Field(..., description="Employer name")
    date: str = Field(..., description="Salary date")


class SalaryCreate(SalaryBase):
    """Model for creating a new salary record"""
    pass


class Salary(SalaryBase):
    """Complete salary model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True
    }


class InvestmentStrategyBase(BaseModel):
    """Base investment strategy model"""
    user_id: str = Field(..., description="User ID for the strategy")
    salary_id: str = Field(..., description="Associated salary record ID")
    strategy: Dict[str, float] = Field(..., description="Token allocation percentages")
    reasoning: str = Field(..., description="Strategy reasoning")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    expected_return: str = Field(..., description="Expected return (conservative/moderate/aggressive)")
    trending_tokens: list = Field(..., description="Trending tokens used for strategy")


class InvestmentStrategyCreate(InvestmentStrategyBase):
    """Model for creating a new investment strategy"""
    pass


class InvestmentStrategy(InvestmentStrategyBase):
    """Complete investment strategy model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    is_mock: bool = Field(default=False, description="Whether this is a mock strategy")
    
    model_config = {
        "populate_by_name": True
    }


class SalaryRequest(BaseModel):
    """Request model for salary endpoint"""
    user_id: str = Field(..., description="User ID who received salary")
    amount: float = Field(..., gt=0, description="Salary amount in INR")
    employer: str = Field(..., description="Employer name")
    date: str = Field(..., description="Salary date")


class SalaryResponse(BaseModel):
    """Response model for salary endpoint"""
    success: bool
    salary_id: Optional[str] = None
    strategy_id: Optional[str] = None
    message: str
    strategy: Optional[Dict[str, Any]] = None 