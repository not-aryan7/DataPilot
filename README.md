# DataPilot

A lightweight, local-first analytics engine that lets you query spreadsheets using plain English.

Upload a CSV or Excel, ask a question, AI generates SQL, DuckDB executes, results show as tables and charts.

**ChatGPT + SQL + DuckDB + Charts** — all running locally. No cloud. No external APIs.

---

## How it works

```
file → pandas → DuckDB table
question → embeddings → FAISS → reranker → prompt + sample data → LLM → SQL
SQL → DuckDB → JSON → table + charts
```

Natural language in. SQL + charts out.

---

## Architecture

```
Frontend (Vite + JS)
        ↓
FastAPI Backend (REST API)
        ↓
RAG SQL Engine (Embeddings + FAISS + Reranker + Ollama LLM)
        ↓
Generated SQL
        ↓
DuckDB execution
        ↓
Tables + Charts
```

---

## Tech Stack

### Backend
- FastAPI
- DuckDB
- Pandas

### AI / ML
- Sentence Transformers (bi-encoder embeddings)
- FAISS (vector similarity search)
- Cross-encoder reranker
- Ollama (local LLM server)
- Qwen2.5-Coder 7B (SQL generation model)
- Retrieval-Augmented Generation (RAG)

### Frontend
- Vite
- Vanilla JavaScript
- Chart.js

---

## Core Feature

### Natural Language → SQL

**Input**
```
average revenue by region
```

**Generated automatically**
```sql
SELECT region, AVG(revenue)
FROM sales
GROUP BY region;
```

Executed instantly inside DuckDB.

---

## Features

- CSV + Excel upload
- automatic schema detection
- column normalization
- safe SQL generation (SELECT only)
- semantic schema retrieval
- sample data injection into prompts for better accuracy
- DuckDB OLAP queries (very fast)
- automatic table rendering
- automatic chart creation
- fully local inference via Ollama
- zero cloud dependencies

---

## Project Structure

```
app/        API + ingestion + endpoints
rag/        embeddings + retriever + SQL generator
frontend/   UI + charts
tests_rag/  model tests
```

---

# Run Locally

## Prerequisites

### Install Ollama

1. Download and install from [ollama.com](https://ollama.com)
2. Pull the model:

```bash
ollama pull qwen2.5-coder:7b
```

Ollama runs as a background service on `http://localhost:11434`. It auto-detects GPU (NVIDIA/AMD) for acceleration.

---

## 1. Clone the repo

```bash
git clone https://github.com/not-aryan7/DataPilot.git
cd DataPilot
```

---

## 2. Backend (FastAPI + DuckDB)

### Create virtual environment
```bash
python -m venv venv
```

### Activate

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Start API
```bash
uvicorn app.main:app --reload
```

Backend → http://127.0.0.1:8000
Docs → http://127.0.0.1:8000/docs

---

## 3. Frontend (Vite)

Open a **new terminal**

```bash
cd frontend
npm install
npm run dev
```

Frontend → http://localhost:5173

---

## 4. Use the app

1. Make sure Ollama is running (it starts automatically after install)
2. Upload CSV or Excel
3. Ask questions in plain English
4. Get SQL + tables + charts instantly

---

## 5. Stop everything

```bash
CTRL + C
deactivate
```

To stop Ollama, quit it from the system tray.

---

## Safety

- SELECT queries only
- no DROP / DELETE / UPDATE
- runs fully offline
- designed for small/medium datasets

---

## Switching Models

Ollama makes it easy to swap models. To use a different model:

```bash
ollama pull mistral
```

Then change the default in `rag/llm.py`:

```python
def __init__(self, model_name: str = "mistral"):
```

Available models that work well for SQL generation:
- `qwen2.5-coder:7b` (default, best for SQL)
- `mistral` (good general purpose)
- `tinyllama` (fastest, less accurate)

---

## Why I built this

To practice building complete end-to-end AI systems that combine:

- backend APIs
- analytical databases
- vector search
- LLM pipelines
- frontend visualization

Everything runs locally for privacy, speed, and zero cost.

---

## Authors

**Ayush Neupane**
**Aryan RajBhandari**

Computer Science + Economics
Building applied AI & data engineering systems
