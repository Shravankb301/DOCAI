import os
import io
import json
from app.utils.file_utils import detect_file_type, get_file_content, validate_file
from fastapi import UploadFile

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "tests", "data")

def create_test_file(filename, content, mode="w"):
    """Helper function to create a test file"""
    filepath = os.path.join(TEST_DATA_DIR, filename)
    with open(filepath, mode) as f:
        f.write(content)
    return filepath

def test_validate_file():
    """Test validating files"""
    print("\nTesting validate_file...")
    
    # Test valid text file
    file_content = b"This is a test file"
    file = UploadFile(
        filename="test.txt",
        file=io.BytesIO(file_content)
    )
    is_valid, error_message = validate_file(file)
    print(f"Valid text file: is_valid={is_valid}, error_message='{error_message}'")
    assert is_valid is True
    assert error_message == ""
    
    # Test invalid extension
    file = UploadFile(
        filename="test.exe",
        file=io.BytesIO(file_content)
    )
    is_valid, error_message = validate_file(file)
    print(f"Invalid extension: is_valid={is_valid}, error_message='{error_message}'")
    assert is_valid is False
    assert "File type .exe not allowed" in error_message
    
    # Test empty file
    file = UploadFile(
        filename="empty.txt",
        file=io.BytesIO(b"")
    )
    is_valid, error_message = validate_file(file)
    print(f"Empty file: is_valid={is_valid}, error_message='{error_message}'")
    assert is_valid is False
    assert "File is empty" in error_message
    
    print("✅ validate_file tests passed")

def test_detect_file_type():
    """Test detecting file types"""
    print("\nTesting detect_file_type...")
    
    # Create a test text file
    content = "This is a plain text file for testing."
    filepath = create_test_file("detect_text.txt", content)
    
    try:
        # Detect file type
        file_info = detect_file_type(filepath)
        print(f"Text file info: {file_info}")
        assert file_info["file_extension"] == ".txt"
        assert file_info["is_binary"] is False
        assert file_info["encoding"].lower() in ["utf-8", "ascii"]
        
        # Create a test binary file
        binary_content = bytes([0x00, 0x01, 0x02, 0x03, 0xFF, 0xFE, 0xFD, 0xFC])
        binary_filepath = create_test_file("detect_binary.bin", binary_content, mode="wb")
        
        # Detect file type
        file_info = detect_file_type(binary_filepath)
        print(f"Binary file info: {file_info}")
        assert file_info["file_extension"] == ".bin"
        
        # Create a test JSON file
        data = {"name": "Test", "value": 123}
        json_filepath = create_test_file("detect.json", json.dumps(data))
        
        # Detect file type
        file_info = detect_file_type(json_filepath)
        print(f"JSON file info: {file_info}")
        assert file_info["file_extension"] == ".json"
        assert file_info["is_binary"] is False
        
        print("✅ detect_file_type tests passed")
    finally:
        # Clean up
        for file in [filepath, binary_filepath, json_filepath]:
            if os.path.exists(file):
                os.remove(file)

def test_get_file_content():
    """Test getting content from files"""
    print("\nTesting get_file_content...")
    
    # Create a test text file
    content = "This is a plain text file for testing."
    filepath = create_test_file("content_text.txt", content)
    
    try:
        # Get file content
        extracted_content = get_file_content(filepath)
        print(f"Text file content: '{extracted_content}'")
        assert extracted_content == content
        
        # Create a test JSON file
        data = {"name": "Test", "value": 123}
        json_filepath = create_test_file("content.json", json.dumps(data))
        
        # Get file content
        extracted_content = get_file_content(json_filepath)
        print(f"JSON file content: '{extracted_content}'")
        extracted_data = json.loads(extracted_content)
        assert extracted_data["name"] == "Test"
        assert extracted_data["value"] == 123
        
        print("✅ get_file_content tests passed")
    finally:
        # Clean up
        for file in [filepath, json_filepath]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    # Make sure the test data directory exists
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    print("🧪 Testing file_utils.py")
    
    # Run tests
    test_validate_file()
    test_detect_file_type()
    test_get_file_content()
    
    print("\n✅ All tests passed!") 