"""
Script to create investment invoices for specific user using the service
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.investment_strategy_service import investment_strategy_service
from src.models.investment_strategy import InvestmentStrategy, StrategyType, TriggerType, StrategyCreateRequest


async def create_invoices_for_user():
    """Create investment invoices for the specific user"""
    print("📄 Creating investment invoices for user...")
    
    # User ID from the request
    user_id = "6872f4a6f0cdf587b2d8f06b"
    
    try:
        # First, let's create a test strategy for this user
        strategy_data = StrategyCreateRequest(
            name="Test Weekly DCA Strategy",
            description="Test strategy for creating invoices",
            strategy_type=StrategyType.DCA,
            trigger_type=TriggerType.WEEKLY,
            amount=5000.0,
            percentage=10,
            crypto_tokens=["BTC", "ETH", "USDT"],
            allocation={"BTC": 50, "ETH": 30, "USDT": 20},
            risk_level="medium",
            max_investment=10000,
            min_investment=1000
        )
        
        # Create the strategy
        strategy = await investment_strategy_service.create_strategy(user_id, strategy_data)
        print(f"✅ Created strategy: {strategy.name}")
        
        # Now create invoices for this strategy
        invoice1 = await investment_strategy_service.generate_investment_invoice(
            strategy, 
            "Weekly DCA strategy triggered"
        )
        print(f"✅ Created invoice 1: {invoice1.id}")
        print(f"   Amount: ₹{invoice1.amount:,.2f}")
        print(f"   Status: {invoice1.status}")
        
        # Create a second invoice with different parameters
        strategy2_data = StrategyCreateRequest(
            name="Test Market Dip Strategy",
            description="Test market dip strategy",
            strategy_type=StrategyType.MARKET_DIP,
            trigger_type=TriggerType.MARKET_DIP,
            amount=10000.0,
            percentage=None,
            crypto_tokens=["BTC", "ETH", "SOL", "MATIC"],
            allocation={"BTC": 40, "ETH": 35, "SOL": 15, "MATIC": 10},
            risk_level="high",
            max_investment=20000,
            min_investment=5000
        )
        
        strategy2 = await investment_strategy_service.create_strategy(user_id, strategy2_data)
        print(f"✅ Created strategy 2: {strategy2.name}")
        
        invoice2 = await investment_strategy_service.generate_investment_invoice(
            strategy2,
            "Market dip strategy triggered"
        )
        print(f"✅ Created invoice 2: {invoice2.id}")
        print(f"   Amount: ₹{invoice2.amount:,.2f}")
        print(f"   Status: {invoice2.status}")
        
        print("\n🎉 Investment invoices created successfully!")
        print(f"📊 User ID: {user_id}")
        print(f"📄 Total invoices: 2")
        print(f"📋 Total strategies: 2")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating invoices: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(create_invoices_for_user()) 