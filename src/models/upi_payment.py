"""
UPI payment models for crypto purchase transactions
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    """UPI payment statuses"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UPIPaymentBase(BaseModel):
    """Base UPI payment model"""
    user_id: str = Field(..., description="User ID making the payment")
    upi_id: str = Field(..., description="UPI ID for receiving payment")
    amount: float = Field(..., gt=0, description="Payment amount in INR")
    txn_ref: str = Field(..., description="Unique transaction reference")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")


class UPIPaymentCreate(BaseModel):
    """Model for creating a new UPI payment"""
    user_id: str = Field(..., description="User ID making the payment")
    amount: float = Field(..., gt=0, description="Payment amount in INR")
    upi_id: str = Field(default="test@upi", description="UPI ID for receiving payment")


class UPIPaymentUpdate(BaseModel):
    """Model for updating UPI payment status"""
    status: PaymentStatus
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UPIPayment(UPIPaymentBase):
    """Complete UPI payment model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "user_id": "user123",
                "upi_id": "test@upi",
                "amount": 1000.0,
                "txn_ref": "TXN_20240101_001",
                "status": "pending"
            }
        }
    }


class UPIPaymentInitiateRequest(BaseModel):
    """Request model for initiating UPI payment"""
    user_id: str = Field(..., description="User ID making the payment")
    amount: float = Field(..., gt=0, description="Payment amount in INR")


class UPIPaymentInitiateResponse(BaseModel):
    """Response model for UPI payment initiation"""
    success: bool
    txn_ref: Optional[str] = None
    upi_string: Optional[str] = None
    qr_code: Optional[str] = None
    message: str


class UPIPaymentCallbackRequest(BaseModel):
    """Request model for UPI payment callback"""
    txn_ref: str = Field(..., description="Transaction reference")
    status: PaymentStatus = Field(..., description="Payment status")


class UPIPaymentCallbackResponse(BaseModel):
    """Response model for UPI payment callback"""
    success: bool
    message: str 