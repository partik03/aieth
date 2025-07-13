"""
UPI payment API routes for crypto purchase transactions
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.models.upi_payment import (
    UPIPaymentInitiateRequest,
    UPIPaymentInitiateResponse,
    UPIPaymentCallbackRequest,
    UPIPaymentCallbackResponse,
    PaymentStatus
)
from src.services.upi_service import upi_service
from src.api.dependencies import get_current_user
from src.models.user import User
from src.services.escrow_service import escrow_service
from src.services.wallet_service import wallet_service
from src.services.investment_strategy_service import investment_strategy_service

router = APIRouter()


@router.post("/initiate-payment", response_model=UPIPaymentInitiateResponse)
async def initiate_upi_payment(request: UPIPaymentInitiateRequest, current_user: User = Depends(get_current_user)):
    """
    Initiate UPI payment and generate QR code
    
    - **user_id**: User ID making the payment (from token)
    - **amount**: Payment amount in INR
    - Returns UPI string and QR code for payment
    """
    try:
        # Use authenticated user's ID instead of request user_id
        request.user_id = current_user.id
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
        
        # Investment execution logic for successful payments
        if request.status == PaymentStatus.SUCCESS:
            # Check if this is an investment invoice payment
            payment = await upi_service.get_payment_by_txn_ref(request.txn_ref)
            if payment and payment.get("upi_id") == "investment@crypto-upi":
                # Find investment invoice by txn_ref
                invoices = await investment_strategy_service.get_user_invoices(payment.get("user_id", ""))
                invoice = next((i for i in invoices if i.txn_ref == request.txn_ref), None)
                
                if invoice:
                    # Execute the investment automatically
                    try:
                        await investment_strategy_service.execute_investment(invoice.id)
                        print(f"✅ Investment executed automatically for invoice {invoice.id}")
                    except Exception as e:
                        print(f"❌ Failed to execute investment: {e}")
            
            # Escrow release logic (existing)
            escrow = await escrow_service.get_escrow_by_txn_ref(request.txn_ref)
            if escrow and escrow.get("status") == "pending_upi":
                # Get buyer wallet address (assume buyer has a wallet)
                buyer_id = escrow.get("buyer_id")
                buyer_wallet = await wallet_service.get_wallet_by_user_id(buyer_id)
                if buyer_wallet:
                    await escrow_service.release_escrow(escrow["_id"], buyer_wallet["wallet_address"])
        
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

        print(payment)
        
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
            "payment": payment
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