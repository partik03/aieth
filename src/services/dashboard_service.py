"""
Dashboard service for aggregating user data and providing summary information
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.services.db import db_service


class DashboardService:
    """Service for aggregating dashboard data"""
    
    async def get_wallet_balances(self, user_id: str) -> Dict[str, float]:
        """Get wallet balances for a user"""
        try:
            # Ensure wallet exists
            from src.services.wallet_service import wallet_service
            wallet = await wallet_service.ensure_wallet_exists(user_id)
            
            balances = {
                "INR": wallet.fiat_balance
            }
            
            # Add crypto balances
            for token, balance in wallet.crypto_balance.items():
                if balance > 0:
                    balances[token] = balance
            
            return balances
            
        except Exception as e:
            print(f"Error getting wallet balances: {e}")
            return {"INR": 0.0}
    
    async def get_last_salary_investment(self, user_id: str) -> Optional[Dict]:
        """Get the latest salary investment strategy"""
        try:
            # Get the most recent investment strategy for the user
            strategies = await db_service.get_documents(
                "investment_strategies",
                {"user_id": user_id}
            )
            
            if not strategies:
                return None
            
            # Sort by generated_at and get the latest
            strategies.sort(key=lambda x: x.get("generated_at", datetime.min), reverse=True)
            latest_strategy = strategies[0]
            
            # Get the associated salary record
            salary = await db_service.get_document(
                "salaries",
                {"_id": latest_strategy.get("salary_id")}
            )
            
            if not salary:
                return None
            
            return {
                "amount": salary.get("amount", 0),
                "tokens": latest_strategy.get("strategy", {}),
                "date": salary.get("date", ""),
                "risk_level": latest_strategy.get("risk_level", ""),
                "expected_return": latest_strategy.get("expected_return", "")
            }
            
        except Exception as e:
            print(f"Error getting last salary investment: {e}")
            return None
    
    async def get_recent_transactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions (UPI payments, crypto transfers)"""
        try:
            transactions = []
            
            # Get recent UPI payments
            upi_payments = await db_service.get_documents(
                "upi_payments",
                {"user_id": user_id}
            )
            
            # Sort by created_at and get recent ones
            upi_payments.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            
            for payment in upi_payments[:limit//2]:  # Half for UPI payments
                transactions.append({
                    "type": "upi_payment",
                    "amount": payment.get("amount", 0),
                    "txn_ref": payment.get("txn_ref", ""),
                    "status": payment.get("status", ""),
                    "date": payment.get("created_at", "").isoformat() if payment.get("created_at") else "",
                    "direction": "out"
                })
            
            # Get recent crypto transactions (mock for now)
            # In a real system, you'd have a transactions collection
            mock_crypto_txs = await self._get_mock_crypto_transactions(user_id, limit//2)
            transactions.extend(mock_crypto_txs)
            
            # Sort all transactions by date
            transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            return transactions[:limit]
            
        except Exception as e:
            print(f"Error getting recent transactions: {e}")
            return []
    
    async def _get_mock_crypto_transactions(self, user_id: str, limit: int) -> List[Dict]:
        """Get mock crypto transactions for demonstration"""
        # In a real system, this would query a transactions collection
        # For now, we'll create some mock data based on escrow activity
        
        escrow_deposits = await db_service.get_documents(
            "escrow_deposits",
            {"user_id": user_id}
        )
        
        transactions = []
        for deposit in escrow_deposits[:limit]:
            if deposit.get("status") == "confirmed":
                transactions.append({
                    "type": "crypto_receive",
                    "token": deposit.get("token_symbol", "ETH"),
                    "amount": deposit.get("amount", 0),
                    "from": "escrow_deposit",
                    "date": deposit.get("confirmed_at", "").isoformat() if deposit.get("confirmed_at") else "",
                    "direction": "in"
                })
        
        return transactions
    
    async def get_escrow_activity(self, user_id: str) -> Dict[str, float]:
        """Get escrow activity summary"""
        try:
            # Get all escrow deposits for the user
            escrow_deposits = await db_service.get_documents(
                "escrow_deposits",
                {"user_id": user_id}
            )
            
            deposited = 0.0
            purchased = 0.0
            
            for deposit in escrow_deposits:
                amount = deposit.get("amount", 0)
                status = deposit.get("status", "")
                
                if status in ["confirmed", "released"]:
                    deposited += amount
                
                if status == "released" and deposit.get("buyer_id") == user_id:
                    purchased += amount
            
            return {
                "deposited": deposited,
                "purchased": purchased,
                "pending": sum(d.get("amount", 0) for d in escrow_deposits if d.get("status") == "pending")
            }
            
        except Exception as e:
            print(f"Error getting escrow activity: {e}")
            return {"deposited": 0.0, "purchased": 0.0, "pending": 0.0}
    
    async def get_investment_performance(self, user_id: str) -> Dict:
        """Get investment performance summary"""
        try:
            strategies = await db_service.get_documents(
                "investment_strategies",
                {"user_id": user_id}
            )
            
            if not strategies:
                return {
                    "total_investments": 0,
                    "strategies_count": 0,
                    "avg_risk_level": "N/A",
                    "latest_strategy_date": None
                }
            
            total_investments = sum(
                strategy.get("strategy", {}).values() 
                for strategy in strategies
            )
            
            risk_levels = [s.get("risk_level", "") for s in strategies if s.get("risk_level")]
            avg_risk = max(set(risk_levels), key=risk_levels.count) if risk_levels else "N/A"
            
            latest_date = max(
                (s.get("generated_at", datetime.min) for s in strategies),
                default=None
            )
            
            return {
                "total_investments": total_investments,
                "strategies_count": len(strategies),
                "avg_risk_level": avg_risk,
                "latest_strategy_date": latest_date.isoformat() if latest_date else None
            }
            
        except Exception as e:
            print(f"Error getting investment performance: {e}")
            return {
                "total_investments": 0,
                "strategies_count": 0,
                "avg_risk_level": "N/A",
                "latest_strategy_date": None
            }
    
    async def get_dashboard_summary(self, user_id: str) -> Dict:
        """Get complete dashboard summary for a user"""
        try:
            # Get all data in parallel
            balances = await self.get_wallet_balances(user_id)
            last_investment = await self.get_last_salary_investment(user_id)
            recent_transactions = await self.get_recent_transactions(user_id, 10)
            escrow_activity = await self.get_escrow_activity(user_id)
            investment_performance = await self.get_investment_performance(user_id)
            
            return {
                "user_id": user_id,
                "wallet_balances": balances,
                "last_salary_investment": last_investment,
                "recent_transactions": recent_transactions,
                "escrow_activity": escrow_activity,
                "investment_performance": investment_performance,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return {
                "user_id": user_id,
                "wallet_balances": {"INR": 0.0},
                "last_salary_investment": None,
                "recent_transactions": [],
                "escrow_activity": {"deposited": 0.0, "purchased": 0.0, "pending": 0.0},
                "investment_performance": {
                    "total_investments": 0,
                    "strategies_count": 0,
                    "avg_risk_level": "N/A",
                    "latest_strategy_date": None
                },
                "last_updated": datetime.utcnow().isoformat()
            }


# Global dashboard service instance
dashboard_service = DashboardService() 