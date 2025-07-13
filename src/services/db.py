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
        print( "get_collection", self.database)
        if self.database is None:
            return None
        return self.database[collection_name]
    
    async def insert_document(self, collection_name: str, document: dict):
        """Insert a document into a collection"""

        collection = self.get_collection(collection_name)
        print( "insert_document", collection)
        if self.database is None:
            print("Database is None")
            await self.connect()
            collection = self.database[collection_name]
            print(self.database, collection)
        print(collection)
        if collection is None:
            print(f"Collection {collection_name} not found")
            collection = self.database[collection_name]
            return None
        
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    
    async def get_document(self, collection_name: str, filter_query: dict):
        """Get a single document from a collection"""
        collection = self.get_collection(collection_name)
        document = await collection.find_one(filter_query)
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def get_documents(self, collection_name: str, filter_query: dict = None):
        """Get multiple documents from a collection"""
        collection = self.get_collection(collection_name)
        if filter_query is None:
            filter_query = {}
        
        cursor = collection.find(filter_query)
        documents = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def update_document(self, collection_name: str, filter_query: dict, update_data: dict):
        """Update a document in a collection"""
        collection = self.get_collection(collection_name)
        result = await collection.update_one(filter_query, {"$set": update_data})
        return result.modified_count > 0
    
    async def delete_document(self, collection_name: str, filter_query: dict):
        """Delete a document from a collection"""
        collection = self.get_collection(collection_name)
        result = await collection.delete_one(filter_query)
        return result.deleted_count > 0
    
    async def delete_documents(self, collection_name: str, filter_query: dict):
        """Delete multiple documents from a collection"""
        collection = self.get_collection(collection_name)
        result = await collection.delete_many(filter_query)
        return result.deleted_count


# Global database service instance
db_service = DatabaseService()


async def get_database():
    """Dependency to get database instance"""
    return db_service.get_database()


async def get_collection(collection_name: str):
    """Dependency to get collection instance"""
    return db_service.get_collection(collection_name) 