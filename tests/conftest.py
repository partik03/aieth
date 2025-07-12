"""
Pytest configuration and common fixtures
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient

from run import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User",
        "phone": "+919876543210",
        "user_type": "indian"
    }


@pytest.fixture
def sample_crypto_data():
    """Sample crypto transaction data for testing"""
    return {
        "crypto_type": "BTC",
        "amount": 0.001,
        "price_inr": 45000
    }


@pytest.fixture
def sample_upi_data():
    """Sample UPI payment data for testing"""
    return {
        "amount": 1000,
        "upi_id": "test@upi",
        "description": "Test payment"
    } 