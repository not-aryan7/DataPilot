"""
API endpoints for DataPilot
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import shutil
import uuid

from app.api.models import AskRequest, AskResponse
from app.core.database import get_connection
from app.services.ai_service import generate_sql
from app.services.ingestion import ingest_file  # ✅ IMPORTANT


router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# ✅ UPLOAD (CSV + Excel + Clean columns)
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

    # 🔥 Delegate to ingestion service
    result = ingest_file(file_path, table_name=f"dataset_{file_id}")

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
