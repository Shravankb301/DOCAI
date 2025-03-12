import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
host = os.getenv("API_HOST", "0.0.0.0")
# Railway sets PORT environment variable - this should take precedence
port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))

# Determine if we're in production (Railway sets this)
is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"

if __name__ == "__main__":
    print(f"Starting AI Compliance Checker API on {host}:{port}")
    print(f"Environment: {'Production' if is_production else 'Development'}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=not is_production  # Only enable reload in development
    ) 