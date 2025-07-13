"""
Script to create dummy test investment invoices
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import datetime as dt
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.db import db_service


async def create_test_invoices():
    """Create dummy test investment invoices"""
    print("📄 Creating dummy test investment invoices...")
    
    # User ID from the request
    user_id = "6872f4a6f0cdf587b2d8f06b"
    
    try:
        # Create test investment invoices
        test_invoices = [
            {
                "user_id": user_id,
                "strategy_id": "test_strategy_1",
                "amount": 5000.0,
                "crypto_tokens": ["BTC", "ETH", "USDT"],
                "allocation": {"BTC": 0.00000001, "ETH": 0.01, "USDT": 10},
                "reason": "Weekly DCA strategy triggered",
                "upi_string": "upi://pay?pa=investment@crypto-upi&pn=Crypto Investment&am=5000&tn=Weekly DCA Investment",
                "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "txn_ref": "TXN_WEEKLY_001",
                "status": "pending",
                "payment_status": "pending",
                "created_at": datetime.now(dt.UTC),
                "expires_at": datetime.now(dt.UTC) + timedelta(hours=24),
                "paid_at": None,
                "executed_at": None
            },
            {
                "user_id": user_id,
                "strategy_id": "test_strategy_2", 
                "amount": 10000.0,
                "crypto_tokens": ["BTC", "ETH", "SOL", "MATIC"],
                "allocation": {"BTC": 0.00000001, "ETH": 1, "SOL": 0.00000001, "MATIC": 0.00000001},
                "reason": "Market dip strategy triggered",
                "upi_string": "upi://pay?pa=investment@crypto-upi&pn=Crypto Investment&am=10000&tn=Market Dip Investment",
                "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "txn_ref": "TXN_MARKET_002",
                "status": "paid",
                "payment_status": "paid",
                "created_at": datetime.now() - timedelta(hours=2),
                "expires_at": datetime.now(dt.UTC) + timedelta(hours=22),
                "paid_at": datetime.now(dt.UTC) - timedelta(hours=1),
                "executed_at": None
            }
        ]
        
        # Insert invoices into database
        for i, invoice in enumerate(test_invoices, 1):
            invoice_id = await db_service.insert_document("investment_invoices", invoice)
            print(f"✅ Created invoice {i}: {invoice_id}")
            print(f"   Amount: ₹{invoice['amount']:,.2f}")
            print(f"   Status: {invoice['status']}")
            print(f"   Tokens: {', '.join(invoice['crypto_tokens'])}")
            print(f"   Reason: {invoice['reason']}")
            print()
        
        print("🎉 Test investment invoices created successfully!")
        print(f"📊 User ID: {user_id}")
        print(f"📄 Total invoices: {len(test_invoices)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test invoices: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(create_test_invoices()) 