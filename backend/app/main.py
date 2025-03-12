from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Compliance Checker",
    description="An AI-enabled system for checking document compliance",
    version="1.0.0"
)

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") or [
    "http://localhost:3000",  # Local development
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.endpoints import documents

app.include_router(documents.router, prefix="/api", tags=["documents"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Compliance Checker API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port) 