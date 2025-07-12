"""
UPI payment service with QR code generation and mock payment simulation
"""

import qrcode
import base64
import uuid
import io
from typing import Optional, Dict, Any
from datetime import datetime

from src.models.upi_payment import (
    UPIPayment,
    UPIPaymentCreate,
    UPIPaymentUpdate,
    PaymentStatus,
    UPIPaymentInitiateRequest,
    UPIPaymentInitiateResponse,
    UPIPaymentCallbackRequest,
    UPIPaymentCallbackResponse
)
from src.services.db import get_collection


class UPIService:
    """Service for UPI payment operations"""
    
    def __init__(self):
        self.collection_name = "upi_payments"
        self.default_upi_id = "test@upi"
        self.merchant_name = "CryptoUPI"
    
    def _generate_txn_ref(self) -> str:
        """Generate unique transaction reference"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"TXN_{timestamp}_{unique_id}"
    
    def _create_upi_string(self, upi_id: str, amount: float, txn_ref: str) -> str:
        """Create UPI payment string"""
        # Format: upi://pay?pa=<upi_id>&pn=<merchant_name>&am=<amount>&cu=INR&tn=<txn_ref>
        upi_string = (
            f"upi://pay?"
            f"pa={upi_id}&"
            f"pn={self.merchant_name}&"
            f"am={amount}&"
            f"cu=INR&"
            f"tn={txn_ref}"
        )
        return upi_string
    
    def _generate_qr_code(self, upi_string: str) -> str:
        """Generate QR code from UPI string and return as base64"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_string)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return ""
    
    async def create_upi_qr(self, amount: float, upi_id: str = None) -> Dict[str, Any]:
        """Create UPI QR code for payment"""
        try:
            if upi_id is None:
                upi_id = self.default_upi_id
            
            txn_ref = self._generate_txn_ref()
            upi_string = self._create_upi_string(upi_id, amount, txn_ref)
            qr_code = self._generate_qr_code(upi_string)
            
            return {
                "txn_ref": txn_ref,
                "upi_string": upi_string,
                "qr_code": qr_code,
                "upi_id": upi_id,
                "amount": amount
            }
            
        except Exception as e:
            raise Exception(f"Failed to create UPI QR: {str(e)}")
    
    async def create_payment(self, request: UPIPaymentInitiateRequest) -> UPIPaymentInitiateResponse:
        """Create a new UPI payment and generate QR code"""
        try:
            # Generate UPI QR
            qr_data = await self.create_upi_qr(request.amount, self.default_upi_id)
            
            # Create payment record
            payment_data = UPIPaymentCreate(
                user_id=request.user_id,
                amount=request.amount,
                upi_id=self.default_upi_id
            ).dict()
            
            payment_data["txn_ref"] = qr_data["txn_ref"]
            payment_data["status"] = PaymentStatus.PENDING
            payment_data["created_at"] = datetime.utcnow()
            payment_data["updated_at"] = datetime.utcnow()
            
            # Save to database
            collection = await get_collection(self.collection_name)
            result = await collection.insert_one(payment_data)
            
            if result.inserted_id:
                return UPIPaymentInitiateResponse(
                    success=True,
                    txn_ref=qr_data["txn_ref"],
                    upi_string=qr_data["upi_string"],
                    qr_code=qr_data["qr_code"],
                    message="UPI payment initiated successfully"
                )
            else:
                return UPIPaymentInitiateResponse(
                    success=False,
                    message="Failed to create payment record"
                )
                
        except Exception as e:
            return UPIPaymentInitiateResponse(
                success=False,
                message=f"Failed to create UPI payment: {str(e)}"
            )
    
    async def simulate_upi_payment(self, txn_ref: str, amount: float) -> PaymentStatus:
        """Simulate UPI payment status change"""
        try:
            # Simulate payment processing (mock logic)
            # In real implementation, this would be called by UPI gateway callback
            
            # For demo purposes, simulate success for even amounts, failure for odd amounts
            if int(amount) % 2 == 0:
                status = PaymentStatus.SUCCESS
            else:
                status = PaymentStatus.FAILED
            
            # Update payment status in database
            collection = await get_collection(self.collection_name)
            await collection.update_one(
                {"txn_ref": txn_ref},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return status
            
        except Exception as e:
            print(f"Error simulating UPI payment: {e}")
            return PaymentStatus.FAILED
    
    async def process_callback(self, request: UPIPaymentCallbackRequest) -> UPIPaymentCallbackResponse:
        """Process UPI payment callback"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Update payment status
            result = await collection.update_one(
                {"txn_ref": request.txn_ref},
                {
                    "$set": {
                        "status": request.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                return UPIPaymentCallbackResponse(
                    success=True,
                    message=f"Payment status updated to {request.status}"
                )
            else:
                return UPIPaymentCallbackResponse(
                    success=False,
                    message="Transaction reference not found"
                )
                
        except Exception as e:
            return UPIPaymentCallbackResponse(
                success=False,
                message=f"Failed to process callback: {str(e)}"
            )
    
    async def get_payment_by_txn_ref(self, txn_ref: str) -> Optional[UPIPayment]:
        """Get payment by transaction reference"""
        try:
            collection = await get_collection(self.collection_name)
            print(txn_ref)
            payment_doc = await collection.find_one({"txn_ref": txn_ref})

            print(payment_doc)
            
            if payment_doc:
                payment_doc['_id'] = str(payment_doc['_id'])
                for key, value in payment_doc.items():
                    if isinstance(value, datetime):
                        payment_doc[key] = value.isoformat()
                return dict(payment_doc)
            return None
            
        except Exception as e:
            print(f"Error getting payment: {e}")
            return None


# Global UPI service instance
upi_service = UPIService() 