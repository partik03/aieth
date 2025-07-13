"""
Escrow service for matching, releasing, and managing escrow deposits
"""

import uuid
from datetime import datetime
from typing import Optional
from src.services.db import db_service

class EscrowService:
    """Service for escrow deposit matching and release"""
    
    async def match_escrow(self, crypto_type: str, amount: float) -> Optional[dict]:
        """Find a confirmed escrow deposit with enough balance"""
        escrows = await db_service.get_documents(
            "escrow_deposits",
            {"token_symbol": crypto_type, "status": "confirmed", "amount": {"$gte": amount}}
        )
        if not escrows:
            return None
        # Pick the oldest suitable escrow
        escrows.sort(key=lambda e: e.get("created_at", datetime.utcnow()))
        return escrows[0]

    async def mark_pending_upi(self, escrow_id: str, buyer_id: str, txn_ref: str):
        """Mark escrow as pending UPI payment"""
        await db_service.update_document(
            "escrow_deposits",
            {"_id": escrow_id},
            {"buyer_id": buyer_id, "txn_ref": txn_ref, "status": "pending_upi", "updated_at": datetime.utcnow()}
        )

    async def release_escrow(self, escrow_id: str, buyer_wallet_address: str) -> bool:
        """Release escrow: mark as released and transfer crypto (mock)"""
        escrow = await db_service.get_document("escrow_deposits", {"_id": escrow_id})
        if not escrow or escrow.get("status") != "pending_upi":
            return False
        amount = escrow["amount"]
        token = escrow["token_symbol"]
        seller_wallet = escrow["wallet_address"]
        buyer_id = escrow.get("buyer_id")
        # Mark escrow as released
        await db_service.update_document(
            "escrow_deposits",
            {"_id": escrow_id},
            {"status": "released", "released_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        )
        # Simulate wallet transfer
        await self._mock_wallet_transfer(seller_wallet, buyer_wallet_address, token, amount)
        return True

    async def _mock_wallet_transfer(self, from_wallet: str, to_wallet: str, token: str, amount: float):
        """Simulate crypto transfer between wallets in DB"""
        # Deduct from seller
        await db_service.update_document(
            "wallets",
            {"wallet_address": from_wallet},
            {f"crypto_balance.{token}": {"$inc": -amount}, "updated_at": datetime.utcnow()}
        )
        # Add to buyer
        await db_service.update_document(
            "wallets",
            {"wallet_address": to_wallet},
            {f"crypto_balance.{token}": {"$inc": amount}, "updated_at": datetime.utcnow()}
        )

    async def get_escrow_by_txn_ref(self, txn_ref: str) -> Optional[dict]:
        return await db_service.get_document("escrow_deposits", {"txn_ref": txn_ref})

# Global instance
escrow_service = EscrowService() 