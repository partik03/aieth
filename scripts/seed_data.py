"""
Data seeding script for development and testing
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config.settings import get_settings


async def seed_sample_data():
    """Seed the database with sample data"""
    
    settings = get_settings()
    
    print("🌱 Seeding sample data...")
    
    # Sample data will be added when models are implemented
    sample_data = {
        "users": [
            {
                "email": "user1@example.com",
                "name": "John Doe",
                "user_type": "indian",
                "phone": "+919876543210"
            },
            {
                "email": "user2@example.com", 
                "name": "Jane Smith",
                "user_type": "international",
                "phone": "+1234567890"
            }
        ],
        "crypto_prices": {
            "BTC": 45000,
            "ETH": 3000,
            "MATIC": 1.5,
            "USDT": 1.0,
            "USDC": 1.0
        }
    }
    
    print("📊 Sample data structure created")
    print("ℹ️  Data will be inserted when models are implemented")
    
    return True


if __name__ == "__main__":
    print("🚀 Starting data seeding...")
    success = asyncio.run(seed_sample_data())
    
    if success:
        print("✅ Data seeding completed successfully!")
    else:
        print("❌ Data seeding failed!")
        sys.exit(1) 