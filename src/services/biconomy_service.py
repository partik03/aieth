"""
Biconomy Smart Account Service for ERC-4337 transactions
"""

import json
import requests
import os
from typing import Dict, Any, Optional
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import time

from src.config.settings import get_settings


class BiconomyService:
    """Service for Biconomy Smart Account operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.bundler_url = f"https://bundler.biconomy.io/api/v2/{self.settings.biconomy_api_key}/"
        self.paymaster_url = f"https://paymaster.biconomy.io/api/v1/{self.settings.biconomy_api_key}/"
        self.chain_id = self.settings.chain_id  # e.g., 80001 for Mumbai
        self.entry_point = self.settings.entry_point_address
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.settings.web3_rpc_url))
        
        # Backend signer (for relayer operations)
        self.backend_signer = Account.from_key(self.settings.biconomy_relayer_key)
    
    def build_user_operation(
        self,
        smart_wallet_address: str,
        target_address: str,
        calldata: str,
        value: int = 0
    ) -> Dict[str, Any]:
        """Build a UserOperation for ERC-4337"""
        
        # Get current nonce
        nonce = self._get_nonce(smart_wallet_address)
        
        # Get gas estimates
        gas_estimate = self._estimate_gas(target_address, calldata, value)
        
        # Build UserOperation
        user_op = {
            "sender": smart_wallet_address,
            "nonce": nonce,
            "initCode": "0x",  # Empty for existing accounts
            "callData": calldata,
            "callGasLimit": gas_estimate["callGasLimit"],
            "verificationGasLimit": gas_estimate["verificationGasLimit"],
            "preVerificationGas": gas_estimate["preVerificationGas"],
            "maxFeePerGas": gas_estimate["maxFeePerGas"],
            "maxPriorityFeePerGas": gas_estimate["maxPriorityFeePerGas"],
            "paymasterAndData": "0x",  # Will be filled by paymaster
            "signature": "0x"  # Will be filled after signing
        }
        
        return user_op
    
    def sign_user_operation(
        self,
        user_op: Dict[str, Any],
        user_private_key: Optional[str] = None
    ) -> str:
        """Sign a UserOperation with user's private key or backend signer"""
        
        # Remove signature and paymasterAndData for hashing
        user_op_for_hash = user_op.copy()
        user_op_for_hash["signature"] = "0x"
        user_op_for_hash["paymasterAndData"] = "0x"
        
        # Create UserOperation hash
        user_op_hash = self._get_user_op_hash(user_op_for_hash)
        
        # Sign with user's private key or backend signer
        if user_private_key:
            signer = Account.from_key(user_private_key)
        else:
            signer = self.backend_signer
        
        # Sign the hash
        message = encode_defunct(primitive=user_op_hash)
        signed_message = signer.sign_message(message)
        
        return signed_message.signature.hex()
    
    async def send_user_operation(
        self,
        user_op: Dict[str, Any],
        signature: str
    ) -> Dict[str, Any]:
        """Send UserOperation to Biconomy bundler"""
        
        # Add signature to UserOperation
        user_op["signature"] = signature
        
        # Prepare payload
        payload = {
            "userOp": user_op,
            "entryPoint": self.entry_point
        }
        
        try:
            # Send to Biconomy bundler
            response = requests.post(
                f"{self.bundler_url}userOp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "userOpHash": result.get("userOpHash"),
                    "message": "UserOperation sent successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Bundler error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send UserOperation: {str(e)}"
            }
    
    async def get_transaction_status(self, user_op_hash: str) -> Dict[str, Any]:
        """Get transaction status from Biconomy bundler"""
        
        try:
            response = requests.get(
                f"{self.bundler_url}userOp/{user_op_hash}",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "status": result.get("status"),
                    "transactionHash": result.get("transactionHash"),
                    "receipt": result.get("receipt")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get status: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get transaction status: {str(e)}"
            }
    
    def encode_erc20_transfer(
        self,
        token_address: str,
        to_address: str,
        amount: int
    ) -> str:
        """Encode ERC20 transfer calldata"""
        
        # ERC20 transfer function signature
        transfer_signature = "transfer(address,uint256)"
        
        # Encode parameters
        encoded_params = self.w3.codec.encode_abi(
            ["address", "uint256"],
            [to_address, amount]
        )
        
        # Combine function selector with encoded parameters
        function_selector = self.w3.keccak(text=transfer_signature)[:4]
        calldata = function_selector + encoded_params
        
        return calldata
    
    def encode_eth_transfer(self, to_address: str, amount: int) -> str:
        """Encode ETH transfer calldata (simple call)"""
        
        # For ETH transfer, we just need to call the target address
        # The calldata can be empty, and value will be set in UserOperation
        return "0x"
    
    def _get_nonce(self, smart_wallet_address: str) -> int:
        """Get current nonce for smart wallet"""
        # This would typically call the EntryPoint contract
        # For now, return 0 (you'll need to implement this based on your EntryPoint)
        return 0
    
    def _estimate_gas(
        self,
        target_address: str,
        calldata: str,
        value: int
    ) -> Dict[str, int]:
        """Estimate gas for UserOperation"""
        
        # These are example values - you should implement proper gas estimation
        return {
            "callGasLimit": 100000,
            "verificationGasLimit": 200000,
            "preVerificationGas": 50000,
            "maxFeePerGas": 30000000000,  # 30 gwei
            "maxPriorityFeePerGas": 1500000000  # 1.5 gwei
        }
    
    def _get_user_op_hash(self, user_op: Dict[str, Any]) -> bytes:
        """Get UserOperation hash for signing"""
        
        # Pack UserOperation data
        packed_data = self.w3.codec.encode_abi(
            [
                "address", "uint256", "bytes32", "bytes",
                "uint256", "uint256", "uint256", "uint256", "uint256",
                "bytes32", "bytes32"
            ],
            [
                user_op["sender"],
                user_op["nonce"],
                user_op["initCode"],
                user_op["callData"],
                user_op["callGasLimit"],
                user_op["verificationGasLimit"],
                user_op["preVerificationGas"],
                user_op["maxFeePerGas"],
                user_op["maxPriorityFeePerGas"],
                user_op["paymasterAndData"],
                user_op["signature"]
            ]
        )
        
        # Hash the packed data
        return self.w3.keccak(packed_data)


# Global Biconomy service instance
biconomy_service = BiconomyService() 