"""
Escrow deposit models for crypto deposits
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class EscrowStatus(str, Enum):
    """Escrow deposit statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EscrowDepositBase(BaseModel):
    """Base escrow deposit model"""
    wallet_address: str = Field(..., description="User's wallet address")
    amount: float = Field(..., gt=0, description="Deposit amount")
    token_symbol: str = Field(..., description="Token symbol (ETH, USDT, MATIC, etc.)")
    user_id: str = Field(..., description="User ID who made the deposit")
    status: EscrowStatus = Field(default=EscrowStatus.PENDING, description="Deposit status")


class EscrowDepositCreate(BaseModel):
    """Model for creating a new escrow deposit"""
    wallet_address: str = Field(..., description="User's wallet address")
    amount: float = Field(..., gt=0, description="Deposit amount")
    token_symbol: str = Field(..., description="Token symbol (ETH, USDT, MATIC, etc.)")


class EscrowDepositUpdate(BaseModel):
    """Model for updating escrow deposit"""
    status: Optional[EscrowStatus] = None
    txn_hash: Optional[str] = None
    block_number: Optional[int] = None
    confirmed_at: Optional[datetime] = None


class EscrowDeposit(EscrowDepositBase):
    """Complete escrow deposit model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    txn_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    block_number: Optional[int] = Field(None, description="Block number where confirmed")
    confirmed_at: Optional[datetime] = Field(None, description="When deposit was confirmed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "amount": 0.5,
                "token_symbol": "ETH",
                "user_id": "user123",
                "status": "pending",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class EscrowDepositResponse(BaseModel):
    """Response model for escrow deposit operations"""
    success: bool
    deposit_id: Optional[str] = None
    message: str
    deposit: Optional[EscrowDeposit] = None


class EscrowDepositListResponse(BaseModel):
    """Response model for listing escrow deposits"""
    success: bool
    deposits: list[EscrowDeposit]
    count: int
    total_amount: float
    pending_count: int
    confirmed_count: int 