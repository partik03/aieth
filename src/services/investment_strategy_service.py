"""
Investment strategy service for AI-driven automated investments
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from web3 import Web3
from eth_account import Account
from src.models.investment_strategy import (
    InvestmentStrategy, 
    InvestmentInvoice, 
    StrategyCreateRequest,
    StrategyType,
    TriggerType
)
from src.services.db import db_service
from src.services.upi_service import upi_service
from src.services.escrow_service import escrow_service
from src.services.twitter_service import twitter_service
from src.services.wallet_service import wallet_service
from src.config.settings import get_settings

settings = get_settings()
w3 = Web3(Web3.HTTPProvider(settings.web3_rpc_url))
ESCROW_ADDRESS = Web3.to_checksum_address(settings.escrow_wallet_address)

class InvestmentStrategyService:
    """Service for managing AI-driven investment strategies"""
    
    def __init__(self):
        self.db = db_service
    
    async def create_strategy(self, user_id: str, strategy_data: StrategyCreateRequest) -> InvestmentStrategy:
        """Create a new investment strategy"""
        try:
            # Validate allocation percentages
            total_allocation = sum(strategy_data.allocation.values())
            if abs(total_allocation - 100.0) > 0.01:
                raise ValueError("Token allocation percentages must sum to 100%")
            
            # Create strategy document
            strategy_doc = {
                "user_id": user_id,
                "name": strategy_data.name,
                "description": strategy_data.description,
                "strategy_type": strategy_data.strategy_type.value,
                "trigger_type": strategy_data.trigger_type.value,
                "amount": strategy_data.amount,
                "percentage": strategy_data.percentage,
                "crypto_tokens": strategy_data.crypto_tokens,
                "allocation": strategy_data.allocation,
                "risk_level": strategy_data.risk_level,
                "max_investment": strategy_data.max_investment,
                "min_investment": strategy_data.min_investment,
                "is_active": True,
                "is_approved": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            strategy_id = await self.db.insert_document("investment_strategies", strategy_doc)
            strategy_doc["_id"] = strategy_id
            
            return InvestmentStrategy(**strategy_doc)
            
        except Exception as e:
            raise Exception(f"Failed to create investment strategy: {str(e)}")
    
    async def get_user_strategies(self, user_id: str) -> List[InvestmentStrategy]:
        """Get all strategies for a user"""
        try:
            strategies_data = await self.db.get_documents("investment_strategies", {"user_id": user_id})
            return [InvestmentStrategy(**strategy) for strategy in strategies_data]
        except Exception as e:
            raise Exception(f"Failed to get user strategies: {str(e)}")
    
    async def get_strategy(self, strategy_id: str) -> Optional[InvestmentStrategy]:
        """Get a specific strategy by ID"""
        try:
            strategy_data = await self.db.get_document("investment_strategies", {"_id": strategy_id})
            if strategy_data:
                return InvestmentStrategy(**strategy_data)
            return None
        except Exception as e:
            raise Exception(f"Failed to get strategy: {str(e)}")
    
    async def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> bool:
        """Update a strategy"""
        try:
            updates["updated_at"] = datetime.utcnow()
            return await self.db.update_document("investment_strategies", {"_id": strategy_id}, updates)
        except Exception as e:
            raise Exception(f"Failed to update strategy: {str(e)}")
    
    async def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a strategy"""
        try:
            return await self.db.delete_document("investment_strategies", {"_id": strategy_id})
        except Exception as e:
            raise Exception(f"Failed to delete strategy: {str(e)}")
    
    async def approve_strategy(self, strategy_id: str) -> bool:
        """Approve a strategy for execution"""
        try:
            return await self.update_strategy(strategy_id, {"is_approved": True})
        except Exception as e:
            raise Exception(f"Failed to approve strategy: {str(e)}")
    
    async def check_triggers(self, user_id: str) -> List[InvestmentStrategy]:
        """Check for strategies that should be triggered"""
        try:
            # Get all active and approved strategies for the user
            strategies_data = await self.db.get_documents("investment_strategies", {
                "user_id": user_id,
                "is_active": True,
                "is_approved": True
            })
            
            triggered_strategies = []
            
            for strategy_data in strategies_data:
                strategy = InvestmentStrategy(**strategy_data)
                
                # Check if strategy should be triggered based on trigger type
                if await self._should_trigger_strategy(strategy):
                    triggered_strategies.append(strategy)
            
            return triggered_strategies
            
        except Exception as e:
            raise Exception(f"Failed to check triggers: {str(e)}")
    
    async def _should_trigger_strategy(self, strategy: InvestmentStrategy) -> bool:
        """Check if a strategy should be triggered"""
        try:
            trigger_type = TriggerType(strategy.trigger_type)
            
            if trigger_type == TriggerType.SALARY_RECEIVED:
                # Check if user received salary recently (within last 24 hours)
                recent_salary = await self._check_recent_salary(strategy.user_id)
                return recent_salary
            
            elif trigger_type == TriggerType.MARKET_DIP:
                # Check if market has dipped (simplified logic)
                return await self._check_market_dip(strategy.crypto_tokens)
            
            elif trigger_type == TriggerType.WEEKLY:
                # Check if it's been a week since last execution
                return await self._check_weekly_trigger(strategy)
            
            elif trigger_type == TriggerType.MONTHLY:
                # Check if it's been a month since last execution
                return await self._check_monthly_trigger(strategy)
            
            elif trigger_type == TriggerType.TRENDING_ALERT:
                # Check if any of the strategy tokens are trending
                return await self._check_trending_tokens(strategy.crypto_tokens)
            
            elif trigger_type == TriggerType.MANUAL:
                # Manual triggers are handled separately
                return False
            
            return False
            
        except Exception as e:
            print(f"Error checking strategy trigger: {e}")
            return False
    
    async def _check_recent_salary(self, user_id: str) -> bool:
        """Check if user received salary recently"""
        try:
            # Check for salary records in the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_salaries = await self.db.get_documents("salary_records", {
                "user_id": user_id,
                "created_at": {"$gte": yesterday}
            })
            return len(recent_salaries) > 0
        except:
            return False
    
    async def _check_market_dip(self, crypto_tokens: List[str]) -> bool:
        """Check if market has dipped (simplified)"""
        # This is a simplified check - in real implementation, you'd check actual price data
        return False  # Placeholder
    
    async def _check_weekly_trigger(self, strategy: InvestmentStrategy) -> bool:
        """Check if weekly trigger should fire"""
        if not strategy.last_executed:
            return True
        
        week_ago = datetime.utcnow() - timedelta(weeks=1)
        return strategy.last_executed < week_ago
    
    async def _check_monthly_trigger(self, strategy: InvestmentStrategy) -> bool:
        """Check if monthly trigger should fire"""
        if not strategy.last_executed:
            return True
        
        month_ago = datetime.utcnow() - timedelta(days=30)
        return strategy.last_executed < month_ago
    
    async def _check_trending_tokens(self, crypto_tokens: List[str]) -> bool:
        """Check if any tokens are trending"""
        try:
            trending_tokens = await twitter_service.get_trending_tokens()
            return any(token in trending_tokens for token in crypto_tokens)
        except:
            return False
    
    async def generate_investment_invoice(self, strategy: InvestmentStrategy, reason: str) -> InvestmentInvoice:
        """Generate an investment invoice for a strategy"""
        try:
            # Calculate investment amount
            investment_amount = strategy.amount
            if strategy.percentage:
                # If percentage is set, calculate based on recent salary
                recent_salary = await self._get_recent_salary_amount(strategy.user_id)
                if recent_salary:
                    investment_amount = (recent_salary * strategy.percentage) / 100
                    investment_amount = min(investment_amount, strategy.max_investment)
                    investment_amount = max(investment_amount, strategy.min_investment)
            
            # Create UPI payment
            upi_request = {
                "user_id": strategy.user_id,
                "amount": investment_amount,
                "upi_id": "investment@crypto-upi"  # You can customize this
            }
            
            upi_response = await upi_service.create_payment(upi_request)
            
            if not upi_response.success:
                raise Exception("Failed to create UPI payment")
            
            # Create invoice document
            invoice_doc = {
                "user_id": strategy.user_id,
                "strategy_id": strategy.id,
                "amount": investment_amount,
                "crypto_tokens": strategy.crypto_tokens,
                "allocation": strategy.allocation,
                "reason": reason,
                "upi_string": upi_response.upi_string,
                "qr_code": upi_response.qr_code,
                "txn_ref": upi_response.txn_ref,
                "status": "pending",
                "payment_status": "pending",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
            }
            
            invoice_id = await self.db.insert_document("investment_invoices", invoice_doc)
            invoice_doc["_id"] = invoice_id
            
            return InvestmentInvoice(**invoice_doc)
            
        except Exception as e:
            raise Exception(f"Failed to generate investment invoice: {str(e)}")
    
    async def _get_recent_salary_amount(self, user_id: str) -> Optional[float]:
        """Get the amount of the most recent salary"""
        try:
            recent_salaries = await self.db.get_documents("salary_records", {
                "user_id": user_id
            })
            
            if recent_salaries:
                # Sort by creation date and get the latest
                recent_salaries.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
                return recent_salaries[0].get("amount", 0)
            
            return None
        except:
            return None
    
    async def execute_investment(self, invoice_id: str) -> bool:
        """Execute an investment after payment is confirmed"""
        try:
            # Get invoice
            invoice_data = await self.db.get_document("investment_invoices", {"_id": invoice_id})
            if not invoice_data:
                raise Exception("Invoice not found")
            
            invoice = InvestmentInvoice(**invoice_data)
            
            if invoice.status != "paid":
                raise Exception("Invoice not paid")
            
            # Get user's wallet
            user_wallet = await wallet_service.get_wallet_by_user_id(invoice.user_id)
            if not user_wallet:
                raise Exception("User wallet not found")
            
            # Execute investment and update wallet balances
            for token, percentage in invoice.allocation.items():
                token_amount = (invoice.amount * percentage) / 100
                
                # Calculate crypto amount based on current price (mock for now)
                # In real implementation, you'd get this from a price API
                crypto_amount = self._calculate_crypto_amount(token_amount, token)
                
                # Update user's crypto balance
                await wallet_service.update_crypto_balance(
                    invoice.user_id, 
                    token, 
                    crypto_amount
                )
                
                # Create escrow deposit record for tracking
                escrow_request = {
                    "wallet_address": user_wallet.wallet_address,
                    "amount": crypto_amount,
                    "token_symbol": token,
                    "user_id": invoice.user_id
                }
                
                # This would integrate with your escrow service
                # await escrow_service.create_escrow_deposit(escrow_request)
            
            # Update invoice status
            await self.db.update_document("investment_invoices", {"_id": invoice_id}, {
                "status": "executed",
                "executed_at": datetime.utcnow()
            })
            
            # Update strategy last executed time
            await self.update_strategy(invoice.strategy_id, {
                "last_executed": datetime.utcnow()
            })

            # Update portfolio performance and user stats
            await self._update_portfolio_performance(invoice.user_id, invoice)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to execute investment: {str(e)}")
    
    def _calculate_crypto_amount(self, inr_amount: float, token: str) -> float:
        """Calculate crypto amount based on INR amount and current token price"""
        # Mock prices - in real implementation, fetch from price API
        token_prices = {
            "BTC": 4500000,  # ₹45,00,000 per BTC
            "ETH": 280000,   # ₹2,80,000 per ETH
            "MATIC": 85,     # ₹85 per MATIC
            "SOL": 8500,     # ₹8,500 per SOL
            "DOGE": 12,      # ₹12 per DOGE
            "USDT": 83,      # ₹83 per USDT
            "USDC": 83       # ₹83 per USDC
        }
        
        price = token_prices.get(token, 100)  # Default price
        return inr_amount / price
    
    async def _update_portfolio_performance(self, user_id: str, invoice: InvestmentInvoice):
        """Update portfolio performance tracking after investment execution"""
        try:
            # Create portfolio performance record
            performance_data = {
                "user_id": user_id,
                "invoice_id": invoice.id,
                "strategy_id": invoice.strategy_id,
                "investment_amount": invoice.amount,
                "crypto_tokens": invoice.crypto_tokens,
                "allocation": invoice.allocation,
                "execution_date": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Store performance record
            await self.db.insert_document("portfolio_performance", performance_data)
            
            # Update user's total investment tracking
            await self._update_user_investment_stats(user_id, invoice.amount)
            
        except Exception as e:
            print(f"Warning: Failed to update portfolio performance: {e}")
    
    async def _update_user_investment_stats(self, user_id: str, amount: float):
        """Update user's investment statistics"""
        try:
            # Get current stats
            stats = await self.db.get_document("user_investment_stats", {"user_id": user_id})
            
            if stats:
                # Update existing stats
                await self.db.update_document("user_investment_stats", {"user_id": user_id}, {
                    "$inc": {
                        "total_invested": amount,
                        "total_investments": 1
                    },
                    "$set": {
                        "last_investment_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                })
            else:
                # Create new stats
                stats_data = {
                    "user_id": user_id,
                    "total_invested": amount,
                    "total_investments": 1,
                    "first_investment_date": datetime.utcnow(),
                    "last_investment_date": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await self.db.insert_document("user_investment_stats", stats_data)
                
        except Exception as e:
            print(f"Warning: Failed to update investment stats: {e}")
    
    async def get_user_invoices(self, user_id: str) -> List[InvestmentInvoice]:
        """Get all investment invoices for a user"""
        try:
            invoices_data = await self.db.get_documents("investment_invoices", {"user_id": user_id})
            print(invoices_data)
            return [InvestmentInvoice(**invoice) for invoice in invoices_data]
        except Exception as e:
            raise Exception(f"Failed to get user invoices: {str(e)}")

    async def send_eth_to_escrow(amount_eth: float) -> str:
        try:
            nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

            tx = {
                "to": ESCROW_ADDRESS,
                "value": w3.to_wei(amount_eth, "ether"),
                "gas": 21000,
                "gasPrice": w3.eth.gas_price,
                "nonce": nonce,
                "chainId": settings.chain_id
            }

            signed_tx = w3.eth.account.sign_transaction(tx, private_key=SENDER_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return w3.to_hex(tx_hash)

        except Exception as e:
            raise Exception(f"ETH transfer failed: {str(e)}")
        
    async def invest_entire_wallet_balance(self, user_id: str) -> bool:
        try:
            wallet = await wallet_service.get_wallet_by_user_id(user_id)
            if not wallet or wallet.fiat_balance <= 0:
                raise Exception("No INR balance available to invest")

            inr_balance = wallet.fiat_balance

            eth_amount = self._calculate_crypto_amount(inr_balance, "ETH")
            if eth_amount <= 0:
                raise Exception("ETH amount calculated is too low")

            sender_private_key = wallet.private_key
            sender_address = Web3.to_checksum_address(wallet.wallet_address)

            nonce = w3.eth.get_transaction_count(sender_address)

            tx = {
                "to": ESCROW_ADDRESS,
                "value": w3.to_wei(eth_amount, "ether"),
                "gas": 21000,
                "gasPrice": w3.eth.gas_price,
                "nonce": nonce,
                "chainId": settings.chain_id
            }

            signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = w3.to_hex(tx_hash)

            await wallet_service.update_fiat_balance(user_id, -inr_balance)
            await wallet_service.update_crypto_balance(user_id, "ETH", eth_amount)
            await self._update_user_investment_stats(user_id, inr_balance)

            await self.db.insert_document("portfolio_performance", {
                "user_id": user_id,
                "strategy_id": None,
                "investment_amount": inr_balance,
                "crypto_tokens": ["ETH"],
                "allocation": {"ETH": 100},
                "execution_date": datetime.utcnow(),
                "tx_hash": tx_hash,
                "created_at": datetime.utcnow()
            })

            return True

        except Exception as e:
            raise Exception(f"Failed to invest entire balance into ETH: {str(e)}")


# Global service instance
investment_strategy_service = InvestmentStrategyService() 