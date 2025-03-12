import pytest
import pytest_asyncio
from fastapi import FastAPI
import httpx
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the app after modifying the path
from app.main import app

pytestmark = pytest.mark.asyncio

# Create a test client
@pytest.fixture
async def client():
    """Create a test client using HTTPX AsyncClient with ASGITransport."""
    transport = httpx.ASGITransport(app=app)
    base_url = "http://testserver"
    async with httpx.AsyncClient(transport=transport, base_url=base_url) as client:
        yield client

@pytest.mark.asyncio
async def test_read_root(client):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Compliance Checker API"}

@pytest.mark.asyncio
async def test_upload_endpoint_no_data(client):
    """Test the upload endpoint with no data."""
    response = await client.post("/api/upload")
    assert response.status_code == 400
    assert "Either file or text content must be provided" in response.text

@pytest.mark.asyncio
async def test_upload_endpoint_with_text(client):
    """Test the upload endpoint with text content."""
    response = await client.post(
        "/api/upload/json",
        json={"text_content": "This is a test document for compliance analysis."}
    )
    assert response.status_code == 202
    assert "Document received and being processed" in response.text 