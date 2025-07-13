"""
Wallet model for crypto and fiat balance management
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WalletBase(BaseModel):
    """Base wallet model"""
    user_id: str = Field(..., description="Unique user identifier")
    wallet_address: str = Field(..., description="Blockchain wallet address")
    private_key: str = Field(..., description="Private Key")
    crypto_balance: Dict[str, float] = Field(
        default_factory=dict,
        description="Crypto balances by currency symbol"
    )
    fiat_balance: float = Field(
        default=0.0,
        description="Fiat balance in INR"
    )


class WalletCreate(WalletBase):
    """Model for creating a new wallet"""
    pass


class WalletUpdate(BaseModel):
    """Model for updating wallet balances"""
    crypto_balance: Optional[Dict[str, float]] = None
    fiat_balance: Optional[float] = None


class Wallet(WalletBase):
    """Complete wallet model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "user_id": "user123",
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "crypto_balance": {
                    "ETH": 0.5,
                    "USDT": 100.0,
                    "BTC": 0.01
                },
                "fiat_balance": 5000.0
            }
        }
    } 