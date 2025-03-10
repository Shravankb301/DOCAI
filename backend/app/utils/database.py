import os
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Warning: Supabase credentials not found in environment variables")
    supabase = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        supabase = None

async def store_analysis_result(
    id: str,
    file_path: Optional[str],
    status: str,
    details: Dict[str, Any]
) -> str:
    """
    Store document analysis result in the database.
    
    Args:
        id: Unique identifier for the document
        file_path: Path to the analyzed file (if any)
        status: Compliance status ("compliant", "non-compliant", or "error")
        details: Detailed analysis results
        
    Returns:
        str: ID of the created record
    """
    if not supabase:
        # Fallback to local storage if Supabase is not available
        print("Supabase not available, storing result locally")
        
        # Store in a local file as JSON
        import json
        os.makedirs("local_db", exist_ok=True)
        with open(f"local_db/{id}.json", "w") as f:
            json.dump({
                "id": id,
                "file_path": file_path,
                "status": status,
                "details": details,
                "created_at": import_datetime().now().isoformat()
            }, f)
        
        return id
    
    try:
        # Insert record into Supabase
        response = supabase.table("risks").insert({
            "id": id,
            "file_path": file_path,
            "status": status,
            "details": details
        }).execute()
        
        # Extract the ID from the response
        data = response.data
        if data and len(data) > 0:
            return data[0]["id"]
        else:
            raise Exception("No ID returned from database insert")
    
    except Exception as e:
        print(f"Error storing analysis result: {str(e)}")
        # Fallback to local storage
        return await store_analysis_result_locally(id, file_path, status, details)

async def store_analysis_result_locally(
    id: str,
    file_path: Optional[str],
    status: str,
    details: Dict[str, Any]
) -> str:
    """
    Fallback function to store results locally if database is unavailable.
    """
    import json
    from datetime import datetime
    
    os.makedirs("local_db", exist_ok=True)
    with open(f"local_db/{id}.json", "w") as f:
        json.dump({
            "id": id,
            "file_path": file_path,
            "status": status,
            "details": details,
            "created_at": datetime.now().isoformat()
        }, f)
    
    return id

def import_datetime():
    """Helper function to import datetime module"""
    from datetime import datetime
    return datetime 