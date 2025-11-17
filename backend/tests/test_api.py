"""
Basic API endpoint tests for TrendKe backend
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "TrendKe API" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "message" in data


def test_docs_endpoint():
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


def test_invalid_endpoint():
    """Test 404 for non-existent endpoint"""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
