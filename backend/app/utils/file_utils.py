from fastapi import UploadFile
import os
from typing import List, Set
import importlib.util

# Define allowed file extensions
ALLOWED_EXTENSIONS: Set[str] = {
    '.txt', '.pdf', '.doc', '.docx', '.rtf', '.md'
}

# Maximum file size (10 MB)
MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB in bytes

# Check if PyPDF2 is available
PYPDF2_AVAILABLE = importlib.util.find_spec("PyPDF2") is not None

def validate_file(file: UploadFile) -> bool:
    """
    Validate if the uploaded file meets the requirements.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    # Check file extension
    _, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        return False
    
    # Check file size (this requires reading the file)
    # Note: This approach loads the file into memory, which may not be ideal for very large files
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        return False
    
    return True

def get_file_content(file_path: str) -> str:
    """
    Extract text content from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Text content of the file
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    try:
        # Handle PDF files
        if file_extension == '.pdf' and PYPDF2_AVAILABLE:
            return extract_text_from_pdf(file_path)
        # Handle plain text files
        elif file_extension in ['.txt', '.md', '.rtf']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        # Handle other file types (placeholder for future implementation)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text
    except ImportError:
        print("PyPDF2 is not installed. Cannot extract text from PDF.")
        return ""
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return "" 