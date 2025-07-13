"""
Investment strategy models for AI-driven automated investments
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class StrategyType(str, Enum):
    """Types of investment strategies"""
    DCA = "dollar_cost_averaging"  # Dollar Cost Averaging
    LUMP_SUM = "lump_sum"  # Lump Sum Investment
    SALARY_PERCENTAGE = "salary_percentage"  # Percentage of salary
    MARKET_DIP = "market_dip"  # Buy on market dips
    TRENDING = "trending_tokens"  # Invest in trending tokens


class TriggerType(str, Enum):
    """Types of investment triggers"""
    SALARY_RECEIVED = "salary_received"
    MARKET_DIP = "market_dip"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TRENDING_ALERT = "trending_alert"
    MANUAL = "manual"


class InvestmentStrategy(BaseModel):
    """Investment strategy model"""
    id: Optional[str] = Field(None, alias="_id", description="Strategy ID")
    user_id: str = Field(..., description="User ID who owns this strategy")
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    strategy_type: StrategyType = Field(..., description="Type of investment strategy")
    trigger_type: TriggerType = Field(..., description="What triggers this investment")
    
    # Investment parameters
    amount: float = Field(..., description="Investment amount in INR")
    percentage: Optional[float] = Field(None, description="Percentage of salary/amount")
    crypto_tokens: List[str] = Field(..., description="List of crypto tokens to invest in")
    allocation: Dict[str, float] = Field(..., description="Token allocation percentages")
    
    # Risk parameters
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    max_investment: float = Field(..., description="Maximum investment amount")
    min_investment: float = Field(..., description="Minimum investment amount")
    
    # Status
    is_active: bool = Field(default=True, description="Whether strategy is active")
    is_approved: bool = Field(default=False, description="Whether user has approved this strategy")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = Field(None, description="Last execution time")


class InvestmentInvoice(BaseModel):
    """Investment invoice model"""
    id: Optional[str] = Field(None, alias="_id", description="Invoice ID")
    user_id: str = Field(..., description="User ID")
    strategy_id: str = Field(..., description="Investment strategy ID")
    amount: float = Field(..., description="Investment amount in INR")
    crypto_tokens: List[str] = Field(..., description="Tokens to purchase")
    allocation: Dict[str, float] = Field(..., description="Token allocation")
    reason: str = Field(..., description="Reason for investment")
    
    # UPI payment details
    upi_string: Optional[str] = Field(None, description="UPI payment string")
    qr_code: Optional[str] = Field(None, description="QR code for payment")
    txn_ref: Optional[str] = Field(None, description="Transaction reference")
    
    # Status
    status: str = Field(default="pending", description="Invoice status: pending, paid, cancelled, executed")
    payment_status: str = Field(default="pending", description="Payment status")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Invoice expiration time")
    paid_at: Optional[datetime] = Field(None, description="Payment timestamp")
    executed_at: Optional[datetime] = Field(None, description="Investment execution timestamp")


class StrategyCreateRequest(BaseModel):
    """Request model for creating investment strategy"""
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    strategy_type: StrategyType = Field(..., description="Type of investment strategy")
    trigger_type: TriggerType = Field(..., description="What triggers this investment")
    amount: float = Field(..., description="Investment amount in INR")
    percentage: Optional[float] = Field(None, description="Percentage of salary/amount")
    crypto_tokens: List[str] = Field(..., description="List of crypto tokens to invest in")
    allocation: Dict[str, float] = Field(..., description="Token allocation percentages")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    max_investment: float = Field(..., description="Maximum investment amount")
    min_investment: float = Field(..., description="Minimum investment amount")


class StrategyResponse(BaseModel):
    """Response model for investment strategy"""
    success: bool = Field(..., description="Whether the operation was successful")
    strategy: Optional[InvestmentStrategy] = Field(None, description="Investment strategy")
    message: str = Field(..., description="Response message")


class InvoiceResponse(BaseModel):
    """Response model for investment invoice"""
    success: bool = Field(..., description="Whether the operation was successful")
    invoice: Optional[InvestmentInvoice] = Field(None, description="Investment invoice")
    message: str = Field(..., description="Response message") 