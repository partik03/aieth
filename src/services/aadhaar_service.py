"""
Aadhaar verification service using DigiLocker sandbox API
"""

import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET

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


class AadhaarService:
    """Service for Aadhaar verification using DigiLocker API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.digilocker_base_url
        self.client_id = self.settings.digilocker_client_id
        self.client_secret = self.settings.digilocker_client_secret
        self.redirect_uri = self.settings.digilocker_redirect_uri
    
    async def initiate_verification(self, request: AadhaarInitiateRequest) -> AadhaarInitiateResponse:
        """Initiate Aadhaar verification by generating OTP"""
        try:
            # Prepare DigiLocker request
            digilocker_request = DigiLockerGenerateOTPRequest(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                aadhaar_number=request.aadhaar_number.replace('-', '')
            )
            
            # Call DigiLocker generate OTP endpoint
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generateOTP",
                    json=digilocker_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        return AadhaarInitiateResponse(
                            success=True,
                            txn=data.get("txn"),
                            message="OTP sent successfully to Aadhaar-linked mobile"
                        )
                    else:
                        return AadhaarInitiateResponse(
                            success=False,
                            message=data.get("message", "Failed to generate OTP"),
                            error_code=data.get("error_code")
                        )
                else:
                    return AadhaarInitiateResponse(
                        success=False,
                        message=f"DigiLocker API error: {response.status_code}",
                        error_code=str(response.status_code)
                    )
                    
        except Exception as e:
            return AadhaarInitiateResponse(
                success=False,
                message=f"Service error: {str(e)}",
                error_code="SERVICE_ERROR"
            )
    
    async def verify_otp(self, request: AadhaarVerifyRequest) -> AadhaarVerifyResponse:
        """Verify OTP and retrieve Aadhaar KYC data"""
        try:
            # Step 1: Verify OTP
            verify_request = DigiLockerVerifyOTPRequest(
                client_id=self.client_id,
                client_secret=self.client_secret,
                txn=request.txn,
                otp=request.otp
            )
            
            async with httpx.AsyncClient() as client:
                # Verify OTP
                verify_response = await client.post(
                    f"{self.base_url}/verifyOTP",
                    json=verify_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if verify_response.status_code != 200:
                    return AadhaarVerifyResponse(
                        success=False,
                        verified=False,
                        message=f"OTP verification failed: {verify_response.status_code}",
                        error_code=str(verify_response.status_code)
                    )
                
                verify_data = verify_response.json()
                
                if verify_data.get("status") != "success":
                    return AadhaarVerifyResponse(
                        success=False,
                        verified=False,
                        message=verify_data.get("message", "Invalid OTP"),
                        error_code=verify_data.get("error_code")
                    )
                
                # Step 2: Get Aadhaar KYC data
                auth_request = DigiLockerGetAuthDataRequest(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    txn=request.txn
                )
                
                auth_response = await client.post(
                    f"{self.base_url}/getAuthData",
                    json=auth_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    
                    if auth_data.get("status") == "success":
                        # Parse KYC data from XML
                        kyc_data = self._parse_kyc_xml(auth_data.get("kyc_data", ""))
                        
                        return AadhaarVerifyResponse(
                            success=True,
                            verified=True,
                            aadhaar_number=kyc_data.get("aadhaar_number"),
                            kyc_data=AadhaarKYCData(**kyc_data),
                            message="Aadhaar verification successful"
                        )
                    else:
                        return AadhaarVerifyResponse(
                            success=False,
                            verified=False,
                            message=auth_data.get("message", "Failed to retrieve KYC data"),
                            error_code=auth_data.get("error_code")
                        )
                else:
                    return AadhaarVerifyResponse(
                        success=False,
                        verified=False,
                        message=f"Failed to retrieve KYC data: {auth_response.status_code}",
                        error_code=str(auth_response.status_code)
                    )
                    
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