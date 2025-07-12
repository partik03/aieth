"""
Aadhaar verification API routes using DigiLocker
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.models.aadhaar import (
    AadhaarInitiateRequest,
    AadhaarVerifyRequest,
    AadhaarInitiateResponse,
    AadhaarVerifyResponse
)
from src.services.aadhaar_service import aadhaar_service

router = APIRouter()


@router.post("/initiate", response_model=AadhaarInitiateResponse)
async def initiate_aadhaar_verification(request: AadhaarInitiateRequest):
    """
    Initiate Aadhaar verification by generating OTP
    
    - **aadhaar_number**: Aadhaar number in format xxxx-xxxx-xxxx
    - Returns transaction ID for OTP verification
    """
    try:
        response = await aadhaar_service.initiate_verification(request)
        print(response)
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": response.message,
                    "error_code": response.error_code
                }
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.post("/verify", response_model=AadhaarVerifyResponse)
async def verify_aadhaar_otp(request: AadhaarVerifyRequest):
    """
    Verify Aadhaar OTP and retrieve KYC data
    
    - **otp**: 6-digit OTP received on Aadhaar-linked mobile
    - **txn**: Transaction ID from initiate response
    - Returns verification status and KYC data
    """
    try:
        response = await aadhaar_service.verify_otp(request)
        
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": response.message,
                    "error_code": response.error_code
                }
            )
        
        if not response.verified:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": response.message,
                    "error_code": response.error_code
                }
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        ) 