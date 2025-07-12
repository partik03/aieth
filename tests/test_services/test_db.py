"""
Tests for database connection service
"""

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from src.services.db import DatabaseService


@pytest.mark.asyncio
async def test_database_service_creation():
    """Test that DatabaseService can be created"""
    db_service = DatabaseService()
    assert db_service.client is None
    assert db_service.database is None
    assert db_service.settings is not None


@pytest.mark.asyncio
async def test_database_service_methods():
    """Test DatabaseService methods"""
    db_service = DatabaseService()
    
    # Test get_database before connection
    assert db_service.get_database() is None
    
    # Test get_collection before connection (should not raise error)
    collection = db_service.get_collection("test")
    assert collection is not None


def test_global_db_service():
    """Test that global db_service is available"""
    from src.services.db import db_service
    assert db_service is not None
    assert isinstance(db_service, DatabaseService) 