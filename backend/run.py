import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
host = os.getenv("API_HOST", "0.0.0.0")
port = int(os.getenv("API_PORT", "8000"))

if __name__ == "__main__":
    print(f"Starting AI Compliance Checker API on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True) 