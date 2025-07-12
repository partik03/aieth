"""
UPI payment API routes for crypto purchase transactions
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.models.upi_payment import (
    UPIPaymentInitiateRequest,
    UPIPaymentInitiateResponse,
    UPIPaymentCallbackRequest,
    UPIPaymentCallbackResponse,
    PaymentStatus
)
from src.services.upi_service import upi_service

router = APIRouter()


@router.post("/initiate-payment", response_model=UPIPaymentInitiateResponse)
async def initiate_upi_payment(request: UPIPaymentInitiateRequest):
    """
    Initiate UPI payment and generate QR code
    
    - **user_id**: User ID making the payment
    - **amount**: Payment amount in INR
    - Returns UPI string and QR code for payment
    """
    try:
        response = await upi_service.create_payment(request)
        
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": response.message,
                    "error_code": "PAYMENT_INITIATION_FAILED"
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


@router.post("/mock-callback", response_model=UPIPaymentCallbackResponse)
async def mock_upi_callback(request: UPIPaymentCallbackRequest):
    """
    Mock UPI payment callback for testing
    
    - **txn_ref**: Transaction reference from initiate response
    - **status**: Payment status (success/failed/cancelled)
    - Updates payment status in database
    """
    try:
        response = await upi_service.process_callback(request)
        
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": response.message,
                    "error_code": "CALLBACK_PROCESSING_FAILED"
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


@router.post("/simulate-payment")
async def simulate_payment(txn_ref: str, amount: float):
    """
    Simulate UPI payment status change for testing
    
    - **txn_ref**: Transaction reference
    - **amount**: Payment amount (even amounts = success, odd amounts = failed)
    - Returns simulated payment status
    """
    try:
        status = await upi_service.simulate_upi_payment(txn_ref, amount)
        
        return {
            "success": True,
            "txn_ref": txn_ref,
            "amount": amount,
            "status": status,
            "message": f"Payment simulation completed: {status}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Simulation failed: {str(e)}",
                "error_code": "SIMULATION_ERROR"
            }
        )


@router.get("/payment-status/{txn_ref}")
async def get_payment_status(txn_ref: str):
    """
    Get payment status by transaction reference
    
    - **txn_ref**: Transaction reference
    - Returns current payment status and details
    """
    try:
        payment = await upi_service.get_payment_by_txn_ref(txn_ref)
        
        if not payment:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Payment not found",
                    "error_code": "PAYMENT_NOT_FOUND"
                }
            )
        
        return {
            "success": True,
            "payment": {
                "txn_ref": payment.txn_ref,
                "user_id": payment.user_id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at,
                "updated_at": payment.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get payment status: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        ) 