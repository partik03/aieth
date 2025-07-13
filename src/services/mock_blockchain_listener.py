"""
Mock blockchain listener for testing escrow deposits
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import random

from src.services.db import db_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockBlockchainListener:
    """Mock blockchain listener for testing escrow deposits"""
    
    def __init__(self):
        self.is_listening = False
        self.escrow_wallet = "0x1234567890123456789012345678901234567890"
        self.mock_transactions = []
        
    async def start_listening(self):
        """Start mock blockchain listener"""
        self.is_listening = True
        logger.info("🚀 Starting mock blockchain listener...")
        logger.info(f"🎯 Mock escrow wallet: {self.escrow_wallet}")
        
        while self.is_listening:
            try:
                # Simulate processing every 10 seconds
                await asyncio.sleep(10)
                
                # Check for pending deposits and randomly confirm some
                await self._simulate_deposit_confirmations()
                
            except Exception as e:
                logger.error(f"❌ Error in mock blockchain listener: {e}")
                await asyncio.sleep(5)
    
    async def stop_listening(self):
        """Stop mock blockchain listener"""
        self.is_listening = False
        logger.info("🛑 Stopped mock blockchain listener")
    
    async def _simulate_deposit_confirmations(self):
        """Simulate random deposit confirmations"""
        try:
            # Get pending deposits
            pending_deposits = await self.get_escrow_deposits(status="pending")
            
            if not pending_deposits:
                return
            
            # Randomly confirm 20% of pending deposits
            for deposit in pending_deposits:
                if random.random() < 0.2:  # 20% chance
                    await self._confirm_deposit(deposit)
                    
        except Exception as e:
            logger.error(f"❌ Error simulating confirmations: {e}")
    
    async def _confirm_deposit(self, deposit: Dict):
        """Confirm a mock deposit"""
        try:
            # Generate mock transaction data
            mock_txn_hash = f"0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}"
            mock_block_number = random.randint(18000000, 19000000)
            
            # Update deposit
            update_data = {
                "status": "confirmed",
                "txn_hash": mock_txn_hash,
                "block_number": mock_block_number,
                "confirmed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db_service.update_document(
                "escrow_deposits",
                {"_id": deposit["_id"]},
                update_data
            )
            
            logger.info(f"✅ Mock deposit confirmed: {deposit.get('amount')} {deposit.get('token_symbol')} from {deposit.get('wallet_address')}")
            
        except Exception as e:
            logger.error(f"❌ Error confirming mock deposit: {e}")
    
    async def get_escrow_deposits(self, wallet_address: str = None, status: str = None) -> List[Dict]:
        """Get escrow deposits from database"""
        try:
            filter_query = {}
            if wallet_address:
                filter_query["wallet_address"] = wallet_address.lower()
            if status:
                filter_query["status"] = status
            
            deposits = await db_service.get_documents("escrow_deposits", filter_query)
            return deposits
            
        except Exception as e:
            logger.error(f"❌ Error getting escrow deposits: {e}")
            return []
    
    async def create_escrow_deposit(self, wallet_address: str, amount: float, 
                                  token_symbol: str, user_id: str) -> Dict:
        """Create a new escrow deposit record"""
        try:
            deposit_data = {
                "wallet_address": wallet_address.lower(),
                "amount": amount,
                "token_symbol": token_symbol,
                "user_id": user_id,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            deposit_id = await db_service.insert_document("escrow_deposits", deposit_data)
            deposit_data["_id"] = deposit_id
            
            logger.info(f"📝 Created mock escrow deposit: {amount} {token_symbol} for {wallet_address}")
            return deposit_data
            
        except Exception as e:
            logger.error(f"❌ Error creating escrow deposit: {e}")
            raise


# Global mock blockchain listener instance
mock_blockchain_listener = MockBlockchainListener() 