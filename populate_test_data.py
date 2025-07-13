"""
Script to populate test data for the real database
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.db import db_service
from src.services.wallet_service import wallet_service
from src.services.mock_upi_data import mock_upi_data_service


async def populate_test_data():
    """Populate test data for the real database"""
    print("📊 Populating test data for real database...")
    
    # Test user ID (matches the hardcoded user in chat)
    test_user_id = "test_user_111111111111"
    
    try:
        # 1. Create a test wallet with initial balance
        wallet = await wallet_service.ensure_wallet_exists(test_user_id)
        print(f"✅ Created/verified wallet for user {test_user_id}")
        
        # 2. Generate mock UPI transactions and save to database
        mock_transactions = mock_upi_data_service.generate_mock_transactions(
            test_user_id, 
            days=90, 
            min_transactions=50,
            max_transactions=150
        )
        
        # Save transactions to database
        for transaction in mock_transactions:
            transaction_doc = {
                "user_id": test_user_id,
                "upi_id": "test@upi",
                "transaction_type": transaction["transaction_type"],
                "amount": transaction["amount"],
                "merchant": transaction["merchant"],
                "category": transaction["category"],
                "date": transaction["date"],
                "description": transaction["description"],
                "created_at": datetime.utcnow()
            }
            
            await db_service.insert_document("upi_transactions", transaction_doc)
        
        print(f"✅ Created {len(mock_transactions)} mock UPI transactions")
        
        # 3. Create some salary records
        salary_records = [
            {
                "user_id": test_user_id,
                "amount": 50000,
                "employer": "Tech Corp",
                "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "created_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "user_id": test_user_id,
                "amount": 52000,
                "employer": "Tech Corp", 
                "date": (datetime.utcnow() - timedelta(days=60)).isoformat(),
                "created_at": datetime.utcnow() - timedelta(days=60)
            }
        ]
        
        for salary in salary_records:
            await db_service.insert_document("salary_records", salary)
        
        print(f"✅ Created {len(salary_records)} salary records")
        
        # 4. Create some investment strategies
        strategies = [
            {
                "user_id": test_user_id,
                "name": "Conservative DCA Strategy",
                "description": "Dollar Cost Averaging with conservative allocation",
                "strategy_type": "dollar_cost_averaging",
                "trigger_type": "weekly",
                "amount": 5000,
                "percentage": 10,
                "crypto_tokens": ["BTC", "ETH", "USDT"],
                "allocation": {"BTC": 50, "ETH": 30, "USDT": 20},
                "risk_level": "low",
                "max_investment": 10000,
                "min_investment": 1000,
                "is_active": True,
                "is_approved": True,
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "user_id": test_user_id,
                "name": "Aggressive Growth Strategy",
                "description": "High-risk strategy for maximum growth potential",
                "strategy_type": "market_dip",
                "trigger_type": "market_dip",
                "amount": 10000,
                "percentage": None,
                "crypto_tokens": ["BTC", "ETH", "SOL", "MATIC", "DOGE"],
                "allocation": {"BTC": 30, "ETH": 30, "SOL": 20, "MATIC": 15, "DOGE": 5},
                "risk_level": "high",
                "max_investment": 20000,
                "min_investment": 5000,
                "is_active": True,
                "is_approved": False,
                "created_at": datetime.utcnow() - timedelta(days=7),
                "updated_at": datetime.utcnow() - timedelta(days=7)
            }
        ]
        
        for strategy in strategies:
            await db_service.insert_document("investment_strategies", strategy)
        
        print(f"✅ Created {len(strategies)} investment strategies")
        
        # 5. Create some investment invoices
        invoices = [
            {
                "user_id": test_user_id,
                "strategy_id": strategies[0]["_id"] if "_id" in strategies[0] else "strategy_1",
                "amount": 5000,
                "crypto_tokens": ["BTC", "ETH", "USDT"],
                "allocation": {"BTC": 50, "ETH": 30, "USDT": 20},
                "reason": "Weekly DCA trigger activated",
                "status": "executed",
                "payment_status": "paid",
                "created_at": datetime.utcnow() - timedelta(days=7),
                "expires_at": datetime.utcnow() - timedelta(days=6),
                "paid_at": datetime.utcnow() - timedelta(days=6),
                "executed_at": datetime.utcnow() - timedelta(days=6)
            }
        ]
        
        for invoice in invoices:
            await db_service.insert_document("investment_invoices", invoice)
        
        print(f"✅ Created {len(invoices)} investment invoices")
        
        print("🎉 Test data population completed successfully!")
        print(f"📊 User ID: {test_user_id}")
        print(f"💰 Wallet Address: {wallet.wallet_address}")
        print(f"💵 Initial Balance: ₹{wallet.fiat_balance:,.2f}")
        print(f"🪙 Crypto Balance: {wallet.crypto_balance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating test data: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(populate_test_data()) 