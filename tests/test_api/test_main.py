"""
Tests for main application endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Crypto-UPI Backend API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_docs_endpoint(client: TestClient):
    """Test that docs endpoint is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint(client: TestClient):
    """Test that redoc endpoint is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200 