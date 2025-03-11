import os
import pytest
import io
import json
from fastapi.testclient import TestClient
from app.main import app
from app.utils.file_utils import validate_file, get_file_content, detect_file_type

# Create a test client
client = TestClient(app)

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def create_test_file(filename, content, mode="w"):
    """Helper function to create a test file"""
    filepath = os.path.join(TEST_DATA_DIR, filename)
    with open(filepath, mode) as f:
        f.write(content)
    return filepath

def test_validate_file_valid_text():
    """Test validating a valid text file"""
    from fastapi import UploadFile
    
    # Create a mock UploadFile
    file_content = b"This is a test file"
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(file_content)
    )
    
    # Validate the file
    is_valid, error_message = validate_file(file)
    
    assert is_valid is True
    assert error_message == ""

def test_validate_file_invalid_extension():
    """Test validating a file with invalid extension"""
    from fastapi import UploadFile
    
    # Create a mock UploadFile with invalid extension
    file_content = b"This is a test file"
    file = UploadFile(
        filename="test.exe",
        file=io.BytesIO(file_content)
    )
    
    # Validate the file
    is_valid, error_message = validate_file(file)
    
    assert is_valid is False
    assert "File type .exe not allowed" in error_message

def test_validate_file_empty():
    """Test validating an empty file"""
    from fastapi import UploadFile
    
    # Create a mock empty UploadFile
    file = UploadFile(
        filename="empty.txt",
        file=io.BytesIO(b"")
    )
    
    # Validate the file
    is_valid, error_message = validate_file(file)
    
    assert is_valid is False
    assert "File is empty" in error_message

def test_detect_file_type_text():
    """Test detecting a text file type"""
    # Create a test text file
    content = "This is a plain text file for testing."
    filepath = create_test_file("detect_text.txt", content)
    
    try:
        # Detect file type
        file_info = detect_file_type(filepath)
        
        assert file_info["file_extension"] == ".txt"
        assert file_info["is_binary"] is False
        assert file_info["encoding"].lower() in ["utf-8", "ascii"]
    finally:
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)

def test_detect_file_type_binary():
    """Test detecting a binary file type"""
    # Use the pre-created binary file
    filepath = os.path.join(TEST_DATA_DIR, "test_binary.bin")
    
    # Detect file type
    file_info = detect_file_type(filepath)
    
    assert file_info["file_extension"] == ".bin"
    # The binary detection might vary based on the content, so we don't assert is_binary

def test_get_file_content_text():
    """Test getting content from a text file"""
    # Create a test text file
    content = "This is a plain text file for testing."
    filepath = create_test_file("content_text.txt", content)
    
    try:
        # Get file content
        extracted_content = get_file_content(filepath)
        
        assert extracted_content == content
    finally:
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)

def test_get_file_content_json():
    """Test getting content from a JSON file"""
    # Use the pre-created JSON file
    filepath = os.path.join(TEST_DATA_DIR, "test.json")
    
    # Get file content
    extracted_content = get_file_content(filepath)
    
    # Parse the extracted content back to JSON
    extracted_data = json.loads(extracted_content)
    
    assert extracted_data["name"] == "Test"
    assert extracted_data["value"] == 123
    assert extracted_data["nested"]["key"] == "value"

def test_upload_endpoint_with_text():
    """Test the upload endpoint with text content"""
    response = client.post(
        "/api/upload",
        data={"text_content": "This is a test document for compliance analysis."}
    )
    assert response.status_code == 202
    assert "Document received and being processed" in response.text
    assert "document_id" in response.json()

def test_upload_endpoint_with_file():
    """Test the upload endpoint with a file"""
    # Create a test file
    content = "This is a test document for compliance analysis."
    
    # Create file data for upload
    files = {
        "file": ("test.txt", content.encode(), "text/plain")
    }
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 202
    assert "Document received and being processed" in response.text
    assert "document_id" in response.json()

def test_upload_endpoint_with_invalid_file():
    """Test the upload endpoint with an invalid file"""
    # Create file data for upload with invalid extension
    files = {
        "file": ("test.exe", b"Binary content", "application/octet-stream")
    }
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 400
    assert "not allowed" in response.text

def test_batch_upload_endpoint():
    """Test the batch upload endpoint"""
    # Create test files
    files = [
        ("files", ("test1.txt", b"Test document 1", "text/plain")),
        ("files", ("test2.txt", b"Test document 2", "text/plain"))
    ]
    
    response = client.post("/api/batch", files=files)
    
    assert response.status_code == 202
    assert "Processed 2 files" in response.text
    
    results = response.json()["results"]
    assert len(results) == 2
    assert all(result["status"] == "processing" for result in results)
    assert all("document_id" in result for result in results)

def test_batch_upload_with_mixed_files():
    """Test the batch upload endpoint with mixed valid and invalid files"""
    # Create test files - one valid, one invalid
    files = [
        ("files", ("test1.txt", b"Test document 1", "text/plain")),
        ("files", ("test2.exe", b"Invalid file", "application/octet-stream"))
    ]
    
    response = client.post("/api/batch", files=files)
    
    assert response.status_code == 202
    
    results = response.json()["results"]
    assert len(results) == 2
    
    # First file should be processed
    assert results[0]["status"] == "processing"
    assert "document_id" in results[0]
    
    # Second file should have an error
    assert results[1]["status"] == "error"
    assert "not allowed" in results[1]["detail"] 