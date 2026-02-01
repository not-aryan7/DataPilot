from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .sql_generator import SQLGenerator


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
# Load AI pipeline ONCE
# -------------------------

schema_docs = [
    "Table calls(agent_name, talk_time_sec, call_date, csat_score)",
    "Table agents(agent_name, team, supervisor)",
    "Table tickets(ticket_id, agent_name, status, created_at)",
    "Table sales(order_id, region, revenue, date)"
]

generator = SQLGenerator(schema_docs)


# -------------------------
# Request / response models
# -------------------------

class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql: str


# -------------------------
# Route
# -------------------------

@app.post("/generate-sql", response_model=QueryResponse)
def generate_sql(req: QueryRequest):
    sql = generator.generate(req.question)
    return {"sql": sql}


# -------------------------
# Health check
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "RAG SQL API running"}
