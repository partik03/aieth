#!/usr/bin/env python3
"""
Test script for Finance Agent with Mock UPI Data
"""

import os
import asyncio
import json
from datetime import datetime

# Set up test environment variables
os.environ.update({
    "MONGO_URI": "mongodb+srv://hs05june:1234567890@cluster0.xpqjxvh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "DB_NAME": "test_db",
    "SECRET_KEY": "test_secret_key_12345",
    "OPENAI_API_KEY": "test_openai_key",
    "UPI_GATEWAY_API_KEY": "test_upi_key",
    "UPI_GATEWAY_SECRET": "test_upi_secret",
    "ETHEREUM_RPC_URL": "https://eth-mainnet.alchemyapi.io/v2/test",
    "POLYGON_RPC_URL": "https://polygon-mainnet.alchemyapi.io/v2/test",
    "PRIVATE_KEY": "test_private_key",
    "TWITTER_API_KEY": "test_twitter_key",
    "TWITTER_API_SECRET": "test_twitter_secret",
    "UPI_MERCHANT_ID": "test_merchant",
    "UPI_APP_ID": "test_app_id",
    "UPI_CALLBACK_URL": "http://localhost:8000/callback",
    "DIGILOCKER_CLIENT_ID": "test_digilocker_id",
    "DIGILOCKER_CLIENT_SECRET": "test_digilocker_secret",
    "DIGILOCKER_REDIRECT_URI": "http://localhost:8000/digilocker/callback",
    "DIGILOCKER_BASE_URL": "https://api.digitallocker.gov.in",
    "ESCROW_WALLET_ADDRESS": "0x1234567890123456789012345678901234567890",
    "ESCROW_PRIVATE_KEY": "test_escrow_key"
})

# Now import the services
from src.services.finance_agent import finance_agent_service
from src.services.mock_upi_data import mock_upi_data_service
from src.services.nlp_service import nlp_service


async def test_finance_agent():
    """Test the finance agent functionality"""
    print("🚀 Testing Finance Agent with Mock UPI Data")
    print("=" * 50)
    
    # Test user ID
    user_id = "test_user_123"
    
    # 1. Generate mock transactions
    print("\n📊 1. Generating Mock UPI Transactions...")
    transactions = mock_upi_data_service.generate_mock_transactions(
        user_id, 
        days=90, 
        min_transactions=50,
        max_transactions=100
    )
    print(f"✅ Generated {len(transactions)} transactions")
    
    # 2. Get transaction summary
    print("\n📋 2. Transaction Summary...")
    summary = mock_upi_data_service.get_transaction_summary(transactions)
    print(f"Total Amount: ₹{summary.get('total_amount', 0):,.2f}")
    print(f"Total Transactions: {summary.get('total_transactions', 0)}")
    print(f"Net Amount: ₹{summary.get('net_amount', 0):,.2f}")
    
    # 3. Test AI analysis (will use fallback due to no real Azure OpenAI)
    print("\n🤖 3. AI-Powered Transaction Analysis...")
    analysis_result = await finance_agent_service.analyze_transactions(user_id, transactions)
    
    if analysis_result.get("success"):
        analysis = analysis_result.get("analysis", {})
        print("✅ Analysis completed successfully!")
        print(f"Key Metrics: {analysis.get('key_metrics', {})}")
    else:
        print(f"❌ Analysis failed: {analysis_result.get('error')}")
    
    # 4. Test financial recommendations
    print("\n💡 4. Financial Recommendations...")
    if analysis_result.get("success"):
        recommendations_result = await finance_agent_service.get_financial_recommendations(
            user_id, analysis_result.get("analysis", {})
        )
        
        if recommendations_result.get("success"):
            print("✅ Recommendations generated successfully!")
            print("Recommendations preview:")
            recommendations = recommendations_result.get("recommendations", "")
            print(recommendations[:200] + "..." if len(recommendations) > 200 else recommendations)
        else:
            print(f"❌ Recommendations failed: {recommendations_result.get('error')}")
    
    # 5. Test NLP integration
    print("\n💬 5. Testing NLP Integration...")
    
    # Test different NLP commands
    test_messages = [
        "analyze my transactions",
        "give me financial insights",
        "show me transaction summary",
        "help"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = await nlp_service.process_nlp_message(message, user_id)
        print(f"AI: {response[:150]}..." if len(response) > 150 else f"AI: {response}")
    
    # 6. Export sample data
    print("\n📁 6. Exporting Sample Data...")
    json_data = mock_upi_data_service.export_transactions_to_json(transactions[:10])
    print(f"✅ Exported {len(transactions[:10])} sample transactions to JSON")
    print("Sample transaction structure:")
    sample_transaction = transactions[0] if transactions else {}
    print(json.dumps(sample_transaction, indent=2, default=str))
    
    print("\n🎉 Finance Agent Testing Complete!")
    print("=" * 50)


async def test_specific_features():
    """Test specific features"""
    print("\n🔧 Testing Specific Features")
    print("=" * 30)
    
    user_id = "feature_test_user"
    
    # Test category filtering
    print("\n🏷️ Category Filtering...")
    transactions = mock_upi_data_service.get_user_transactions(user_id, days=30)
    food_transactions = mock_upi_data_service.get_transactions_by_category(transactions, "Food & Dining")
    print(f"Food & Dining transactions: {len(food_transactions)}")
    
    # Test date range filtering
    print("\n📅 Date Range Filtering...")
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_transactions = mock_upi_data_service.get_transactions_by_date_range(
        transactions, start_date, end_date
    )
    print(f"Transactions in last 7 days: {len(recent_transactions)}")
    
    # Test different time periods
    print("\n⏰ Different Time Periods...")
    periods = [30, 60, 90]
    for days in periods:
        period_transactions = mock_upi_data_service.get_user_transactions(user_id, days=days)
        summary = mock_upi_data_service.get_transaction_summary(period_transactions)
        print(f"Last {days} days: ₹{summary.get('total_amount', 0):,.2f} ({summary.get('total_transactions', 0)} transactions)")


if __name__ == "__main__":
    print("🧪 Finance Agent Test Suite")
    print("This script tests the finance agent with mock UPI data")
    print("Note: Azure OpenAI calls will use fallback responses in test mode")
    print()
    
    # Run tests
    asyncio.run(test_finance_agent())
    asyncio.run(test_specific_features()) 