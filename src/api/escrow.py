"""
Escrow API routes for crypto deposit management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from src.models.escrow import (
    EscrowDepositCreate,
    EscrowDepositResponse,
    EscrowDepositListResponse,
    EscrowDeposit,
    EscrowStatus
)
from src.services.mock_blockchain_listener import mock_blockchain_listener as blockchain_listener
from src.api.dependencies import get_current_user
from src.models.user import User
from src.services.escrow_service import escrow_service
from src.services.upi_service import upi_service
import uuid

from pydantic import BaseModel

class EscrowBuyRequest(BaseModel):
    user_id: str
    crypto_type: str
    amount: float

class EscrowBuyResponse(BaseModel):
    upi_string: str
    qr_code: str
    txn_ref: str
    message: str

router = APIRouter(prefix="/escrow", tags=["Escrow Deposits"])


@router.post("/deposits", response_model=EscrowDepositResponse, status_code=201)
async def create_escrow_deposit(
    deposit_create: EscrowDepositCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new escrow deposit record
    
    - **wallet_address**: User's wallet address
    - **amount**: Deposit amount
    - **token_symbol**: Token symbol (ETH, USDT, MATIC, etc.)
    - Returns escrow deposit ID and instructions
    """
    try:
        # Create escrow deposit record
        deposit_data = await blockchain_listener.create_escrow_deposit(
            wallet_address=deposit_create.wallet_address,
            amount=deposit_create.amount,
            token_symbol=deposit_create.token_symbol,
            user_id=current_user.id
        )
        
        # Get escrow wallet address for deposit instructions
        escrow_wallet = blockchain_listener.escrow_wallet
        
        return EscrowDepositResponse(
            success=True,
            deposit_id=deposit_data["_id"],
            message=f"Escrow deposit created. Send {deposit_create.amount} {deposit_create.token_symbol} to {escrow_wallet}",
            deposit=EscrowDeposit(**deposit_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create escrow deposit: {str(e)}"
        )


@router.get("/deposits", response_model=EscrowDepositListResponse)
async def get_escrow_deposits(
    status: Optional[EscrowStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user)
):
    """
    Get escrow deposits for current user
    
    - **status**: Optional status filter (pending, confirmed, cancelled, completed)
    - Returns list of escrow deposits
    """
    try:
        # Get deposits for current user
        deposits = await blockchain_listener.get_escrow_deposits(
            wallet_address=None,  # We'll filter by user_id in the service
            status=status.value if status else None
        )
        
        # Filter by user_id (since we don't have user_id in the service filter yet)
        user_deposits = [d for d in deposits if d.get("user_id") == current_user.id]
        
        # Calculate statistics
        total_amount = sum(d.get("amount", 0) for d in user_deposits)
        pending_count = len([d for d in user_deposits if d.get("status") == "pending"])
        confirmed_count = len([d for d in user_deposits if d.get("status") == "confirmed"])
        
        return EscrowDepositListResponse(
            success=True,
            deposits=[EscrowDeposit(**deposit) for deposit in user_deposits],
            count=len(user_deposits),
            total_amount=total_amount,
            pending_count=pending_count,
            confirmed_count=confirmed_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get escrow deposits: {str(e)}"
        )


@router.get("/deposits/{deposit_id}", response_model=EscrowDepositResponse)
async def get_escrow_deposit(
    deposit_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific escrow deposit by ID
    
    - **deposit_id**: Escrow deposit ID
    - Returns escrow deposit details
    """
    try:
        # Get all deposits for user and find the specific one
        deposits = await blockchain_listener.get_escrow_deposits()
        user_deposits = [d for d in deposits if d.get("user_id") == current_user.id]
        
        deposit = next((d for d in user_deposits if d.get("_id") == deposit_id), None)
        
        if not deposit:
            raise HTTPException(
                status_code=404,
                detail="Escrow deposit not found"
            )
        
        return EscrowDepositResponse(
            success=True,
            deposit_id=deposit_id,
            message="Escrow deposit found",
            deposit=EscrowDeposit(**deposit)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get escrow deposit: {str(e)}"
        )


@router.get("/deposits/wallet/{wallet_address}", response_model=EscrowDepositListResponse)
async def get_escrow_deposits_by_wallet(
    wallet_address: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get escrow deposits for a specific wallet address
    
    - **wallet_address**: Wallet address to filter by
    - Returns list of escrow deposits for that wallet
    """
    try:
        # Ensure user can only access their own wallet data
        deposits = await blockchain_listener.get_escrow_deposits(wallet_address=wallet_address)
        user_deposits = [d for d in deposits if d.get("user_id") == current_user.id]
        
        # Calculate statistics
        total_amount = sum(d.get("amount", 0) for d in user_deposits)
        pending_count = len([d for d in user_deposits if d.get("status") == "pending"])
        confirmed_count = len([d for d in user_deposits if d.get("status") == "confirmed"])
        
        return EscrowDepositListResponse(
            success=True,
            deposits=[EscrowDeposit(**deposit) for deposit in user_deposits],
            count=len(user_deposits),
            total_amount=total_amount,
            pending_count=pending_count,
            confirmed_count=confirmed_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get escrow deposits: {str(e)}"
        )


@router.post("/buy", response_model=EscrowBuyResponse)
async def buy_escrow_crypto(request: EscrowBuyRequest, current_user: User = Depends(get_current_user)):
    """
    Buy crypto from confirmed escrow using UPI
    """
    # 1. Match a confirmed escrow
    escrow = await escrow_service.match_escrow(request.crypto_type, request.amount)
    if not escrow:
        raise HTTPException(status_code=404, detail="No matching escrow found")
    # 2. Mark escrow as pending UPI
    txn_ref = str(uuid.uuid4())
    await escrow_service.mark_pending_upi(escrow["_id"], current_user.id, txn_ref)
    # 3. Generate UPI string and QR code
    upi_payload = {
        "user_id": current_user.id,
        "amount": request.amount,
        "upi_id": "test@upi"  # You may want to use a real or mock UPI ID
    }
    upi_result = await upi_service.create_payment(upi_payload)
    if not upi_result.success:
        raise HTTPException(status_code=500, detail="Failed to generate UPI payment")
    # 4. Return UPI info
    return EscrowBuyResponse(
        upi_string=upi_result.upi_string,
        qr_code=upi_result.qr_code,
        txn_ref=txn_ref,
        message=f"Pay via UPI to buy {request.amount} {request.crypto_type}"
    )


@router.get("/status")
async def get_escrow_status(current_user: User = Depends(get_current_user)):
    """
    Get escrow system status and statistics
    
    Returns overall escrow system status for the user
    """
    try:
        deposits = await blockchain_listener.get_escrow_deposits()
        user_deposits = [d for d in deposits if d.get("user_id") == current_user.id]
        
        # Calculate statistics
        total_deposits = len(user_deposits)
        total_amount = sum(d.get("amount", 0) for d in user_deposits)
        pending_amount = sum(d.get("amount", 0) for d in user_deposits if d.get("status") == "pending")
        confirmed_amount = sum(d.get("amount", 0) for d in user_deposits if d.get("status") == "confirmed")
        
        # Group by token
        token_stats = {}
        for deposit in user_deposits:
            token = deposit.get("token_symbol", "UNKNOWN")
            if token not in token_stats:
                token_stats[token] = {"total": 0, "pending": 0, "confirmed": 0}
            
            amount = deposit.get("amount", 0)
            status = deposit.get("status", "pending")
            
            token_stats[token]["total"] += amount
            if status == "pending":
                token_stats[token]["pending"] += amount
            elif status == "confirmed":
                token_stats[token]["confirmed"] += amount
        
        return {
            "success": True,
            "user_id": current_user.id,
            "total_deposits": total_deposits,
            "total_amount": total_amount,
            "pending_amount": pending_amount,
            "confirmed_amount": confirmed_amount,
            "token_breakdown": token_stats,
            "escrow_wallet": blockchain_listener.escrow_wallet,
            "listener_status": "active" if blockchain_listener.is_listening else "inactive"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get escrow status: {str(e)}"
        ) 