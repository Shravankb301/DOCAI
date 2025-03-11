import os
import io
import json
from app.utils.file_utils import detect_file_type, get_file_content

def create_test_file(filename, content, mode="w"):
    """Helper function to create a test file"""
    with open(filename, mode) as f:
        f.write(content)
    return filename

def test_detect_file_type():
    """Test detecting file types"""
    # Create a test text file
    text_file = create_test_file("test_text.txt", "This is a plain text file for testing.")
    
    try:
        # Detect file type
        file_info = detect_file_type(text_file)
        print(f"Text file info: {file_info}")
        
        # Create a test binary file
        binary_file = create_test_file("test_binary.bin", bytes([0x00, 0x01, 0x02, 0x03, 0xFF, 0xFE, 0xFD, 0xFC]), mode="wb")
        
        # Detect file type
        file_info = detect_file_type(binary_file)
        print(f"Binary file info: {file_info}")
        
        # Create a test JSON file
        data = {"name": "Test", "value": 123}
        json_file = create_test_file("test.json", json.dumps(data))
        
        # Detect file type
        file_info = detect_file_type(json_file)
        print(f"JSON file info: {file_info}")
        
    finally:
        # Clean up
        for file in [text_file, binary_file, json_file]:
            if os.path.exists(file):
                os.remove(file)

def test_get_file_content():
    """Test getting content from files"""
    # Create a test text file
    text_file = create_test_file("test_text.txt", "This is a plain text file for testing.")
    
    try:
        # Get file content
        content = get_file_content(text_file)
        print(f"Text file content: {content}")
        
        # Create a test JSON file
        data = {"name": "Test", "value": 123}
        json_file = create_test_file("test.json", json.dumps(data))
        
        # Get file content
        content = get_file_content(json_file)
        print(f"JSON file content: {content}")
        
    finally:
        # Clean up
        for file in [text_file, json_file]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    print("Testing detect_file_type...")
    test_detect_file_type()
    
    print("\nTesting get_file_content...")
    test_get_file_content() 