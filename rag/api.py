from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from .sql_generator import SQLGenerator
from .llm import LocalLLM
from app.core.database import get_connection, execute_query


# -------------------------
# App setup
# -------------------------

app = FastAPI(title="DataPilot AI SQL Service")


# allow frontend (React) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only (ok for now)
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Load LLM ONCE (heavy model)
# -------------------------

_llm_instance = None

def get_llm():
    """Lazy load the LLM once and reuse."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LocalLLM()
    return _llm_instance


# -------------------------
# Request / response models
# -------------------------

class QueryRequest(BaseModel):
    question: str
    table_name: Optional[str] = None
    schema_docs: Optional[List[str]] = None  # Dynamic schema from caller


class QueryResponse(BaseModel):
    sql: str
    data: List[Dict[str, Any]]
    row_count: int
    message: str


# -------------------------
# Route
# -------------------------

@app.post("/generate-sql", response_model=QueryResponse)
def generate_sql_endpoint(req: QueryRequest):
    """Generate SQL from question and execute against DuckDB."""
    try:
        # Use provided schema or fallback to default
        if req.schema_docs and len(req.schema_docs) > 0:
            schema_docs = req.schema_docs
        else:
            # Fallback for testing
            schema_docs = [
                "Table calls(agent_name, talk_time_sec, call_date, csat_score)",
                "Table agents(agent_name, team, supervisor)",
                "Table tickets(ticket_id, agent_name, status, created_at)",
                "Table sales(order_id, region, revenue, date)"
            ]
        
        # Create SQLGenerator with the actual schema (reuse LLM)
        llm = get_llm()
        generator = SQLGenerator(schema_docs=schema_docs, llm_instance=llm)
        
        # 1. Generate SQL
        sql = generator.generate(req.question)
        
        # 2. Execute against DuckDB
        try:
            data = execute_query(sql)
            row_count = len(data)
            message = f"Query executed successfully, returned {row_count} rows"
        except Exception as e:
            # If execution fails, return the SQL with error
            return QueryResponse(
                sql=sql,
                data=[],
                row_count=0,
                message=f"SQL generated but execution failed: {str(e)}"
            )
        
        return QueryResponse(
            sql=sql,
            data=data,
            row_count=row_count,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Health check
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "RAG SQL API running"}

