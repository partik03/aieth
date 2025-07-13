"""
Mock database service for testing without MongoDB
"""

import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


class MockDatabaseService:
    """Mock database service using in-memory storage"""
    
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "aadhaar_verifications": [],
            "upi_payments": [],
            "escrow_deposits": [],
            "salary_records": [],
            "investment_strategies": [],
            "wallets": []
        }
        print("🗄️  Using Mock Database Service")
    
    async def connect(self):
        """Mock connection - always succeeds"""
        print("✅ Connected to Mock Database")
        await asyncio.sleep(0.1)  # Simulate connection delay
    
    async def disconnect(self):
        """Mock disconnection"""
        print("🔌 Disconnected from Mock Database")
    
    def get_database(self):
        """Get the mock database instance"""
        return self
    
    def get_collection(self, collection_name: str):
        """Get a mock collection instance"""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        return MockCollection(self.collections[collection_name])
    
    async def insert_document(self, collection_name: str, document: dict):
        """Insert a document into a collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        
        # Add ID and timestamps
        document["_id"] = str(uuid.uuid4())
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        
        self.collections[collection_name].append(document)
        return document["_id"]
    
    async def get_document(self, collection_name: str, filter_query: dict):
        """Get a single document from a collection"""
        if collection_name not in self.collections:
            return None
        
        for doc in self.collections[collection_name]:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                return doc.copy()
        return None
    
    async def get_documents(self, collection_name: str, filter_query: dict = None):
        """Get multiple documents from a collection"""
        if collection_name not in self.collections:
            return []
        
        if filter_query is None:
            return [doc.copy() for doc in self.collections[collection_name]]
        
        documents = []
        for doc in self.collections[collection_name]:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                documents.append(doc.copy())
        return documents
    
    async def update_document(self, collection_name: str, filter_query: dict, update_data: dict):
        """Update a document in a collection"""
        if collection_name not in self.collections:
            return False
        
        for doc in self.collections[collection_name]:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                doc.update(update_data)
                doc["updated_at"] = datetime.utcnow()
                return True
        return False
    
    async def delete_document(self, collection_name: str, filter_query: dict):
        """Delete a document from a collection"""
        if collection_name not in self.collections:
            return False
        
        for i, doc in enumerate(self.collections[collection_name]):
            if all(doc.get(k) == v for k, v in filter_query.items()):
                del self.collections[collection_name][i]
                return True
        return False
    
    async def delete_documents(self, collection_name: str, filter_query: dict):
        """Delete multiple documents from a collection"""
        if collection_name not in self.collections:
            return 0
        
        deleted_count = 0
        indices_to_delete = []
        
        for i, doc in enumerate(self.collections[collection_name]):
            if all(doc.get(k) == v for k, v in filter_query.items()):
                indices_to_delete.append(i)
        
        for i in reversed(indices_to_delete):
            del self.collections[collection_name][i]
            deleted_count += 1
        
        return deleted_count


class MockCollection:
    """Mock collection class"""
    
    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents
    
    async def insert_one(self, document: dict):
        """Insert one document"""
        document["_id"] = str(uuid.uuid4())
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        self.documents.append(document)
        return MockInsertResult(document["_id"])
    
    async def find_one(self, filter_query: dict):
        """Find one document"""
        for doc in self.documents:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                return doc.copy()
        return None
    
    async def find(self, filter_query: dict = None):
        """Find documents"""
        if filter_query is None:
            return MockCursor([doc.copy() for doc in self.documents])
        
        documents = []
        for doc in self.documents:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                documents.append(doc.copy())
        return MockCursor(documents)
    
    async def update_one(self, filter_query: dict, update_data: dict):
        """Update one document"""
        for doc in self.documents:
            if all(doc.get(k) == v for k, v in filter_query.items()):
                doc.update(update_data["$set"])
                doc["updated_at"] = datetime.utcnow()
                return MockUpdateResult(1)
        return MockUpdateResult(0)
    
    async def delete_one(self, filter_query: dict):
        """Delete one document"""
        for i, doc in enumerate(self.documents):
            if all(doc.get(k) == v for k, v in filter_query.items()):
                del self.documents[i]
                return MockDeleteResult(1)
        return MockDeleteResult(0)


class MockInsertResult:
    """Mock insert result"""
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class MockUpdateResult:
    """Mock update result"""
    def __init__(self, modified_count: int):
        self.modified_count = modified_count


class MockDeleteResult:
    """Mock delete result"""
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class MockCursor:
    """Mock cursor"""
    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents
    
    async def to_list(self, length: Optional[int] = None):
        """Convert cursor to list"""
        if length is None:
            return self.documents
        return self.documents[:length]


# Global mock database service instance
mock_db_service = MockDatabaseService() 