from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from models.regulatory_agents_new import RegulatorySearchAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Regulatory Search API",
    description="API for searching and analyzing regulatory information",
    version="1.0.0"
)

# Initialize the regulatory search agent
agent = RegulatorySearchAgent()

class SearchRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """
    Search for regulatory information.
    
    Args:
        request: SearchRequest containing the query
        
    Returns:
        Dict containing search results and analysis
    """
    try:
        logger.info(f"Received search request: {request.query}")
        
        # Perform the search
        results = agent.search(request.query)
        
        # Check for errors
        if results.get("error", False):
            error_message = results.get("error_message", "Unknown error occurred")
            logger.error(f"Search error: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)
            
        logger.info(f"Search completed successfully. Found {len(results.get('sources', []))} sources.")
        return results
        
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Regulatory Search API",
        "version": "1.0.0",
        "description": "API for searching and analyzing regulatory information",
        "endpoints": {
            "/health": "Health check endpoint",
            "/search": "Search for regulatory information (POST)",
            "/": "This information"
        }
    } 