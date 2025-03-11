import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the app after modifying the path
from app.main import app

# Create a test client
@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Compliance Checker API"}

def test_upload_endpoint_no_data(client):
    """Test the upload endpoint with no data."""
    response = client.post("/api/upload")
    assert response.status_code == 400
    assert "Either file or text content must be provided" in response.text

def test_upload_endpoint_with_text(client):
    """Test the upload endpoint with text content."""
    response = client.post(
        "/api/upload/json",
        json={"text_content": "This is a test document for compliance analysis."}
    )
    assert response.status_code == 202
    assert "Document received and being processed" in response.text 