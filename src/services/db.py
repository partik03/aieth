"""
MongoDB connection service using motor for async operations
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from src.config.settings import get_settings


class DatabaseService:
    """MongoDB database service for async operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.settings = get_settings()
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.settings.mongo_uri)
            self.database = self.client[self.settings.db_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.settings.mongo_uri}")
            print(f"📊 Using database: {self.settings.db_name}")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    def get_database(self):
        """Get the database instance"""
        return self.database
    
    def get_collection(self, collection_name: str):
        """Get a collection instance"""
        return self.database[collection_name]


# Global database service instance
db_service = DatabaseService()


async def get_database():
    """Dependency to get database instance"""
    return db_service.get_database()


async def get_collection(collection_name: str):
    """Dependency to get collection instance"""
    return db_service.get_collection(collection_name) 