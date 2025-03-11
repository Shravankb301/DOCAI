from fastapi.testclient import TestClient
from app.main import app

# Create a test client with the correct syntax for FastAPI with httpx 0.24.0
client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Compliance Checker API"}

def test_upload_endpoint_no_data():
    """Test the upload endpoint with no data."""
    response = client.post("/api/upload")
    assert response.status_code == 400
    assert "Either file or text content must be provided" in response.text

def test_upload_endpoint_with_text():
    """Test the upload endpoint with text content."""
    response = client.post(
        "/api/upload",
        data={"text_content": "This is a test document for compliance analysis."}
    )
    assert response.status_code == 202
    assert "Document received and being processed" in response.text 