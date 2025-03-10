from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Body
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Optional, List, Dict, Any
import aiofiles
from app.models.compliance import analyze_document
from app.utils.database import store_analysis_result
from app.utils.file_utils import validate_file, get_file_content
import json
import glob
import re

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# UUID validation pattern
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID.
    """
    return bool(UUID_PATTERN.match(uuid_string))

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
):
    """
    Upload a document file or text content for compliance analysis.
    """
    if not file and not text_content:
        raise HTTPException(status_code=400, detail="Either file or text content must be provided")
    
    # Process file upload
    if file:
        # Validate file
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type or size")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Read file content for analysis using the appropriate method based on file type
        content_to_analyze = get_file_content(file_path)
        
        # Check if file is empty
        if not content_to_analyze.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be read. Please upload a valid file with content.")
    else:
        # Use provided text content
        content_to_analyze = text_content
        file_path = None
        
        # Check if text content is empty
        if not content_to_analyze.strip():
            raise HTTPException(status_code=400, detail="Text content is empty. Please provide some text to analyze.")
    
    # Generate a document ID
    document_id = str(uuid.uuid4())
    
    # Process the document in the background
    background_tasks.add_task(
        process_document,
        content_to_analyze,
        file_path,
        document_id
    )
    
    return JSONResponse(
        status_code=202,
        content={
            "message": "Document received and being processed",
            "document_id": document_id
        }
    )

@router.get("/status/{document_id}")
async def get_analysis_status(document_id: str):
    """
    Get the status of a document analysis.
    """
    try:
        # Validate document_id format
        if not is_valid_uuid(document_id):
            raise HTTPException(status_code=400, detail="Invalid document ID format")
            
        # Check if the document exists in the local_db directory
        local_db_path = os.path.join("local_db", f"{document_id}.json")
        
        if os.path.exists(local_db_path):
            # Read the analysis result from the local file
            with open(local_db_path, 'r') as f:
                analysis_result = json.load(f)
            
            return {
                "status": "completed",
                "result": analysis_result
            }
        
        # If using Supabase, you would query the database here
        # Example:
        # if supabase:
        #     response = supabase.table("risks").select("*").eq("id", document_id).execute()
        #     if response.data and len(response.data) > 0:
        #         return {
        #             "status": "completed",
        #             "result": response.data[0]
        #         }
        
        # If not found, return pending status
        return {"status": "pending"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis status: {str(e)}")

@router.get("/history")
async def get_analysis_history():
    """
    Get the history of document analyses.
    """
    try:
        # Check for documents in the local_db directory
        history = []
        local_db_path = "local_db"
        
        if os.path.exists(local_db_path):
            # Get all JSON files in the local_db directory
            json_files = glob.glob(os.path.join(local_db_path, "*.json"))
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r') as f:
                        analysis_result = json.load(f)
                    
                    # Add to history list with basic information
                    history.append({
                        "id": analysis_result.get("id"),
                        "status": analysis_result.get("status"),
                        "file_path": analysis_result.get("file_path"),
                        "created_at": analysis_result.get("created_at")
                    })
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
            
            # Sort by created_at in descending order (newest first)
            history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # If using Supabase, you would query the database here
        # Example:
        # if supabase:
        #     response = supabase.table("risks").select("id,status,file_path,created_at").order("created_at", desc=True).execute()
        #     if response.data:
        #         history = response.data
        
        return {"history": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis history: {str(e)}")

@router.post("/batch")
async def batch_upload(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple documents for batch compliance analysis.
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
    
    batch_results = []
    
    for file in files:
        # Validate file
        if not validate_file(file):
            batch_results.append({
                "filename": file.filename,
                "status": "error",
                "error": "Invalid file type or size"
            })
            continue
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Generate a document ID
            document_id = str(uuid.uuid4())
            
            # Process the document in the background
            background_tasks.add_task(
                process_document,
                get_file_content(file_path),
                file_path,
                document_id
            )
            
            batch_results.append({
                "filename": file.filename,
                "document_id": document_id,
                "status": "processing"
            })
            
        except Exception as e:
            batch_results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return JSONResponse(
        status_code=202,
        content={
            "message": f"Batch processing started for {len(files)} documents",
            "results": batch_results
        }
    )

async def process_document(content: str, file_path: Optional[str], document_id: str):
    """
    Process the document content and store results.
    """
    try:
        # Analyze document for compliance
        analysis_result = analyze_document(content)
        
        # Store results in database
        await store_analysis_result(
            id=document_id,
            file_path=file_path,
            status=analysis_result["status"],
            details=analysis_result
        )
        
        return document_id
    except Exception as e:
        # Log error
        print(f"Error processing document: {str(e)}")
        # Could implement error notification here 

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its analysis results.
    """
    try:
        # Validate document_id format
        if not is_valid_uuid(document_id):
            raise HTTPException(status_code=400, detail="Invalid document ID format")
        
        # Check if the document exists in the local_db directory
        local_db_path = os.path.join("local_db", f"{document_id}.json")
        
        if not os.path.exists(local_db_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Read the document data to get the file path
        with open(local_db_path, 'r') as f:
            document_data = json.load(f)
        
        # Delete the document file if it exists
        file_path = document_data.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the document record
        os.remove(local_db_path)
        
        return {"message": "Document deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.delete("/bulk")
async def bulk_delete_documents(document_ids: List[str] = Body(...)):
    """
    Delete multiple documents and their analysis results.
    """
    if not document_ids:
        raise HTTPException(status_code=400, detail="No document IDs provided")
    
    if len(document_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 documents can be deleted at once")
    
    results = []
    
    for document_id in document_ids:
        try:
            # Validate document_id format
            if not is_valid_uuid(document_id):
                results.append({
                    "document_id": document_id,
                    "status": "error",
                    "message": "Invalid document ID format"
                })
                continue
            
            # Check if the document exists in the local_db directory
            local_db_path = os.path.join("local_db", f"{document_id}.json")
            
            if not os.path.exists(local_db_path):
                results.append({
                    "document_id": document_id,
                    "status": "error",
                    "message": "Document not found"
                })
                continue
            
            # Read the document data to get the file path
            with open(local_db_path, 'r') as f:
                document_data = json.load(f)
            
            # Delete the document file if it exists
            file_path = document_data.get("file_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete the document record
            os.remove(local_db_path)
            
            results.append({
                "document_id": document_id,
                "status": "success",
                "message": "Document deleted successfully"
            })
            
        except Exception as e:
            results.append({
                "document_id": document_id,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}

@router.get("/search")
async def search_documents(
    query: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Search for documents by content or status.
    """
    try:
        # Check for documents in the local_db directory
        results = []
        local_db_path = "local_db"
        
        if not os.path.exists(local_db_path):
            return {"results": [], "total": 0}
        
        # Get all JSON files in the local_db directory
        json_files = glob.glob(os.path.join(local_db_path, "*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    document = json.load(f)
                
                # Filter by status if provided
                if status and document.get("status") != status:
                    continue
                
                # Filter by query if provided
                if query:
                    # Check if query is in the document content
                    # This is a simple implementation - in a real system, you would use a proper search index
                    file_path = document.get("file_path")
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if query.lower() not in content.lower():
                            # Also check in the findings
                            findings = document.get("details", {}).get("key_findings", [])
                            found_in_findings = False
                            
                            for finding in findings:
                                if query.lower() in finding.get("finding", "").lower() or query.lower() in finding.get("context", "").lower():
                                    found_in_findings = True
                                    break
                            
                            if not found_in_findings:
                                continue
                
                # Add to results
                results.append({
                    "id": document.get("id"),
                    "status": document.get("status"),
                    "file_path": document.get("file_path"),
                    "created_at": document.get("created_at"),
                    "confidence": document.get("details", {}).get("confidence")
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
        
        # Sort by created_at in descending order (newest first)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        total = len(results)
        results = results[offset:offset + limit]
        
        return {
            "results": results,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}") 