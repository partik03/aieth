"""
Wallet API routes for Biconomy Smart Account operations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from src.services.biconomy_service import biconomy_service
from src.services.db import get_collection
from datetime import datetime

router = APIRouter()

class TransferRequest(BaseModel):
    smart_wallet_address: str
    to_address: str
    token_address: str  # "0x0000000000000000000000000000000000000000" for ETH
    amount: str  # Amount in wei
    user_private_key: str = None  # Optional, if not provided uses backend signer

class DepositRequest(BaseModel):
    smart_wallet_address: str
    amount: str  # Amount in wei
    user_private_key: str = None

@router.post("/wallet/transfer")
async def transfer_assets(request: TransferRequest):
    """
    Transfer ERC20 tokens or ETH using Biconomy Smart Account
    
    - **smart_wallet_address**: Smart wallet address
    - **to_address**: Recipient address
    - **token_address**: Token contract address (0x0 for ETH)
    - **amount**: Amount in wei
    - **user_private_key**: Optional private key for signing
    """
    try:
        # Determine if it's ETH or ERC20 transfer
        if request.token_address.lower() == "0x0000000000000000000000000000000000000000":
            # ETH transfer
            calldata = biconomy_service.encode_eth_transfer(request.to_address, int(request.amount))
            value = int(request.amount)
        else:
            # ERC20 transfer
            calldata = biconomy_service.encode_erc20_transfer(
                request.token_address,
                request.to_address,
                int(request.amount)
            )
            value = 0
        
        # Build UserOperation
        user_op = biconomy_service.build_user_operation(
            request.smart_wallet_address,
            request.to_address,
            calldata,
            value
        )
        
        # Sign UserOperation
        signature = biconomy_service.sign_user_operation(
            user_op,
            request.user_private_key
        )
        
        # Send UserOperation
        result = await biconomy_service.send_user_operation(user_op, signature)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": result["error"],
                    "error_code": "TRANSFER_FAILED"
                }
            )
        
        # Save transaction to database
        collection = await get_collection("transactions")
        await collection.insert_one({
            "smart_wallet_address": request.smart_wallet_address,
            "to_address": request.to_address,
            "token_address": request.token_address,
            "amount": request.amount,
            "user_op_hash": result["userOpHash"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "type": "transfer"
        })
        
        return {
            "success": True,
            "user_op_hash": result["userOpHash"],
            "message": "Transfer initiated successfully",
            "status": "pending"
        }
        
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

@router.post("/wallet/deposit")
async def deposit_funds(request: DepositRequest):
    """
    Deposit funds to smart wallet (typically from UPI)
    
    - **smart_wallet_address**: Smart wallet address
    - **amount**: Amount in wei
    - **user_private_key**: Optional private key for signing
    """
    try:
        # For deposits, we might just record the transaction
        # since the funds are already in the smart wallet from UPI
        
        # Save deposit record to database
        collection = await get_collection("transactions")
        await collection.insert_one({
            "smart_wallet_address": request.smart_wallet_address,
            "amount": request.amount,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
            "type": "deposit",
            "source": "upi"
        })
        
        return {
            "success": True,
            "message": "Deposit recorded successfully",
            "amount": request.amount,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        )

@router.get("/wallet/transaction/{user_op_hash}")
async def get_transaction_status(user_op_hash: str):
    """
    Get transaction status by UserOperation hash
    
    - **user_op_hash**: UserOperation hash from transfer
    """
    try:
        result = await biconomy_service.get_transaction_status(user_op_hash)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": result["error"],
                    "error_code": "STATUS_CHECK_FAILED"
                }
            )
        
        return {
            "success": True,
            "user_op_hash": user_op_hash,
            "status": result["status"],
            "transaction_hash": result.get("transactionHash"),
            "receipt": result.get("receipt")
        }
        
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

@router.get("/wallet/transactions/{smart_wallet_address}")
async def get_wallet_transactions(smart_wallet_address: str, limit: int = 10):
    """
    Get recent transactions for a smart wallet
    
    - **smart_wallet_address**: Smart wallet address
    - **limit**: Number of transactions to return
    """
    try:
        collection = await get_collection("transactions")
        
        transactions = await collection.find(
            {"smart_wallet_address": smart_wallet_address}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "smart_wallet_address": smart_wallet_address,
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get transactions: {str(e)}",
                "error_code": "TRANSACTIONS_ERROR"
            }
        ) 