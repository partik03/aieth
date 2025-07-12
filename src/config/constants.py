"""
Application constants and enums
"""

from enum import Enum
from typing import Dict, Any


class TransactionType(str, Enum):
    """Transaction types"""
    CRYPTO_PURCHASE = "crypto_purchase"
    CRYPTO_SALE = "crypto_sale"
    UPI_DEPOSIT = "upi_deposit"
    UPI_WITHDRAWAL = "upi_withdrawal"
    ESCROW_DEPOSIT = "escrow_deposit"
    ESCROW_RELEASE = "escrow_release"
    LOAN_DISBURSEMENT = "loan_disbursement"
    LOAN_REPAYMENT = "loan_repayment"


class TransactionStatus(str, Enum):
    """Transaction statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CryptoCurrency(str, Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH"
    POLYGON = "MATIC"
    USDT = "USDT"
    USDC = "USDC"


class UserType(str, Enum):
    """User types"""
    INDIAN = "indian"
    INTERNATIONAL = "international"
    MERCHANT = "merchant"


class LoanStatus(str, Enum):
    """Loan statuses"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    REPAID = "repaid"
    DEFAULTED = "defaulted"


# API Response Messages
API_MESSAGES = {
    "SUCCESS": "Operation completed successfully",
    "UNAUTHORIZED": "Authentication required",
    "FORBIDDEN": "Access denied",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Invalid input data",
    "INTERNAL_ERROR": "Internal server error",
    "UPI_PAYMENT_SUCCESS": "UPI payment processed successfully",
    "UPI_PAYMENT_FAILED": "UPI payment failed",
    "INSUFFICIENT_BALANCE": "Insufficient balance",
    "ESCROW_LOCKED": "Escrow is locked",
    "LOAN_APPROVED": "Loan application approved",
    "LOAN_REJECTED": "Loan application rejected",
}

# UPI Configuration
UPI_CONFIG = {
    "SUPPORTED_APPS": ["gpay", "phonepe", "paytm", "amazonpay", "bhim"],
    "MAX_AMOUNT": 100000,  # INR
    "MIN_AMOUNT": 1,  # INR
    "TIMEOUT_SECONDS": 300,  # 5 minutes
}

# Crypto Configuration
CRYPTO_CONFIG = {
    "MIN_TRADE_AMOUNT": {
        "BTC": 0.001,
        "ETH": 0.01,
        "MATIC": 1,
        "USDT": 10,
        "USDC": 10,
    },
    "MAX_TRADE_AMOUNT": {
        "BTC": 10,
        "ETH": 100,
        "MATIC": 10000,
        "USDT": 100000,
        "USDC": 100000,
    },
    "NETWORK_FEES": {
        "BTC": 0.0001,
        "ETH": 0.005,
        "MATIC": 0.1,
        "USDT": 0.001,
        "USDC": 0.001,
    }
}

# AI Agent Configuration
AI_CONFIG = {
    "MAX_INVESTMENT_PERCENTAGE": 0.1,  # 10% of total balance
    "MIN_INVESTMENT_AMOUNT": 100,  # INR
    "RISK_LEVELS": ["low", "medium", "high"],
    "STRATEGY_TYPES": ["dca", "momentum", "arbitrage", "trend_following"],
}

# Microfinance Configuration
MICROFINANCE_CONFIG = {
    "MIN_LOAN_AMOUNT": 1000,  # INR
    "MAX_LOAN_AMOUNT": 100000,  # INR
    "LOAN_TERMS": [3, 6, 12, 24],  # months
    "INTEREST_RATES": {
        "low_risk": 0.08,  # 8%
        "medium_risk": 0.12,  # 12%
        "high_risk": 0.18,  # 18%
    },
    "MIN_CREDIT_SCORE": 600,
    "MAX_CREDIT_SCORE": 900,
}

# Database Configuration
DB_CONFIG = {
    "POOL_SIZE": 20,
    "MAX_OVERFLOW": 30,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 3600,
}

# Rate Limiting
RATE_LIMITS = {
    "API_CALLS_PER_MINUTE": 60,
    "UPI_PAYMENTS_PER_HOUR": 10,
    "CRYPTO_TRADES_PER_DAY": 50,
    "AI_QUERIES_PER_MINUTE": 30,
}

# Security Configuration
SECURITY_CONFIG = {
    "PASSWORD_MIN_LENGTH": 8,
    "PASSWORD_REQUIREMENTS": {
        "uppercase": True,
        "lowercase": True,
        "numbers": True,
        "special_chars": True,
    },
    "SESSION_TIMEOUT": 3600,  # 1 hour
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOCKOUT_DURATION": 900,  # 15 minutes
} 