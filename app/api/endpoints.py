"""
API endpoints for DataPilot
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import shutil
import uuid
import json
import logging

from app.api.models import AskRequest, AskResponse, Dataset
from app.core.database import get_connection, get_session, engine
from app.services.ai_service import generate_sql
from app.services.ingestion import ingest_file
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# LIST DATASETS
# ==================================================
@router.get("/datasets")
def list_datasets():
    with Session(engine) as session:
        datasets = session.exec(select(Dataset)).all()
        results = []
        for ds in datasets:
            try:
                schema = json.loads(ds.schema_info)
            except Exception:
                schema = []
            results.append({
                "id": ds.id,
                "name": ds.filename,
                "table_name": ds.table_name_duckdb,
                "schema": schema,
                "row_count": ds.row_count,
            })
        return results


# ==================================================
# DELETE DATASET
# ==================================================
@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):
    with Session(engine) as session:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")

        # Drop from DuckDB
        try:
            conn = get_connection()
            conn.execute(f"DROP TABLE IF EXISTS {dataset.table_name_duckdb}")
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to drop DuckDB table: {e}")

        session.delete(dataset)
        session.commit()
        return {"message": "Dataset deleted"}


# ==================================================
# UPLOAD (CSV + Excel + Clean columns)
# ==================================================
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    filename = file.filename.lower()

    if not filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "Only CSV or Excel supported")

    file_id = uuid.uuid4().hex[:8]
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    # save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Delegate to ingestion service
    result = ingest_file(file_path, table_name=f"dataset_{file_id}")

    # Persist dataset metadata to SQLite
    with Session(engine) as session:
        ds = Dataset(
            id=result["dataset_id"],
            filename=file.filename,
            table_name_duckdb=result["table_name"],
            schema_info=json.dumps(result["schema"]),
            row_count=result["row_count"],
        )
        session.add(ds)
        session.commit()

    return result


# ==================================================
# ✅ ASK (AI → SQL → DuckDB)
# ==================================================
@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):

    conn = get_connection()

    try:
        # -----------------------
        # Get schema for AI
        # -----------------------
        schema_rows = conn.execute(f"DESCRIBE {request.dataset_id}").fetchall()
        schema = [{"column": r[0], "type": r[1]} for r in schema_rows]

        # -----------------------
        # Get sample data for prompt context
        # -----------------------
        sample_rows = conn.execute(
            f"SELECT * FROM {request.dataset_id} LIMIT 3"
        ).fetchdf().to_dict(orient="records")

        # -----------------------
        # Generate SQL
        # -----------------------
        sql_query = generate_sql(
            question=request.question,
            schema=schema,
            table_name=request.dataset_id,
            sample_data=sample_rows
        )

        # Safety: SELECT only
        if not sql_query.strip().lower().startswith("select"):
            raise HTTPException(400, "Only SELECT queries allowed")

        # -----------------------
        # Execute safely
        # -----------------------
        try:
            df = conn.execute(sql_query).fetchdf()
        except Exception:
            # 🔥 fallback if AI makes bad SQL
            df = conn.execute(
                f"SELECT * FROM {request.dataset_id} LIMIT 5"
            ).fetchdf()

        data = df.to_dict(orient="records")

        return AskResponse(
            answer=f"I found {len(data)} result(s).",
            sql_query=sql_query,
            data=data,
            message="success"
        )

    finally:
        conn.close()
