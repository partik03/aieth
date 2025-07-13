"""
Blockchain listener service for real-time crypto deposit detection
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_abi import decode_abi
from eth_utils import to_checksum_address

from src.services.db import db_service
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ERC20 Transfer event signature
ERC20_TRANSFER_EVENT = "Transfer(address,address,uint256)"
ERC20_TRANSFER_TOPIC = Web3.keccak(text=ERC20_TRANSFER_EVENT).hex()

# Common token addresses (mainnet)
TOKEN_ADDRESSES = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT on Ethereum
    "USDC": "0xA0b86a33E6441b8C4C8C8C8C8C8C8C8C8C8C8C8",  # USDC on Ethereum
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB",  # MATIC on Ethereum
}

# Token decimals
TOKEN_DECIMALS = {
    "USDT": 6,
    "USDC": 6,
    "MATIC": 18,
    "ETH": 18,
}


class BlockchainListener:
    """Real-time blockchain listener for crypto deposits"""
    
    def __init__(self):
        self.settings = get_settings()
        self.w3 = None
        self.escrow_wallet = None
        self.is_listening = False
        self.last_processed_block = 0
        
        # Initialize Web3 connection
        self._setup_web3()
    
    def _setup_web3(self):
        """Setup Web3 connection to blockchain"""
        try:
            # Connect to Ethereum mainnet or testnet
            self.w3 = Web3(Web3.HTTPProvider(self.settings.ethereum_rpc_url))
            
            # Add POA middleware for testnets
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Set escrow wallet address
            self.escrow_wallet = to_checksum_address(self.settings.escrow_wallet_address)
            
            # Test connection
            if self.w3.is_connected():
                logger.info(f"✅ Connected to blockchain: {self.settings.ethereum_rpc_url}")
                logger.info(f"🎯 Escrow wallet: {self.escrow_wallet}")
                logger.info(f"🔗 Current block: {self.w3.eth.block_number}")
            else:
                logger.error("❌ Failed to connect to blockchain")
                
        except Exception as e:
            logger.error(f"❌ Web3 setup failed: {e}")
    
    async def start_listening(self):
        """Start listening for blockchain deposits"""
        if not self.w3 or not self.w3.is_connected():
            logger.error("❌ Web3 not connected, cannot start listening")
            return
        
        self.is_listening = True
        logger.info("🚀 Starting blockchain deposit listener...")
        
        # Get current block number
        self.last_processed_block = self.w3.eth.block_number
        logger.info(f"📦 Starting from block: {self.last_processed_block}")
        
        while self.is_listening:
            try:
                await self._process_new_blocks()
                await asyncio.sleep(5)  # Poll every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in blockchain listener: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def stop_listening(self):
        """Stop listening for blockchain deposits"""
        self.is_listening = False
        logger.info("🛑 Stopped blockchain deposit listener")
    
    async def _process_new_blocks(self):
        """Process new blocks for deposits"""
        try:
            current_block = self.w3.eth.block_number
            
            if current_block <= self.last_processed_block:
                return
            
            # Process blocks from last processed to current
            for block_num in range(self.last_processed_block + 1, current_block + 1):
                await self._process_block(block_num)
            
            self.last_processed_block = current_block
            
        except Exception as e:
            logger.error(f"❌ Error processing blocks: {e}")
    
    async def _process_block(self, block_number: int):
        """Process a single block for deposits"""
        try:
            # Get block with full transaction details
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            
            if not block or not block.transactions:
                return
            
            logger.debug(f"🔍 Processing block {block_number} with {len(block.transactions)} transactions")
            
            # Process each transaction in the block
            for tx in block.transactions:
                await self._process_transaction(tx, block_number)
                
        except Exception as e:
            logger.error(f"❌ Error processing block {block_number}: {e}")
    
    async def _process_transaction(self, tx, block_number: int):
        """Process a single transaction for deposits"""
        try:
            # Check if transaction is to our escrow wallet
            if tx.to and tx.to.lower() == self.escrow_wallet.lower():
                await self._handle_native_deposit(tx, block_number)
            
            # Check for ERC20 transfers to our escrow wallet
            if tx.input and len(tx.input) > 10:
                await self._handle_erc20_transfer(tx, block_number)
                
        except Exception as e:
            logger.error(f"❌ Error processing transaction {tx.hash.hex()}: {e}")
    
    async def _handle_native_deposit(self, tx, block_number: int):
        """Handle native ETH/MATIC deposits"""
        try:
            from_address = tx['from']
            amount_wei = tx.value
            amount_eth = self.w3.from_wei(amount_wei, 'ether')
            
            logger.info(f"💰 Native deposit detected: {amount_eth} ETH from {from_address}")
            
            # Update escrow record
            await self._update_escrow_deposit(
                wallet_address=from_address,
                amount=float(amount_eth),
                token_symbol="ETH",
                txn_hash=tx.hash.hex(),
                block_number=block_number
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling native deposit: {e}")
    
    async def _handle_erc20_transfer(self, tx, block_number: int):
        """Handle ERC20 token transfers"""
        try:
            # Check if this is a Transfer function call
            if tx.input[:10] != "0xa9059cbb":  # Transfer function signature
                return
            
            # Decode the transfer data
            transfer_data = tx.input[10:]  # Remove function signature
            
            # Decode parameters: (address to, uint256 amount)
            try:
                decoded = decode_abi(['address', 'uint256'], bytes.fromhex(transfer_data))
                to_address = "0x" + decoded[0].hex()
                amount_raw = decoded[1]
                
                # Check if transfer is to our escrow wallet
                if to_address.lower() != self.escrow_wallet.lower():
                    return
                
                # Determine token and amount
                token_address = tx.to
                token_symbol = await self._get_token_symbol(token_address)
                decimals = TOKEN_DECIMALS.get(token_symbol, 18)
                amount = amount_raw / (10 ** decimals)
                
                logger.info(f"🪙 ERC20 deposit detected: {amount} {token_symbol} from {tx['from']}")
                
                # Update escrow record
                await self._update_escrow_deposit(
                    wallet_address=tx['from'],
                    amount=float(amount),
                    token_symbol=token_symbol,
                    txn_hash=tx.hash.hex(),
                    block_number=block_number
                )
                
            except Exception as e:
                logger.error(f"❌ Error decoding ERC20 transfer: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error handling ERC20 transfer: {e}")
    
    async def _get_token_symbol(self, token_address: str) -> str:
        """Get token symbol from address"""
        # For now, return a default symbol
        # In production, you'd query the token contract
        return "USDT"  # Default to USDT
    
    async def _update_escrow_deposit(self, wallet_address: str, amount: float, 
                                   token_symbol: str, txn_hash: str, block_number: int):
        """Update escrow deposit record in database"""
        try:
            # Find pending escrow deposit for this wallet
            escrow_filter = {
                "wallet_address": wallet_address.lower(),
                "status": "pending"
            }
            
            escrow_deposit = await db_service.get_document("escrow_deposits", escrow_filter)
            
            if escrow_deposit:
                # Update escrow deposit
                update_data = {
                    "status": "confirmed",
                    "txn_hash": txn_hash,
                    "block_number": block_number,
                    "confirmed_at": datetime.utcnow(),
                    "amount": amount,
                    "token_symbol": token_symbol
                }
                
                await db_service.update_document(
                    "escrow_deposits", 
                    {"_id": escrow_deposit["_id"]}, 
                    update_data
                )
                
                logger.info(f"✅ Escrow deposit confirmed: {amount} {token_symbol} from {wallet_address}")
                
                # You could also trigger additional actions here:
                # - Send notification to user
                # - Update wallet balance
                # - Trigger UPI payment processing
                
            else:
                logger.warning(f"⚠️ No pending escrow found for wallet: {wallet_address}")
                
        except Exception as e:
            logger.error(f"❌ Error updating escrow deposit: {e}")
    
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
            
            logger.info(f"📝 Created escrow deposit: {amount} {token_symbol} for {wallet_address}")
            return deposit_data
            
        except Exception as e:
            logger.error(f"❌ Error creating escrow deposit: {e}")
            raise


# Global blockchain listener instance
blockchain_listener = BlockchainListener() 