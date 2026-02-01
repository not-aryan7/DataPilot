"""API endpoints for DataPilot."""
import shutil
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select

from app.api.models import UploadResponse, AskRequest, AskResponse, Dataset, QueryHistory
from app.core.database import get_session
from app.services.ingestion import ingest_csv
from app.services.query_service import validate_table_exists, get_table_schema, execute_user_query
from app.services.ai_service import generate_sql, generate_answer

router = APIRouter()

# Directory for uploaded files
UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload a CSV file, ingest it into DuckDB, and save record to SQLite.
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
        
        # Save to SQLite
        dataset = Dataset(
            id=result["dataset_id"],
            filename=file.filename,
            table_name_duckdb=result["table_name"],
            schema_info=json.dumps(result["schema"]),
            row_count=result["row_count"]
        )
        session.add(dataset)
        session.commit()
        session.refresh(dataset)
        
        return UploadResponse(
            dataset_id=dataset.id,
            table_name=dataset.table_name_duckdb,
            schema=result["schema"],
            row_count=dataset.row_count,
            message=f"Successfully uploaded {file.filename}"
        )
    except Exception as e:
        # Clean up file on failure
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    session: Session = Depends(get_session)
):
    """
    Ask a natural language question about a dataset.
    """
    # Validate dataset exists
    if not validate_table_exists(request.dataset_id):
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset '{request.dataset_id}' not found"
        )
    
    # Get schema for context
    schema = get_table_schema(request.dataset_id)
    
    # Generate SQL from question (AI service)
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
    
    # Generate answer (AI service)
    answer = generate_answer(request.question, data)
    
    # Save query history
    try:
        query_history = QueryHistory(
            dataset_id=request.dataset_id,
            question=request.question,
            sql_query=sql_query,
            answer=answer
        )
        session.add(query_history)
        session.commit()
    except Exception as e:
        # Don't fail the request if history save fails, just log it
        print(f"Failed to save query history: {e}")
    
    return AskResponse(
        answer=answer,
        sql_query=sql_query,
        data=data,
        message="Query executed successfully"
    )

@router.get("/datasets")
async def get_datasets(session: Session = Depends(get_session)):
    """List all uploaded datasets."""
    datasets = session.exec(select(Dataset)).all()
    # Parse schema_info JSON back to list/dict for frontend if needed, 
    # but for now returning as is or we can use a Pydantic model to handle it.
    # The frontend expects 'schema' in the dataset object for some operations,
    # but primarily just needs id, name, etc.
    # Let's clean up the response to match what frontend expects.
    response = []
    for d in datasets:
        response.append({
            "id": d.id,
            "name": d.filename,
            "table_name": d.table_name_duckdb,
            "schema": json.loads(d.schema_info),
            "row_count": d.row_count,
            "created_at": d.created_at
        })
    return response

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str, session: Session = Depends(get_session)):
    """Delete a dataset by ID."""
    from app.core.database import get_connection
    
    # Find and delete from SQLite
    dataset = session.exec(select(Dataset).where(Dataset.id == dataset_id)).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    table_name = dataset.table_name_duckdb
    
    # Delete from SQLite
    session.delete(dataset)
    session.commit()
    
    # Try to drop table from DuckDB
    try:
        conn = get_connection()
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.close()
    except Exception as e:
        # Log but don't fail - SQLite record is already deleted
        print(f"Warning: Could not drop DuckDB table {table_name}: {e}")
    
    return {"message": f"Dataset {dataset_id} deleted successfully"}

