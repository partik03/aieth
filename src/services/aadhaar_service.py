"""
Aadhaar verification service using DigiLocker sandbox API
"""

import httpx
import json
from bson import ObjectId
from typing import Optional, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
from twilio.rest import Client
import random
from src.services.db import get_collection
from src.config.settings import get_settings
from src.models.aadhaar import (
    AadhaarInitiateRequest,
    AadhaarVerifyRequest,
    AadhaarInitiateResponse,
    AadhaarVerifyResponse,
    AadhaarKYCData,
    DigiLockerGenerateOTPRequest,
    DigiLockerVerifyOTPRequest,
    DigiLockerGetAuthDataRequest
)
from src.services.wallet_service import wallet_service


class AadhaarService:
    """Service for Aadhaar verification using DigiLocker API"""
    
    def __init__(self):
        self.collection_name = "aadhaar_verification"
    
    async def initiate_verification(self, request: AadhaarInitiateRequest) -> AadhaarInitiateResponse:
        """Initiate Aadhaar verification by generating OTP"""
        try:
            
            account_sid = 'ACdcd1b22e57f5d93ceb9b332ab7a21c23'
            auth_token = '19c8a215c787c5da3038265dd3a24533'
            otp = str(random.randint(100000, 999999))
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_='+15075919786',
                body=f"Your AADHAAR verifcation code is : {otp}",
                to='+919653040310'
            )

            collection = await get_collection(self.collection_name)

            aadhaar_verification_doc = {
                "aadhaar_number": request.aadhaar_number,
                "mobile_number":'+919653040310',
                "otp": otp,
                "generated_at": datetime.utcnow()
            }
            
            result = await collection.insert_one(aadhaar_verification_doc)
            if result.inserted_id:
                return AadhaarInitiateResponse(success= True, txn=str(result.inserted_id))
            return None
                    
        except Exception as e:
            return AadhaarInitiateResponse(
                success=False,
                message=f"Service error: {str(e)}",
                error_code="SERVICE_ERROR"
            )
    
    async def verify_otp(self, request: AadhaarVerifyRequest) -> AadhaarVerifyResponse:
        """Verify OTP and retrieve Aadhaar KYC data"""
        try:
            collection = await get_collection(self.collection_name)
            aadhaar_verification_doc = await collection.find_one({"_id": ObjectId(request.txn)})

            if aadhaar_verification_doc["otp"] == request.otp:
                wallet_service.create_wallet(aadhaar_verification_doc["aadhaar_number"])
                return AadhaarVerifyResponse(success=True, verified=True)
            else:
                return AadhaarVerifyResponse(success=True, verified=False)
            
        except Exception as e:
            return AadhaarVerifyResponse(
                success=False,
                verified=False,
                message=f"Service error: {str(e)}",
                error_code="SERVICE_ERROR"
            )
    
    def _parse_kyc_xml(self, xml_data: str) -> Dict[str, Any]:
        """Parse KYC data from XML response"""
        try:
            if not xml_data:
                return {}
            
            # Parse XML
            root = ET.fromstring(xml_data)
            
            # Extract KYC data
            kyc_data = {}
            
            # Aadhaar number
            aadhaar_elem = root.find(".//AadhaarNumber")
            if aadhaar_elem is not None:
                kyc_data["aadhaar_number"] = aadhaar_elem.text
            
            # Name
            name_elem = root.find(".//Name")
            if name_elem is not None:
                kyc_data["name"] = name_elem.text
            
            # Date of Birth
            dob_elem = root.find(".//DateOfBirth")
            if dob_elem is not None:
                kyc_data["date_of_birth"] = dob_elem.text
            
            # Gender
            gender_elem = root.find(".//Gender")
            if gender_elem is not None:
                kyc_data["gender"] = gender_elem.text
            
            # Address
            address_elem = root.find(".//Address")
            if address_elem is not None:
                kyc_data["address"] = address_elem.text
            
            # Mobile
            mobile_elem = root.find(".//Mobile")
            if mobile_elem is not None:
                kyc_data["mobile"] = mobile_elem.text
            
            # Email
            email_elem = root.find(".//Email")
            if email_elem is not None:
                kyc_data["email"] = email_elem.text
            
            return kyc_data
            
        except Exception as e:
            print(f"Error parsing KYC XML: {e}")
            return {}


# Global Aadhaar service instance
aadhaar_service = AadhaarService() 