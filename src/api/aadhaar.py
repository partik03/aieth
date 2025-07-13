"""
Aadhaar verification API routes using DigiLocker
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Depends
from src.services.db import get_collection

from src.models.aadhaar import (
    AadhaarInitiateRequest,
    AadhaarVerifyRequest,
    AadhaarInitiateResponse,
    AadhaarVerifyResponse
)
from src.models.user import UserCreate, UserResponse, Token
from src.services.aadhaar_service import aadhaar_service
from src.services.auth import auth_service
from datetime import timedelta

router = APIRouter()


@router.post("/initiate", response_model=AadhaarInitiateResponse)
async def initiate_aadhaar_verification(request: AadhaarInitiateRequest):
    """
    Initiate Aadhaar verification by generating OTP
    
    - **aadhaar_number**: Aadhaar number in format xxxx-xxxx-xxxx
    - Returns transaction ID for OTP verification
    """
    try:
        print("initiate_aadhaar_verification", request)
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


class RegisterDIDRequest(BaseModel):
    did: str
    aadhaar_no: str
    zk_proof: dict

async def verify_zk_proof(aadhaar_no: str, zk_proof: dict) -> bool:
    # TODO: Replace with actual zkProof verification logic
    # For now, always return True (accept all proofs)
    return True

@router.post("/register_did/")
async def register_did(request: RegisterDIDRequest):
    # 1. Verify zkProof
    if not await verify_zk_proof(request.aadhaar_no, request.zk_proof):
        raise HTTPException(status_code=400, detail="Invalid zkProof")

    # 2. Register DID (store in MongoDB)
    try:
        collection = await get_collection("did_registrations")
        # Check if DID already registered
        existing = await collection.find_one({"did": request.did})
        if existing:
            raise HTTPException(status_code=400, detail="DID already registered")
        # Insert new registration
        await collection.insert_one({
            "did": request.did,
            "aadhaar_no": request.aadhaar_no,
            "zk_proof": request.zk_proof
        })
        return {"status": "success", "message": "DID registered with KYC"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
