"""
Database initialization script
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine, text
from src.config.settings import get_settings


async def init_database():
    """Initialize the database with tables"""
    
    settings = get_settings()
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create tables (will be implemented when models are created)
        print("📋 Database initialization completed")
        print("ℹ️  Tables will be created when models are implemented")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Initializing database...")
    success = asyncio.run(init_database())
    
    if success:
        print("✅ Database setup completed successfully!")
    else:
        print("❌ Database setup failed!")
        sys.exit(1) 