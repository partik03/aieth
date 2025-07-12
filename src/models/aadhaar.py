"""
Aadhaar verification models for DigiLocker integration
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class AadhaarInitiateRequest(BaseModel):
    """Request model for initiating Aadhaar verification"""
    aadhaar_number: str = Field(..., description="Aadhaar number in format xxxx-xxxx-xxxx")
    
    @validator('aadhaar_number')
    def validate_aadhaar_format(cls, v):
        """Validate Aadhaar number format"""
        # Remove hyphens and validate 12 digits
        clean_number = v.replace('-', '')
        if not re.match(r'^\d{12}$', clean_number):
            raise ValueError('Aadhaar number must be 12 digits in format xxxx-xxxx-xxxx')
        return v


class AadhaarVerifyRequest(BaseModel):
    """Request model for verifying Aadhaar OTP"""
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    txn: str = Field(..., description="Transaction ID from initiate response")


class DigiLockerGenerateOTPRequest(BaseModel):
    """DigiLocker generate OTP request"""
    client_id: str
    client_secret: str
    redirect_uri: str
    aadhaar_number: str
    state: str = "aadhaar_verification"


class DigiLockerVerifyOTPRequest(BaseModel):
    """DigiLocker verify OTP request"""
    client_id: str
    client_secret: str
    txn: str
    otp: str


class DigiLockerGetAuthDataRequest(BaseModel):
    """DigiLocker get auth data request"""
    client_id: str
    client_secret: str
    txn: str


class AadhaarKYCData(BaseModel):
    """Aadhaar KYC data from DigiLocker"""
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None


class AadhaarInitiateResponse(BaseModel):
    """Response model for Aadhaar initiation"""
    success: bool
    txn: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[str] = None


class AadhaarVerifyResponse(BaseModel):
    """Response model for Aadhaar verification"""
    success: bool
    verified: bool
    aadhaar_number: Optional[str] = None
    kyc_data: Optional[AadhaarKYCData] = None
    message: Optional[str] = None
    error_code: Optional[str] = None


class AadhaarUserData(BaseModel):
    """Aadhaar data to store in user/wallet"""
    aadhaar_number: str
    aadhaar_verified: bool = True
    kyc_data: Optional[AadhaarKYCData] = None
    verification_timestamp: Optional[str] = None 