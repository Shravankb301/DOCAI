"""Pytest configuration for backend tests."""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before running tests."""
    # Set environment variables for testing
    os.environ["TESTING"] = "True"
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
    
    # Setup code here
    yield
    # Teardown code here 