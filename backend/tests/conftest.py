"""
Test configuration and fixtures
"""
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }

@pytest.fixture
def test_video_data():
    """Sample video data for testing"""
    return {
        "title": "Test Video",
        "description": "This is a test video",
        "hashtags": ["test", "demo"]
    }
