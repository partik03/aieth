"""
Tests for the ping endpoint
"""

import pytest
from fastapi.testclient import TestClient


def test_ping_endpoint(client: TestClient):
    """Test the ping endpoint returns correct response"""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"


def test_root_endpoint(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Crypto-UPI Backend API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running" 