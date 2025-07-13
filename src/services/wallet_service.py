"""
Wallet service for managing crypto and fiat balances
"""

from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId

from src.models.wallet import Wallet, WalletCreate, WalletUpdate
from src.services.db import get_collection


class WalletService:
    """Service for wallet operations"""
    
    def __init__(self):
        self.collection_name = "wallets"
    
    async def create_wallet(self, user_id: str, wallet_address: str) -> Wallet:
        """Create a new wallet for a user"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Check if wallet already exists for this user
            existing_wallet = await collection.find_one({"user_id": user_id})
            if existing_wallet:
                raise ValueError(f"Wallet already exists for user: {user_id}")
            
            # Create wallet document
            wallet_data = WalletCreate(
                user_id=user_id,
                wallet_address=wallet_address,
                crypto_balance={},
                fiat_balance=0.0
            ).dict()
            
            wallet_data["created_at"] = datetime.utcnow()
            wallet_data["updated_at"] = datetime.utcnow()
            
            # Insert into database
            result = await collection.insert_one(wallet_data)
            
            # Return created wallet
            created_wallet = await collection.find_one({"_id": result.inserted_id})
            return Wallet(**created_wallet)
            
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}")
    
    async def get_wallet_by_user_id(self, user_id: str) -> Optional[Wallet]:
        """Get wallet by user ID"""
        try:
            collection = await get_collection(self.collection_name)
            wallet_doc = await collection.find_one({"user_id": user_id})
            
            if wallet_doc:
                return Wallet(**wallet_doc)
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get wallet: {str(e)}")
    
    async def get_or_create_wallet(self, user_id: str, wallet_address: str = None) -> Wallet:
        """Get existing wallet or create a new one if it doesn't exist"""
        try:
            wallet = await self.get_wallet_by_user_id(user_id)
            
            if wallet:
                return wallet
            
            # Create a new wallet if it doesn't exist
            if not wallet_address:
                wallet_address = f"0x{user_id[-40:]}" if len(user_id) >= 40 else f"0x{user_id:0>40}"
            
            return await self.create_wallet(user_id, wallet_address)
            
        except Exception as e:
            raise Exception(f"Failed to get or create wallet: {str(e)}")
    
    async def ensure_wallet_exists(self, user_id: str) -> Wallet:
        """Ensure a wallet exists for the user, create if needed"""
        try:
            wallet = await self.get_wallet_by_user_id(user_id)
            
            if not wallet:
                # Create a default wallet with some initial balance for demo
                wallet_address = f"0x{user_id[-40:]}" if len(user_id) >= 40 else f"0x{user_id:0>40}"
                wallet = await self.create_wallet(user_id, wallet_address)
                
                # Add some initial balance for demo purposes
                await self.update_fiat_balance(user_id, 10000.0)  # ₹10,000 initial balance
                await self.update_crypto_balance(user_id, "BTC", 0.001)  # Small BTC balance
                await self.update_crypto_balance(user_id, "ETH", 0.01)   # Small ETH balance
                await self.update_crypto_balance(user_id, "USDT", 100.0) # Some USDT
                
                print(f"✅ Created wallet for user {user_id} with initial balance")
            
            return wallet
            
        except Exception as e:
            raise Exception(f"Failed to ensure wallet exists: {str(e)}")
    
    async def update_fiat_balance(self, user_id: str, amount: float) -> Wallet:
        """Update fiat balance using $inc operator"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Update using $inc for atomic increment
            result = await collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"fiat_balance": amount},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Wallet not found for user: {user_id}")
            
            # Return updated wallet
            updated_wallet = await collection.find_one({"user_id": user_id})
            return Wallet(**updated_wallet)
            
        except Exception as e:
            raise Exception(f"Failed to update fiat balance: {str(e)}")
    
    async def update_crypto_balance(self, user_id: str, crypto_symbol: str, amount: float) -> Wallet:
        """Update crypto balance for a specific currency"""
        try:
            collection = await get_collection(self.collection_name)
            
            # Update using $inc for atomic increment
            result = await collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {f"crypto_balance.{crypto_symbol}": amount},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Wallet not found for user: {user_id}")
            
            # Return updated wallet
            updated_wallet = await collection.find_one({"user_id": user_id})
            return Wallet(**updated_wallet)
            
        except Exception as e:
            raise Exception(f"Failed to update crypto balance: {str(e)}")
    
    async def set_crypto_balance(self, user_id: str, crypto_balances: Dict[str, float]) -> Wallet:
        """Set complete crypto balance dictionary"""
        try:
            collection = await get_collection(self.collection_name)
            
            result = await collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "crypto_balance": crypto_balances,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Wallet not found for user: {user_id}")
            
            # Return updated wallet
            updated_wallet = await collection.find_one({"user_id": user_id})
            return Wallet(**updated_wallet)
            
        except Exception as e:
            raise Exception(f"Failed to set crypto balance: {str(e)}")
    
    async def delete_wallet(self, user_id: str) -> bool:
        """Delete wallet by user ID"""
        try:
            collection = await get_collection(self.collection_name)
            result = await collection.delete_one({"user_id": user_id})
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to delete wallet: {str(e)}")


# Global wallet service instance
wallet_service = WalletService() 