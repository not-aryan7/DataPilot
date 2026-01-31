"""API endpoints for DataPilot."""
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.models import UploadResponse, AskRequest, AskResponse
from app.services.ingestion import ingest_csv
from app.services.query_service import validate_table_exists, get_table_schema, execute_user_query
from app.services.ai_service import generate_sql, generate_answer

router = APIRouter()

# Directory for uploaded files
UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV file and ingest it into the database.
    
    Returns dataset_id and schema information.
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Save file to disk
    file_id = uuid.uuid4().hex[:8]
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Ingest into DuckDB
    try:
        result = ingest_csv(file_path, table_name=f"dataset_{file_id}")
        return UploadResponse(
            dataset_id=result["dataset_id"],
            table_name=result["table_name"],
            schema=result["schema"],
            row_count=result["row_count"],
            message=f"Successfully uploaded {file.filename}"
        )
    except Exception as e:
        # Clean up file on failure
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a natural language question about a dataset.
    
    Returns generated SQL, query results, and a natural language answer.
    """
    # Validate dataset exists
    if not validate_table_exists(request.dataset_id):
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset '{request.dataset_id}' not found"
        )
    
    # Get schema for context
    schema = get_table_schema(request.dataset_id)
    
    # Generate SQL from question (AI service - stub for now)
    sql_query = generate_sql(
        question=request.question,
        schema=schema,
        table_name=request.dataset_id
    )
    
    # Execute the query
    try:
        data = execute_user_query(sql_query)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {str(e)}"
        )
    
    # Generate answer (AI service - stub for now)
    answer = generate_answer(request.question, data)
    
    return AskResponse(
        answer=answer,
        sql_query=sql_query,
        data=data,
        message="Query executed successfully"
    )
