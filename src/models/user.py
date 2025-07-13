"""
User model for authentication and profile management using Aadhaar
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user model"""
    aadhaar_number: str = Field(..., description="Aadhaar number in format xxxx-xxxx-xxxx")
    full_name: str = Field(..., description="User's full name")
    aadhaar_verified: bool = Field(default=False, description="Aadhaar verification status")
    
    @validator('aadhaar_number')
    def validate_aadhaar_format(cls, v):
        """Validate Aadhaar number format"""
        # Remove hyphens and validate 12 digits
        clean_number = v.replace('-', '')
        if not re.match(r'^\d{12}$', clean_number):
            raise ValueError('Aadhaar number must be 12 digits in format xxxx-xxxx-xxxx')
        return v


class UserCreate(BaseModel):
    """Model for creating a new user after Aadhaar verification"""
    aadhaar_number: str = Field(..., description="Aadhaar number in format xxxx-xxxx-xxxx")
    full_name: str = Field(..., description="User's full name")
    kyc_data: Optional[dict] = Field(None, description="KYC data from Aadhaar verification")
    
    @validator('aadhaar_number')
    def validate_aadhaar_format(cls, v):
        """Validate Aadhaar number format"""
        # Remove hyphens and validate 12 digits
        clean_number = v.replace('-', '')
        if not re.match(r'^\d{12}$', clean_number):
            raise ValueError('Aadhaar number must be 12 digits in format xxxx-xxxx-xxxx')
        return v


class UserLogin(BaseModel):
    """Model for user login using Aadhaar"""
    aadhaar_number: str = Field(..., description="Aadhaar number in format xxxx-xxxx-xxxx")
    
    @validator('aadhaar_number')
    def validate_aadhaar_format(cls, v):
        """Validate Aadhaar number format"""
        # Remove hyphens and validate 12 digits
        clean_number = v.replace('-', '')
        if not re.match(r'^\d{12}$', clean_number):
            raise ValueError('Aadhaar number must be 12 digits in format xxxx-xxxx-xxxx')
        return v


class UserUpdate(BaseModel):
    """Model for updating user profile"""
    full_name: Optional[str] = None
    aadhaar_verified: Optional[bool] = None


class User(UserBase):
    """Complete user model with database fields"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    kyc_data: Optional[dict] = Field(None, description="KYC data from Aadhaar verification")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "aadhaar_number": "1234-5678-9012",
                "full_name": "John Doe",
                "aadhaar_verified": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class UserResponse(BaseModel):
    """User response model"""
    id: str = Field(..., description="User ID")
    aadhaar_number: str = Field(..., description="Aadhaar number")
    full_name: str = Field(..., description="User's full name")
    aadhaar_verified: bool = Field(..., description="Aadhaar verification status")
    created_at: datetime = Field(..., description="Account creation date")


class Token(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    aadhaar_number: Optional[str] = None 