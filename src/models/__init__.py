"""
Models package for the Crypto-UPI Backend
"""

from .wallet import Wallet, WalletCreate, WalletUpdate, WalletBase
from .aadhaar import (
    AadhaarInitiateRequest,
    AadhaarVerifyRequest,
    AadhaarInitiateResponse,
    AadhaarVerifyResponse,
    AadhaarKYCData,
    AadhaarUserData
)
from .upi_payment import (
    UPIPayment,
    UPIPaymentCreate,
    UPIPaymentUpdate,
    PaymentStatus,
    UPIPaymentInitiateRequest,
    UPIPaymentInitiateResponse,
    UPIPaymentCallbackRequest,
    UPIPaymentCallbackResponse
)
from .salary import (
    Salary,
    SalaryCreate,
    InvestmentStrategy,
    InvestmentStrategyCreate,
    SalaryRequest,
    SalaryResponse
)

__all__ = [
    "Wallet",
    "WalletCreate", 
    "WalletUpdate",
    "WalletBase",
    "AadhaarInitiateRequest",
    "AadhaarVerifyRequest",
    "AadhaarInitiateResponse",
    "AadhaarVerifyResponse",
    "AadhaarKYCData",
    "AadhaarUserData",
    "UPIPayment",
    "UPIPaymentCreate",
    "UPIPaymentUpdate",
    "PaymentStatus",
    "UPIPaymentInitiateRequest",
    "UPIPaymentInitiateResponse",
    "UPIPaymentCallbackRequest",
    "UPIPaymentCallbackResponse",
    "Salary",
    "SalaryCreate",
    "InvestmentStrategy",
    "InvestmentStrategyCreate",
    "SalaryRequest",
    "SalaryResponse"
]
