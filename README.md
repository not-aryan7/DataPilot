🚀 DataPilot

DataPilot is a lightweight, local-first analytics tool that lets you query spreadsheets using plain English.

Upload a CSV or Excel file → ask a question → AI generates SQL → DuckDB executes it → results are returned as tables and charts.

It combines LLMs + vector search + databases + APIs + frontend into one complete end-to-end system.

Think:

ChatGPT + SQL + Power BI — but fully local and private.

✨ Demo Queries

Try asking:

total revenue by year

sum of sales by region

average price per product

top 5 rows

group by month

average talk time per agent

🧠 System Architecture
Frontend (Vite + JS)
        ↓
FastAPI Backend (REST API)
        ↓
RAG SQL Engine (Embeddings + FAISS + Reranker + LLM)
        ↓
Generated SQL
        ↓
DuckDB execution
        ↓
Tables + Charts

🧩 Tech Stack
Backend

FastAPI

DuckDB

Pandas

FAISS

Sentence Transformers

Cross-Encoder reranker

Local LLM (TinyLlama / Mistral)

Frontend

Vite

Vanilla JavaScript

Chart.js

AI / ML

Bi-encoder embeddings

Vector similarity search

Cross-encoder reranking

Prompt engineering

Local inference (no cloud APIs)

🔥 Core Feature
Natural Language → SQL

Example:

Input

average revenue by region last year


Generated SQL

SELECT region, AVG(revenue)
FROM sales
GROUP BY region;


Executed automatically → results returned instantly.

🧠 Backend / AI Engine (Built From Scratch)

The backend contains a custom Retrieval-Augmented Generation (RAG) pipeline designed specifically for accurate SQL generation.

Retrieval Pipeline
User question
    ↓
Embed query
    ↓
FAISS similarity search
    ↓
Cross-encoder reranking
    ↓
Inject schema into prompt
    ↓
Local LLM generates SQL
    ↓
DuckDB executes query

Components
1️⃣ Embeddings (embed.py)

SentenceTransformer bi-encoder

normalized vectors

fast semantic similarity

converts schema text → vectors

2️⃣ Vector Index (index.py)

FAISS IndexFlatIP

cosine similarity search

millisecond retrieval

scalable to thousands of tables

3️⃣ Reranker (reranker.py)

cross-encoder/ms-marco model

reranks top candidates

improves precision

reduces irrelevant tables

4️⃣ Prompt Builder (prompt.py)

injects only relevant schema

prevents hallucinated tables/columns

forces valid SQL only

deterministic outputs

5️⃣ Local LLM (llm.py)

TinyLlama / Mistral

runs fully offline

no API cost

deterministic generation

strips explanations/markdown

6️⃣ SQL Generator (sql_generator.py)

High-level orchestrator:

Retriever → Prompt → LLM → SQL


Single call:

sql = generator.generate(question)

7️⃣ API Layer (api.py)

FastAPI service exposes:

Endpoints
GET  /
POST /generate

Request
{
  "question": "average talk time per agent"
}

Response
{
  "sql": "SELECT agent_name, AVG(talk_time_sec) FROM calls GROUP BY agent_name;"
}


Frontend simply calls this endpoint.

✨ Features

✅ CSV + Excel upload
✅ automatic schema detection
✅ column normalization
✅ natural language → SQL
✅ semantic schema retrieval
✅ safe SELECT-only execution
✅ fast DuckDB queries
✅ tables + charts
✅ fully local inference
✅ no cloud dependencies

💡 Why These Choices
FastAPI

simple REST APIs

async

auto docs

lightweight

DuckDB

embedded analytics database

no server needed

extremely fast aggregations

perfect for local OLAP

FAISS

production-grade vector search

very fast similarity matching

RAG approach

reduces hallucinations

improves SQL accuracy

scales to large schemas

Local LLM

privacy friendly

works offline

zero cost

reproducible

🧠 What I Learned Building This

This project was focused heavily on backend + AI engineering:

designing REST APIs

building Retrieval-Augmented Generation systems

embeddings + vector search

FAISS indexing

cross-encoder reranking

prompt engineering

LLM inference optimization

SQL safety constraints

working with analytical databases

connecting backend + frontend cleanly

building complete end-to-end AI products

📂 Project Structure
rag/
 ├── embed.py
 ├── index.py
 ├── reranker.py
 ├── retriever.py
 ├── prompt.py
 ├── llm.py
 ├── sql_generator.py
 ├── api.py
 └── requirements.txt

frontend/
 ├── vite app
 └── charts + UI

tests_rag/
 ├── test_embed.py
 ├── test_index.py
 ├── test_retriever.py
 ├── test_llm.py
 └── test_sqlgenerator.py

⚙️ Run Locally
Backend
python -m venv venv
venv\Scripts\activate
pip install -r rag/requirements.txt
uvicorn rag.api:app --reload


Server:

http://127.0.0.1:8000

Frontend
cd frontend
npm install
npm run dev

🛡️ Safety Notes

SELECT queries only

no DROP/DELETE/UPDATE

local only

designed for small/medium datasets

not production hardened

🚀 Future Improvements

streaming responses

query caching

better SQL validation

fine-tuned SQL model

schema auto-refresh

Docker deployment

multi-table joins optimization

larger cross-encoder

quantized LLM for faster CPU inference

👨‍💻 Author

Built as a full-stack + AI engineering learning project combining:

Data Engineering

LLM Systems

APIs

Databases

Frontend Integration
